# Agentic RAG System

这是一个基于 **FastAPI**、**Vue3**、**Weaviate** 和 **SiliconCloud (硅基流动)** 大模型构建的企业级 Agentic RAG（检索增强生成）系统。

该系统集成了 LlamaIndex 和 LangGraph 的设计思想，支持智能文档检索、多轮对话管理、动态知识库更新以及完整的可观测性追踪。

## ✨ 核心特性

- **🚀 现代化技术栈**: 前端 Vue3 + Vite，后端 FastAPI (Python 3.10+)。
- **🧠 智能 Agent**: 基于检索-生成的 Agentic 工作流，支持上下文感知。
- **📚 多格式支持**: 支持 PDF、Word (.docx)、Markdown (.md) 和纯文本 (.txt) 上传解析。
- **🔍 高效检索**: 集成 Weaviate 向量数据库，支持混合检索与 Top-K 召回。
- **🛡️ 生产级稳定性**: 内置错误重试 (Retry) 与熔断 (Circuit Breaker) 机制。
- **🐳 容器化部署**: 提供完整的 Docker 和 Docker Compose 编排，一键启动。
- **🛠️ 开发者友好**: 提供 Python 和 JavaScript/TypeScript SDK，方便集成。
- **📊 可观测性**: 完整的请求日志追踪与性能监控。

## 🏗️ 技术架构

- **Frontend**: Vue 3, Vite, TailwindCSS (风格)
- **Backend**: FastAPI, Uvicorn
- **LLM**: SiliconCloud API (Qwen/DeepSeek 等模型)
- **Vector DB**: Weaviate (Local instance)
- **RAG Framework**: Custom Pipeline inspired by LlamaIndex & LangGraph
- **Infrastructure**: Docker, Docker Compose

详细架构设计请参阅 [ARCHITECTURE.md](./ARCHITECTURE.md)。

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+ & pnpm
- Docker & Docker Compose (可选，推荐)
- [SiliconCloud](https://siliconflow.cn/) API Key

### 🐳 Docker 一键部署 (推荐)

1. **配置环境变量**
   复制 `.env.example` 为 `.env` (如果不存在则手动创建):

   ```bash
   # Linux/Mac
   export SILICONCLOUD_API_KEY="sk-your-key-here"

   # Windows PowerShell
   $env:SILICONCLOUD_API_KEY="sk-your-key-here"
   ```
2. **启动服务**

   ```bash
   docker compose up -d --build
   ```
3. **访问应用**

   - 前端界面: http://localhost:3000
   - 后端 API: http://localhost:8000/docs
   - Weaviate: http://localhost:8080

### 💻 本地开发

#### 后端 (Backend)

1. 进入后端目录并创建虚拟环境:

   ```bash
   cd backend
   # 使用 uv (推荐)
   uv venv
   # Windows 激活
   ..\.venv\Scripts\Activate.ps1
   # Linux/Mac 激活
   source .venv/bin/activate
   ```
2. 安装依赖:

   ```bash
   uv pip install -r requirements.txt
   ```
3. 配置环境变量:
   在 `backend` 目录下创建 `.env` 文件:

   ```env
   SILICONCLOUD_API_KEY=sk-your-api-key
   SILICONCLOUD_MODEL=Qwen/Qwen2.5-14B-Instruct
   SILICONCLOUD_EMBED_MODEL=Qwen/Qwen3-Embedding-8B
   WEAVIATE_URL=http://localhost:8080
   LOG_LEVEL=INFO
   ```
4. 启动后端服务:
   确保本地已运行 Weaviate (可通过 `docker compose up weaviate text2vec-transformers -d` 启动数据库部分)。

   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### 前端 (Frontend)

1. 进入前端目录:

   ```bash
   cd frontend
   ```
2. 安装依赖并启动:

   ```bash
   pnpm install
   pnpm dev
   ```

   访问 http://localhost:5173 (Vite 默认端口)。

## 🔌 API 说明

详细接口文档启动服务后访问 `/docs` (Swagger UI)。

| 方法 | 路径                   | 说明                                           |
| ---- | ---------------------- | ---------------------------------------------- |
| POST | `/api/chat`          | 发送对话请求，包含 `query` 和 `session_id` |
| POST | `/api/upload`        | 上传文档文件 (PDF/MD/Docx/Txt)                 |
| POST | `/api/admin/reindex` | 重建向量索引 (管理员)                          |
| GET  | `/healthz`           | 健康检查                                       |

## 📦 SDK 使用

本项目提供了 Python 和 JavaScript SDK 方便二次开发。

### Python SDK

位于 `sdk/python/agenticrag.py`

```python
from sdk.python.agenticrag import AgenticRAGClient

client = AgenticRAGClient(base_url="http://localhost:8000")

# 上传文档
client.upload(["./docs/manual.pdf"])

# 对话
response = client.chat(
    session_id="session_001", 
    query="文档里提到了什么核心架构？"
)
print(response["answer"])
```

### JavaScript SDK

位于 `sdk/js/index.ts`

```typescript
import { AgenticRAGClient } from './sdk/js';

const client = new AgenticRAGClient('http://localhost:8000');

// 上传 (File 对象)
await client.upload([fileObject]);

// 对话
const res = await client.chat('session_001', '总结一下文档内容');
console.log(res.answer);
```

## 🧪 测试

后端包含单元测试，覆盖 API 连通性、文档解析与 RAG 流程。

```bash
cd backend
# 运行所有测试
pytest
```

## 📝 License

MIT License
