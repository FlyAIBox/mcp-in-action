import json
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Any, List
from contextlib import AsyncExitStack
import asyncio

import client_chunk as chunk
from client_config import *
import sys

class MCPClient:
    """
    A client class for interacting with the MCP (Model Control Protocol) server.
    This class manages the connection and communication with the SQLite database through MCP.
    
    MCP客户端类，用于与MCP(模型控制协议)服务器交互。
    该类管理与SQLite数据库通过MCP的连接和通信。
    """

    def __init__(self, host: str):
        """
        Initialize the MCP client with server parameters
        
        使用服务器参数初始化MCP客户端
        """
        self.host = host  # MCP服务器主机地址
        self.exit_stack = AsyncExitStack()  # 异步上下文管理器栈，用于管理异步资源
        self.session = None  # MCP会话对象
        self._client = None  # MCP客户端对象

    async def __aenter__(self):
        """
        Async context manager entry
        
        异步上下文管理器入口，进入时自动连接服务器
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit
        
        异步上下文管理器出口，退出时自动关闭连接
        """
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        """
        Establishes connection to MCP server with retry mechanism
        
        建立与MCP服务器的连接，包含重试机制
        """
        max_retries = 5
        base_delay = 2  # seconds
        max_delay = 32  # maximum delay in seconds
        
        for attempt in range(max_retries):
            try:
                print(f"Attempting to connect to MCP server (attempt {attempt + 1}/{max_retries})...")
                self._client = sse_client(self.host, timeout=10)  # 创建SSE客户端，设置超时时间为10秒
                # 使用异步上下文管理器栈(exit_stack)进入SSE客户端的异步上下文
                stdio_transport = await self.exit_stack.enter_async_context(self._client)  # 进入异步上下文并获取传输对象
                read, write = stdio_transport  # 解包获取读写通道
                
                # Add a delay to ensure server initialization is complete
                await asyncio.sleep(2)
                
                self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))  # 创建并进入客户端会话
                
                # Test the connection by listing tools
                await self.get_available_tools()
                print(f"Successfully connected to MCP server on attempt {attempt + 1}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"Connection attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Failed to connect after {max_retries} attempts: {e}")
                    raise

    async def get_available_tools(self) -> List[Any]:
        """
        Retrieve a list of available tools from the MCP server.
        
        从MCP服务器获取可用工具列表
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")  # 如果会话未建立，抛出运行时错误

        tools = await self.session.list_tools()  # 异步获取工具列表
        return tools.tools  # 返回可用工具

    def call_tool(self, tool_name: str, args) -> Any:
        """
        Create a callable function for a specific tool.
        This allows us to execute database operations through the MCP server.

        Args:
            tool_name: The name of the tool to create a callable for

        Returns:
            A callable async function that executes the specified tool
            
        创建特定工具的可调用函数。
        这允许我们通过MCP服务器执行数据库操作。

        参数:
            tool_name: 要创建可调用函数的工具名称

        返回:
            执行指定工具的异步可调用函数
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")  # 如果会话未建立，抛出运行时错误

        return self.session.call_tool(tool_name, args)  # 调用指定工具并传递参数


async def agent_loop(mcp_client, query: str, tools, messages: List[dict] = None):
    """
    Main interaction loop that processes user queries using the LLM and available tools.

    This function:
    1. Sends the user query to the LLM with context about available tools
    2. Processes the LLM's response, including any tool calls
    3. Returns the final response to the user

    Args:
        query: User's input question or command
        tools: Dictionary of available database tools and their schemas
        messages: List of messages to pass to the LLM, defaults to None
        
    主要交互循环，使用LLM和可用工具处理用户查询。

    此函数:
    1. 将用户查询发送给LLM，并提供可用工具的上下文
    2. 处理LLM的响应，包括任何工具调用
    3. 向用户返回最终响应

    参数:
        query: 用户的输入问题或命令
        tools: 可用数据库工具及其模式的字典
        messages: 传递给LLM的消息列表，默认为None
    """
    # 将工具列表转换为LLM可用的格式
    available_tools = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    } for tool in tools]

    # 创建消息列表，包含用户查询
    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    # 使用系统提示、用户查询和可用工具查询LLM
    response = await llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=available_tools
    )

    final_text = []  # 用于存储最终文本响应
    message = response.choices[0].message  # 获取LLM响应的第一个选项
    final_text.append(message.content or "")  # 添加LLM响应内容到最终文本

    # 当LLM响应包含工具调用时，处理工具调用
    while message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name  # 获取工具名称
            tool_args = json.loads(tool_call.function.arguments)  # 解析工具参数

            # 调用指定工具并获取结果
            result = await mcp_client.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")  # 记录工具调用信息

            # 将工具调用添加到消息历史中
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }
                ]
            })

            # 将工具调用结果添加到消息历史中
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result.content)
            })

        # 再次查询LLM，包含工具调用结果
        response = await llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=available_tools
        )

        message = response.choices[0].message  # 获取LLM的新响应
        if message.content:
            final_text.append(message.content)  # 将新响应添加到最终文本

    return "\n".join(final_text)  # 将所有文本拼接并返回


