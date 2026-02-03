# 后端代码说明文档 (Backend Guide)

本文档详细介绍了 Agentic RAG 系统后端部分的代码结构、模块职责及开发指南。后端基于 **FastAPI** 框架，集成了 **Weaviate** 和 **SiliconCloud LLM**。

## 1. 目录结构

```
backend/
├── app/
│   ├── models/          # Pydantic 数据模型
│   │   └── schemas.py       # API 请求/响应 Schema
│   ├── rag/             # RAG 核心逻辑
│   │   ├── document_loader.py # 文档解析 (PDF/MD/Docx)
│   │   ├── pipeline.py        # Agent 执行流 (Retrieve-Generate)
│   │   └── vector_store.py    # Weaviate 向量库封装
│   ├── routers/         # API 路由
│   │   ├── admin.py         # 管理接口 (重置索引等)
│   │   ├── chat.py          # 对话接口
│   │   └── upload.py        # 文件上传接口
│   ├── services/        # 业务服务
│   │   ├── llm_siliconcloud.py # LLM API 客户端
│   │   └── session.py          # 会话内存管理
│   ├── utils/           # 工具函数
│   │   ├── logging.py       # 日志配置
│   │   └── retry.py         # 重试与熔断装饰器
│   ├── config.py        # 全局配置 (Env)
│   └── main.py          # 应用入口 (FastAPI App)
├── tests/               # 单元测试
├── requirements.txt     # Python 依赖
└── Dockerfile           # 后端容器构建文件
```

## 2. 核心模块详解

### 2.1 核心入口 (main.py)

- 初始化 `FastAPI` 应用。
- 配置 CORS 中间件。
- 注册路由 (`/api/chat`, `/api/upload` 等)。
- 配置全局日志。

### 2.2 RAG 管道 (app/rag/)

这是系统的“大脑”。

- **pipeline.py**:

  - `AgentPipeline`: 简化的 Agent 实现。
    1. `run()`: 接收 Query。
    2. 调用 `vector_store` 检索 Top-K 文档。
    3. 拼接 Context 与 Query。
    4. 调用 `llm` 生成回答。
    5. 更新 Session 历史。
  - `build_langgraph`: (可选) 基于 LangGraph 的图式 Agent 定义，支持更复杂的循环与决策。
- **vector_store.py**:

  - 封装 `weaviate-client` (v4)。
  - `init_schema()`: 定义 `Document` 集合 (Class)。
  - `add_documents()`: 批量添加文本块。
  - `query()`: 执行混合检索/向量检索。
- **document_loader.py**:

  - `parse_files()`: 统一入口，根据文件扩展名分发处理逻辑。
  - 支持 `PyPDF2` 解析 PDF，`python-docx` 解析 Word。

### 2.3 服务层 (app/services/)

- **llm_siliconcloud.py**:

  - 封装 HTTP 请求调用 SiliconCloud API (OpenAI 兼容接口)。
  - 集成 `tenacity` 重试机制。
  - 集成 `pybreaker` 熔断机制，防止服务雪崩。
- **session.py**:

  - `SessionManager`: 简单的内存字典存储 `session_id -> history`。
  - 生产环境建议替换为 Redis 实现持久化。

### 2.4 API 路由 (app/routers/)

- **chat.py**:
  - `POST /chat`: 处理用户对话，返回 `ChatResponse` (包含 answer, sources, latency)。
- **upload.py**:
  - `POST /upload`: 接收 `UploadFile` 列表，调用 Loader 解析并存入向量库。

## 3. 配置管理 (app/config.py)

使用 `pydantic-settings` 管理环境变量。

| 变量名                   | 说明         | 默认值                        |
| ------------------------ | ------------ | ----------------------------- |
| `SILICONCLOUD_API_KEY` | LLM API 密钥 | (必填)                        |
| `SILICONCLOUD_MODEL`   | 模型名称     | `Qwen/Qwen2.5-14B-Instruct` |
| `WEAVIATE_URL`         | 向量库地址   | `http://localhost:8080`     |
| `RETRIEVAL_TOP_K`      | 检索文档数   | `4`                         |

## 4. 开发指南

### 环境准备

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 运行服务

```bash
python -m uvicorn app.main:app --reload
```

### 运行测试

```bash
pytest
```

测试文件位于 `tests/test_api.py`，覆盖了健康检查、文档上传和对话接口的基本功能。

## 5. 错误处理与日志

- 系统使用 `logging` 模块输出结构化日志。
- `utils/retry.py` 提供了 `@with_retry` 装饰器，自动处理网络波动。
- 全局异常处理器在 `main.py` 中虽然未显式展示，但 FastAPI 默认处理了 500 错误，建议在生产环境增加自定义 `ExceptionMiddleware`。
