from mcp.server import FastMCP
from typing import Any, Dict, List
from loguru import logger
from app.services.milvus_service import MilvusService
from app.models.models import KnowledgeContent, FAQContent
from app.dependencies import get_milvus_service_dependency
import asyncio

class MilvusMCPServer(FastMCP):
    """MCP server implementation for Milvus vector database."""
    
    def __init__(self):
        super().__init__()
        self.milvus_service = get_milvus_service_dependency()
        self.is_ready = False
        
        # Register tools - Call directly in __init__ after service initialization
        tool_configs = [
            {
                "name": "storeKnowledge",
                "fn": self.store_knowledge,
                "description": "Store document into knowledge store for later retrieval.",
            },
            {
                "name": "searchKnowledge",
                "fn": self.search_knowledge,
                "description": "Search for similar documents on natural language descriptions from knowledge store.",
            },
            {
                "name": "storeFAQ",
                "fn": self.store_faq,
                "description": "Store document into FAQ store for later retrieval.",
            },
            {
                "name": "searchFAQ",
                "fn": self.search_faq,
                "description": "Search for similar documents on natural language descriptions from FAQ store.",
            }
        ]
        
        # Register each tool directly with the server
        for config in tool_configs:
            self.add_tool(
                fn=config["fn"],
                name=config["name"],
                description=config["description"]
            )
            logger.info(f"Registered tool: {config['name']}")
            
        # Set server as ready after tools are registered
        self.is_ready = True
        
    def run(self, transport='sse'):
        """Override run method to add startup event handling"""
        # Log startup event directly
        logger.info("MCP Server startup event")
        
        # Ensure all tools are registered and services are ready
        if not self.is_ready:
            logger.warning("Server not ready - waiting for initialization")
            asyncio.get_event_loop().run_until_complete(self.ready_for_connections())
            
        logger.info("MCP Server is ready for connections")
        
        # Call parent run method
        super().run(transport=transport)
        
    async def ready_for_connections(self):
        """Check if server is ready to accept connections"""
        # If not ready, wait for a bit
        if not self.is_ready:
            logger.warning("Server not ready yet - waiting")
            for _ in range(5):  # Try 5 times with 1s intervals
                await asyncio.sleep(1)
                if self.is_ready:
                    break
        return self.is_ready
            
    async def store_knowledge(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store knowledge content in Milvus."""
        # Ensure server is ready before processing
        await self.ready_for_connections()
        
        try:
            knowledge_content = KnowledgeContent(
                content=content,
                metadata=metadata or {}
            )
            self.milvus_service.store_knowledge(knowledge_content)
            return {"status": "success", "message": "Knowledge stored successfully"}
        except Exception as e:
            logger.error(f"Error storing knowledge: {e}")
            return {"status": "error", "message": str(e)}
            
    async def search_knowledge(self, query: str, size: int = 5) -> Dict[str, Any]:
        """Search knowledge content in Milvus."""
        # Ensure server is ready before processing
        await self.ready_for_connections()
        
        try:
            results = self.milvus_service.search_knowledge(query, size)
            return {
                "status": "success",
                "results": [result.dict() for result in results]
            }
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {"status": "error", "message": str(e)}
            
    async def store_faq(self, question: str, answer: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store FAQ content in Milvus."""
        # Ensure server is ready before processing
        await self.ready_for_connections()
        
        try:
            content = FAQContent(
                question=question,
                answer=answer,
                metadata=metadata or {}
            )
            self.milvus_service.store_faq(content)
            return {"status": "success", "message": "FAQ stored successfully"}
        except Exception as e:
            logger.error(f"Error storing FAQ: {e}")
            return {"status": "error", "message": str(e)}
            
    async def search_faq(self, query: str, size: int = 5) -> Dict[str, Any]:
        """Search FAQ content in Milvus."""
        # Ensure server is ready before processing
        await self.ready_for_connections()
        
        try:
            results = self.milvus_service.search_faq(query, size)
            return {
                "status": "success",
                "results": [result.dict() for result in results]
            }
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return {"status": "error", "message": str(e)} 