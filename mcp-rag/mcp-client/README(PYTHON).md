

## 环境设置

1. Python版本：
```bash
Python 3.10.12
```

2. 创建虚拟环境（可选但推荐）：
```bash
python -m venv env-mcp-rag
source env-mcp-rag/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```


## 功能示例

### 导入知识库
```bash
(tablestore) root@fly:~/AI-Box/code/rag/alibabacloud-tablestore-mcp-server/tablestore-java-mcp-server-rag/knowledge-data-generator# python knowledge_manager.py import tablestore_vector.md
Total Chunks: 1
Processing chunk 0.

[Calling tool storeKnowledge with args {'content': '表格存储向量检索在原有的 DiskANN 算法之上进行优化，提供大规模和高性能的向量检索服务。前期我们也先对用户提供了基于 HNSW 的图算法，但是发现明显的性能问题。', 'meta_data': {'source': 'internal documentation', 'version': '1.0'}}]
内容已经成功存储到知识库中。如果您需要查询或进一步操作，请告诉我。

[Calling tool storeKnowledge with args {'content': 'HNSW 对内存要求很高，很难支撑大规模数据，当内存不足时，HNSW 访问磁盘的性能极差。', 'meta_data': {'source': '技术文档', 'author': '张三'}}]
文档已成功存储到知识库中。存储的内容是关于HNSW对内存的要求很高，并且在处理大规模数据时存在困难，尤其是在内存不足需要访问磁盘时性能会变得极差。如果有任何其他问题或需要进一步的帮助，请告诉我！

[Calling tool storeKnowledge with args {'content': '表格存储上的用户大多数据量相对较大，HNSW 的规模和成本问题不符合我们产品的定位。', 'meta_data': {'source': '内部讨论', 'date': '2023-04-01'}}]
文档已成功存储到知识库中。如果您需要查询或进一步操作，请告诉我。

[Calling tool storeKnowledge with args {'content': '我们希望可以让更多的数据可以低成本地使用上向量能力，因此我们后续废弃掉了 HNSW 算法，使用 DiskAnn 重新实现了向量检索能力。', 'meta_data': {'author': '张三', 'date': '2023-04-01'}}]
文档已成功存储到知识库中。内容是：“我们希望可以让更多的数据可以低成本地使用上向量能力，因此我们后续废弃掉了 HNSW 算法，使用 DiskAnn 重新实现了向量检索能力。”并且附加了作者“张三”和日期“2023-04-01”作为元数据。

[Calling tool storeFAQ with args {'answer': '表格存储向量检索在原有的 DiskANN 算法之上进行了优化。', 'question': '表格存储向量检索使用了什么算法进行优化？'}]
已经将您提供的问题和答案成功存储到了FAQ库中。问题为：“表格存储向量检索使用了什么算法进行优化？” 答案是：“表格存储向量检索在原有的 DiskANN 算法之上进行了优化。” 如果您还有其他条目需要添加，或者有其他任何问题，请告诉我！

[Calling tool storeFAQ with args {'answer': '因为 HNSW 图算法存在明显的性能问题，尤其是对内存的要求很高，难以支撑大规模数据，而且在内存不足的情况下访问磁盘的性能很差。', 'question': '为什么放弃了基于 HNSW 的图算法？'}]
已经将提供的问题和答案存储到了FAQ库中。如果需要查询或进一步操作，请告诉我。

[Calling tool storeFAQ with args {'answer': 'HNSW 图算法对内存需求高，难以支持大规模的数据集，且在内存不够时磁盘访问效率很低。', 'question': 'HNSW 图算法有什么局限性？'}]
该内容已成功存储到FAQ库中。问题是：HNSW 图算法有什么局限性？答案是：HNSW 图算法对内存需求高，难以支持大规模的数据集，且在内存不够时磁盘访问效率很低。

[Calling tool storeFAQ with args {'answer': '表格存储上的用户通常拥有较大的数据量。', 'question': '表格存储用户的典型数据量是怎样的？'}]
已经将提供的问题和答案存储到了FAQ库中。如果您有其他问题或需要进一步的帮助，请告诉我！

[Calling tool storeFAQ with args {'answer': '由于 HNSW 的规模和成本问题，并不符合表格存储产品的定位。', 'question': 'HNSW 是否符合表格存储产品的定位？'}]
该FAQ已经成功存储到FAQ库中。问题为：“HNSW 是否符合表格存储产品的定位？” 答案为：“由于 HNSW 的规模和成本问题，并不符合表格存储产品的定位。”

[Calling tool storeFAQ with args {'answer': '表格存储的目标是让更多的数据能够以低成本的方式使用向量检索能力。', 'question': '表格存储的目标是什么？'}]
已经将提供的问题和答案存储到了FAQ库中。您可以随时查询它们。问题是：“表格存储的目标是什么？”而答案是：“表格存储的目标是让更多的数据能够以低成本的方式使用向量检索能力。”如果您有其他信息需要存入或者查询，请告诉我。

[Calling tool storeFAQ with args {'answer': '最终选择了 DiskANN 算法来重新实现向量检索能力。', 'question': '最终选择了哪种算法来实现向量检索？'}]
该内容已成功存储到FAQ库中。问题是：“最终选择了哪种算法来实现向量检索？”答案是：“最终选择了 DiskANN 算法来重新实现向量检索能力。”
```
### 检索知识库

