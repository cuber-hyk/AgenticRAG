# 前端代码说明文档 (Frontend Guide)

本文档详细介绍了 Agentic RAG 系统前端部分的代码结构、组件设计及开发指南。前端采用 **Vue 3** + **Vite** + **Tailwind CSS** 构建。

## 1. 目录结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── components/      # Vue 组件
│   │   ├── ChatBox.vue       # 核心对话组件
│   │   └── UploadPanel.vue   # 文件上传面板组件
│   ├── assets/          # 静态资源 (Logo, CSS)
│   ├── App.vue          # 根组件 (布局入口)
│   ├── main.js          # 应用入口 (挂载 Vue)
│   └── style.css        # 全局样式 (Tailwind 指令)
├── sdk-js.js            # 后端 API 客户端封装
├── index.html           # HTML 模板
├── package.json         # 依赖配置
├── vite.config.js       # Vite 配置
└── Dockerfile           # 前端容器构建文件
```

## 2. 核心组件详解

### 2.1 ChatBox.vue
对话界面的核心组件，负责展示消息历史和发送用户输入。

- **功能**:
  - 渲染用户消息 (User) 和 AI 回复 (Assistant)。
  - 支持 Markdown 渲染 (通过 `markdown-it`)。
  - 展示参考源 (Sources)。
  - 自动滚动到底部。
- **Props**:
  - `history`: 消息数组对象。
  - `loading`: 当前是否正在生成回复。
- **Events**:
  - `send`: 当用户点击发送或按回车时触发，传递 `query`。

### 2.2 UploadPanel.vue
侧边栏的文件上传组件。

- **功能**:
  - 文件选择 (Input file)。
  - 上传进度与状态展示 (Success/Error)。
  - 调用 SDK 上传文件。
- **Events**:
  - `uploaded`: 上传成功后触发，通知父组件可能需要刷新状态或提示。

### 2.3 App.vue
整个应用的布局容器。

- **布局**:
  - 左侧: `UploadPanel` (固定宽度)。
  - 右侧: `ChatBox` (自适应宽度)。
- **状态管理**:
  - `sessionId`: 生成唯一的会话 ID (UUID v4)。
  - `history`: 维护当前的对话上下文列表。
- **逻辑**:
  - 初始化 `AgenticRAGClient`。
  - 处理 `handleSend`：调用 `client.chat()` 并更新 `history`。

## 3. SDK 集成 (sdk-js.js)

为了解耦 UI 与 API 逻辑，前端通过 `sdk-js.js` (或 TS 版) 与后端交互。

```javascript
// 示例调用
import { AgenticRAGClient } from './sdk-js';

const client = new AgenticRAGClient('http://localhost:8000');

// 上传
await client.upload([fileObj]);

// 对话
const response = await client.chat(sessionId, query);
// response: { answer: "...", sources: [...] }
```

## 4. 样式系统

项目使用 **Tailwind CSS** 进行快速样式开发。
- 配置文件: `tailwind.config.js`
- 全局样式: `src/style.css` (包含 `@tailwind base; ...`)

## 5. 开发与构建

### 安装依赖
```bash
pnpm install
```

### 启动开发服务器
```bash
pnpm dev
# 默认地址: http://localhost:5173
```

### 构建生产版本
```bash
pnpm build
# 输出目录: dist/
```

### Docker 部署
前端使用 Nginx 或轻量级 Node 服务 (本项目示例用 `serve`) 进行容器化托管。
```dockerfile
# 详见 Dockerfile
CMD ["npx", "serve", "-s", "dist", "-l", "3000"]
```
