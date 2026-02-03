# ClaudeBlueprint 安全规则

本文档定义了 ClaudeBlueprint 的安全规范。在为用户编写代码时，必须遵循以下安全最佳实践。

---

## 认证授权

### JWT 令牌
- 始终在受保护路由上验证 JWT 令牌
- 使用强密钥（至少 32 字符）
- 设置合理的过期时间
- 实现令牌刷新机制
- 验证失败返回 401/403，成功后将用户信息附加到请求上下文

### 密码安全
- 使用 bcrypt/argon2 哈希密码
- 不在日志中记录密码
- 要求最小密码强度（8+ 字符，包含大小写字母、数字）
- 实现密码重置流程

### 速率限制
- 在认证端点实施速率限制
- 防止暴力破解攻击
- 使用 Redis 存储计数器
- 典型阈值：登录 5/分钟，密码重试 3/小时

---

## 数据验证

### 输入验证
- **所有**用户输入必须在后端验证
- 使用 Pydantic (Python) 或 Zod (Node.js)
- 验证类型、长度、格式
- 清理特殊字符防止 XSS

### SQL 注入防护
- 始终使用参数化查询
- 使用 ORM (SQLAlchemy/TypeORM/Prisma)
- 不拼接 SQL 字符串
- 禁止字符串拼接生成 SQL；统一采用绑定变量或 ORM 查询

### XSS 防护
- 转义用户生成的内容
- 设置 Content-Security-Policy 头
- 使用 httpOnly Cookie
- 推荐 CSP：`default-src 'self'`，并设置 `X-Frame-Options: DENY`

---

## 密钥管理

### 环境变量
- 不在代码中硬编码 API 密钥
- 使用 `.env` 文件（本地开发）
- 生产环境使用密钥管理服务
- `.env` 文件必须加入 `.gitignore`
- 在应用启动时校验关键环境变量是否存在，缺失则失败

### 敏感数据保护
不在日志中记录：
- 密码
- 令牌
- API 密钥
- 个人身份信息 (PII)
- 信用卡号
- 对日志输入进行清洗，敏感键统一替换为 `***`

---

## HTTPS 与传输安全

### 生产环境
- 始终使用 HTTPS
- 配置 HTTP → HTTPS 重定向
- 使用 HSTS 头
- 仅允许受信任主机访问；生产环境强制 HTTPS 重定向

### CORS 配置
- 明确配置允许的来源
- 不使用 `*` 在生产环境
- 验证 Origin 头
- 允许来源通过环境变量配置；仅开放必要方法与头

---

## 依赖安全

### 定期审计
- Python 使用 `pip-audit`/`safety`；Node 使用 `npm audit`/`npm audit fix`

### 保持更新
- 定期更新依赖
- 订阅安全公告
- 使用 Dependabot
- 固定关键依赖版本或采用安全范围版本；开启自动安全更新

---

## 常见漏洞防护清单

在提交代码前检查：

- [ ] **SQL 注入** - 使用参数化查询或 ORM
- [ ] **XSS** - 转义输出，设置 CSP
- [ ] **CSRF** - 使用 CSRF 令牌
- [ ] **点击劫持** - 设置 X-Frame-Options
- [ ] **不安全的反序列化** - 验证数据
- [ ] **日志注入** - 清理日志输入
- [ ] **敏感数据泄露** - 不在日志中记录敏感信息
- [ ] **认证失效** - 正确实现会话管理
- [ ] **路径遍历** - 验证文件路径
- [ ] **XXE** - 禁用 XML 外部实体

---

## 必须的安全响应头
- 必设：`X-Content-Type-Options=nosniff`, `X-Frame-Options=DENY`, `Strict-Transport-Security`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy`

---

## 文件上传安全
- 验证文件类型（不只检查扩展名）
- 限制文件大小
- 重命名上传文件（防止路径遍历）
- 存储在 web 根目录外
- 扫描恶意软件
- 典型限制：图片仅允许 jpg/jpeg/png/gif；大小 ≤ 5MB；统一生成安全文件名

---

## 错误处理

### 生产环境
- 不暴露堆栈跟踪
- 使用通用错误消息
- 详细错误记录到日志
- 实现错误监控
- 统一全局异常处理：生产环境隐藏细节；开发环境可返回详细错误

---

## 敏感配置检查

在 ClaudeBlueprint hooks 中实现的安全检查：

### pre_write_quality_check.py
- 检测硬编码的密钥、密码、令牌
- 检测不安全的配置
- 关键检测模式覆盖 password/api_key/token/secret 等关键词