```bash
(tablestore) root@fly:~/AI-Box/code/rag/alibabacloud-tablestore-mcp-server/tablestore-java-mcp-server-rag/knowledge-data-generator# python knowledge_manager.py search "Tablestore雇层向量素引算法送择了思种实现?"

[Calling tool searchKnowledge with args {'query': 'Tablestore雇层向量素引算法送择了思种实现?', 'size': 20}]
[Calling tool searchFAQ with args {'query': 'Tablestore雇层向量素引算法送择了思种实现?', 'size': 20}]
Knowledge：1. 表格存储向量检索在原有的 DiskANN 算法之上进行优化，提供大规模和高性能的向量检索服务。前期我们也先对用户提供了基于 HNSW 的图算法，但是发现明显的性能问题。
2. 我们希望可以让更多的数据可以低成本地使用上向量能力，因此我们后续废弃掉了 HNSW 算法，使用 DiskANN 重新实现了向量检索能力。
3. 表格存储上的用户大多数据量相对较大，HNSW 的规模和成本问题不符合我们产品的定位。
4. HNSW 对内存要求很高，很难支撑大规模数据，当内存不足时，HNSW 访问磁盘的性能极差。

FAQ：1. 最终选择了哪种算法来实现向量检索？- 最终选择了 DiskANN 算法来重新实现向量检索能力。
2. 为什么放弃了基于 HNSW 的图算法？- 因为 HNSW 图算法存在明显的性能问题，尤其是对内存的要求很高，难以支撑大规模数据，而且在内存不足的情况下访问磁盘的性能很差。
3. 表格存储向量检索使用了什么算法进行优化？- 表格存储向量检索在原有的 DiskANN 算法之上进行了优化。
4. HNSW 图算法有什么局限性？- HNSW 图算法对内存需求高，难以支持大规模的数据集，且在内存不够时磁盘访问效率很低。
5. HNSW 是否符合表格存储产品的定位？- 由于 HNSW 的规模和成本问题，并不符合表格存储产品的定位。
6. 表格存储用户的典型数据量是怎样的？- 表格存储上的用户通常拥有较大的数据量。
7. 表格存储的目标是什么？- 表格存储的目标是让更多的数据能够以低成本的方式使用向量检索能力。

```

### 基于知识库进行问答
```bash
(tablestore) root@fly:~/AI-Box/code/rag/alibabacloud-tablestore-mcp-server/tablestore-java-mcp-server-rag/knowledge-data-generator# python knowledge_manager.py chat "Tablestore雇层向量素引算法选择了围种实现？"

[Calling tool searchKnowledge with args {'query': 'Tablestore雇层向量素引算法', 'size': 10}]
[Calling tool searchFAQ with args {'query': 'Tablestore雇层向量素引算法', 'size': 10}]
从检索到的信息来看，Tablestore 最初尝试了基于 HNSW 的图算法来实现向量检索功能，但很快发现该算法存在明显的性能问题，特别是对内存的要求很高，难以支撑大规模数据集。当内存不足时，HNSW 访问磁盘的效率极低，这与 Tablestore 用户通常拥有较大数据量的情况不符。

为了解决这些问题，并且让更多的数据能够以低成本的方式使用上向量检索能力，Tablestore 后续放弃了 HNSW 算法，转而选择了 DiskANN 算法来重新实现向量检索能力。DiskANN 算法在原有基础上进行了优化，提供了更高效的大规模和高性能向量检索服务。

因此，Tablestore 用于实现向量索引的最终算法是 DiskANN。这种选择旨在更好地满足用户需求，提供更为强大、成本效益更高的向量检索解决方案。
```