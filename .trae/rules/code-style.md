# ClaudeBlueprint 代码风格规则

本文档定义了 ClaudeBlueprint 项目的代码风格规范。在为用户项目编写代码时，应遵循以下规范。

---

## ClaudeBlueprint Scripts (Python)

### 格式规范
- **缩进**: 4 个空格
- **最大行长度**: 100 字符
- **导入顺序**: 标准库 → 第三方 → 本地模块
- **空行**: 类定义之间 2 行，方法之间 1 行

### 命名约定
- **文件名**: snake_case (`session_start.py`, `post_write_format.py`)
- **类名**: PascalCase (`ConfigManager`, `SessionState`)
- **函数/变量**: snake_case (`get_project_root`, `file_path`)
- **常量**: UPPER_SNAKE_CASE (`MAX_TOKENS`, `DEFAULT_TIMEOUT`)
- **私有成员**: 前缀下划线 (`_internal_function`)

### 类型注解
- 所有公共函数必须有类型注解
- 使用 `|` 而非 `Union` (Python 3.10+)
- 优先使用 `X | None` 而非 `Optional[X]`

### 异步编程
- 使用 `async/await` 语法
- 异步函数命名保持清晰：`get_*`, `fetch_*`, `load_*`
- 使用 `asyncio.run()` 在同步上下文中运行异步代码

### 文档字符串
- 使用 Google 风格文档字符串
- 所有公共模块、类、函数都需要文档字符串

---

## 用户项目代码风格

当为用户编写代码时，根据项目技术栈遵循相应规范：

### Vue 3 项目

#### TypeScript/JavaScript
- **缩进**: 2 个空格
- **字符串**: 单引号
- **分号**: 必须使用
- **尾随逗号**: 多行时必须

#### 组件规范
- 使用 `<script setup lang="ts">` 语法
- 优先使用 Composition API
- 组件命名: PascalCase (`UserProfile.vue`, `DataTable.vue`)

#### 样式
- 使用 scoped 样式
- 优先使用 CSS 变量
- 避免深层选择器

---

### Node.js 项目

#### 代码格式
- **缩进**: 2 个空格
- **字符串**: 单引号
- **分号**: 必须使用

#### 命名约定
- **文件**: kebab-case (`user-service.ts`, `api-client.ts`)
- **变量/函数**: camelCase (`userProfile`, `fetchData`)
- **类/接口**: PascalCase (`UserService`, `IRequest`)
- **常量**: UPPER_SNAKE_CASE (`API_BASE_URL`)

#### Express 路由
- 路由需使用 try/catch 并调用错误处理中间件，避免无错误处理的返回

---

### Python 项目

#### 格式 (遵循 PEP 8 + Black)
- **缩进**: 4 个空格
- **最大行长度**: 88 字符 (Black 默认)

#### 命名约定
- **类**: PascalCase (`UserService`, `APIRouter`)
- **函数/变量**: snake_case (`get_user`, `user_list`)
- **常量**: UPPER_SNAKE_CASE (`API_KEY`, `MAX_SIZE`)

#### FastAPI 路由
- 路由需添加类型注解与错误处理（如 404），保持返回模型一致

---

## 通用规则

### API 端点命名 (RESTful)

| 方法   | 路径            | 说明     |
| ------ | --------------- | -------- |
| GET    | `/users`        | 列表     |
| GET    | `/users/:id`    | 详情     |
| POST   | `/users`        | 创建     |
| PUT    | `/users/:id`    | 完整更新 |
| PATCH  | `/users/:id`    | 部分更新 |
| DELETE | `/users/:id`    | 删除     |

### 查询参数
- 分页: `?page=1&limit=10`
- 排序: `?sort=created_at&order=desc`
- 过滤: `?status=active&role=admin`

### 注释规范
- **函数**: 必须有文档字符串
- **复杂逻辑**: 添加解释性注释
- **避免**: 无意义的注释 (`// i++` 自增)

### 错误处理
- 始终处理可能的错误
- 使用自定义错误类
- 提供有用的错误消息

### 安全规范
- 不在代码中硬编码密钥
- 不在日志中记录敏感信息
- 验证所有用户输入

---

## 代码格式化工具

- **Python**: Black, Ruff
- **TypeScript/JavaScript**: Prettier, ESLint
- **Vue**: Prettier + ESLint

### 使用 Prettier 格式化配置
```json
{
  "singleQuote": true,
  "semi": true,
  "trailingComma": "es5",
  "printWidth": 100
}
```

### 使用 Black 配置
```ini
[tool.black]
line-length = 100
target-version = ['py310']
```