async def import_knowledge(path):
    """
    导入知识库文件，将文本内容分块并存储到数据库中
    
    参数:
        path: 知识库文件路径
    """
    # 读取知识文本内容
    try:
        with open(path, 'r', encoding='utf-8') as f:
            knowledge_text = f.read()
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return

    # 将文本切分成每块不超过2000字符的块
    chunks = chunk.to_chunks(knowledge_text, 2000)
    
    # 创建并连接MCP客户端
    print(f"Connecting to MCP server at {MCP_SERVER_HOST}")
    
    try:
        async with MCPClient(MCP_SERVER_HOST) as mcp_client:
            # 尝试访问服务器，确保连接正常
            try:
                # 获取可用数据库工具并为LLM准备它们
                tools = await mcp_client.get_available_tools()
                if not tools:
                    print("Warning: No tools available from the server")
            except Exception as e:
                print(f"Error communicating with MCP server: {e}")
                return

            print('Total Chunks: %d' % len(chunks))  # 打印块总数
            i = 0
            # 处理每一个文本块
            for c in chunks:
                print('Processing chunk %d.' % i)  # 打印当前处理的块序号
                i = i + 1
                try:
                    # 根据模板构建分析内容的提示
                    query = analysis_content_prompt_template % c
                    # 调用agent_loop处理分析任务
                    response = await agent_loop(mcp_client, query, tools)
                    try:
                        # 尝试将响应解析为JSON
                        j = json.loads(response)
                    except Exception as e:
                        print(f"Error parsing response: {e}")
                        print(f"Response: {response}")
                        continue

                    # 处理解析出的文本块，存储到知识库
                    for kc in j.get('Chunks', []):
                        try:
                            # 根据模板构建存储知识的提示
                            q = store_knowledge_prompt_template % kc
                            # 调用agent_loop处理存储任务
                            response = await agent_loop(mcp_client, q, tools)
                            print(response)  # 打印存储结果
                        except Exception as e:
                            print(f"Error storing chunk: {e}")

                    # 处理解析出的FAQ对，存储到FAQ库
                    for faq in j.get('FAQs', []):
                        try:
                            q = store_faq_prompt_template % (faq.get('Question', ''), faq.get('Answer', ''))
                            response = await agent_loop(mcp_client, q, tools)
                            print(response)
                        except Exception as e:
                            print(f"Error storing FAQ: {e}")
                except Exception as e:
                    print(f"Error processing chunk {i}: {e}")
    except Exception as e:
        print(f"Connection error: {e}")

async def search_knowledge(query):
    """
    搜索知识库中的内容
    
    参数:
        query: 搜索查询
    """
    # 根据模板构建搜索提示
    query = search_prompt_template % query
    # 创建并连接MCP客户端
    async with MCPClient(MCP_SERVER_HOST) as mcp_client:
        # 获取可用数据库工具并为LLM准备它们
        tools = await mcp_client.get_available_tools()
        # 调用agent_loop处理搜索任务
        response = await agent_loop(mcp_client, query, tools)
        print(response)  # 打印搜索结果

async def chat(query):
    """
    基于知识库的智能问答
    
    参数:
        query: 用户问题
    """
    # 根据模板构建聊天提示
    query = chat_prompt_template % query
    # 创建并连接MCP客户端
    async with MCPClient(MCP_SERVER_HOST) as mcp_client:
        # 获取可用数据库工具并为LLM准备它们
        tools = await mcp_client.get_available_tools()
        # 调用agent_loop处理聊天任务
        response = await agent_loop(mcp_client, query, tools)
        print(response)  # 打印聊天响应

async def main():
    """
    主函数，处理命令行参数并执行相应操作
    """
    # 读取sys.argv中的参数，如果参数数量少于2则返回错误
    if len(sys.argv) != 3:
        print("Usage: python knowledge_manager.py import/search/chat <args>")
        return

    command = sys.argv[1]  # 获取命令（import/search/chat）
    args = sys.argv[2]  # 获取命令参数

    # 根据命令执行相应操作
    if command == 'import':
        await import_knowledge(args)  # 导入知识
    elif command == 'search':
        await search_knowledge(args)  # 搜索知识
    elif command == 'chat':
        await chat(args)  # 基于知识库聊天
    else:
        # 命令无效，打印使用说明
        print("Usage: python knowledge_manager.py import/search/chat <args>")
        return

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())