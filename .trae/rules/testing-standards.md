# ClaudeBlueprint 测试标准

本文档定义了 ClaudeBlueprint 的测试规范。在为用户编写代码时，必须遵循以下测试最佳实践。

---

## 覆盖率要求

### 最低标准
- **单元测试**: 80%+ 代码覆盖率
- **关键路径**: 100% 覆盖率（认证、支付、数据处理等）
- **新功能**: 必须包含测试才能合并

### 覆盖率计算
- Python：`pytest --cov=src`；Node：`npm test -- --coverage`

---

## 测试组织

### 目录结构
- 建议：tests/ 下分 unit、integration、e2e、fixtures 等子目录

### 文件命名

| 语言     | 测试文件格式              | 示例                          |
| -------- | ------------------------- | ----------------------------- |
| Python   | `test_*.py`               | `test_user_service.py`        |
| TypeScript | `*.test.ts`, `*.spec.ts` | `user.service.test.ts`        |
| Vue      | `*.spec.ts`               | `UserProfile.spec.ts`         |

---

## TDD 工作流
### 红-绿-重构
- 流程：先写失败测试 → 最少实现让其通过 → 重构提升质量 → 循环迭代

---

## 测试质量

### 独立性
- 每个测试独立运行
- 不依赖执行顺序
- 不依赖共享状态
- 清理副作用（使用 `tearDown`/`afterEach`）

### 确定性
- 相同输入总是相同输出
- 不使用随机数据（或使用固定种子）
- Mock 外部依赖
- 固定时间/日期

### 速度要求
- 单元测试 < 100ms
- 集成测试 < 5s
- E2E 测试 < 30s

---

## 命名规范

### 描述性名称
- 使用行为驱动的描述性名称；避免 `test_works`、`test_1` 等模糊命名

### AAA 模式 (Arrange-Act-Assert)
- 推荐使用 AAA 模式组织测试步骤（准备/执行/断言）

---

## 断言指南

### 一个断言原则
- 每个测试尽量聚焦一个行为；相关断言可在同一测试中

### 有意义的失败消息
- 使用带匹配条件的断言/异常消息，提升失败可读性

---

## Mock 和 Stub

### 何时使用 Mock
- 文件系统操作
- 网络请求
- 数据库操作
- 时间/日期
- 外部 API

---

## 测试夹具 (Fixtures)
### Pytest Fixtures
- 使用 fixtures 提供稳定的测试数据与资源，并在测试后清理

---

## 跳过和标记测试

### 临时跳过
- 使用 skip/skipif/xfail 管理临时跳过与预期失败

### 测试标记
- 常用标记：unit/integration/slow；通过 `pytest -m` 选择性运行

### TypeScript 示例
- TypeScript：使用 `it.skip`/`it.only`，提交前清理 `only/skip`

---

## CI/CD 集成

### GitHub Actions 示例
- 在 PR 上运行测试与覆盖率，并上传报告（如 Codecov）

### 提交前检查 (Pre-commit)
- 在提交前运行测试，并设置覆盖率下限（如 80%）
- 配置 precommit 脚本运行测试

---

## 禁止事项

- ❌ 提交未完成的测试
- ❌ 注释掉失败的测试
- ❌ 在测试中使用 `try-catch` 隐藏错误
- ❌ 测试私有方法（测试公共接口）
- ❌ 依赖测试执行顺序
- ❌ 在测试中使用随机数据（无固定种子）
- ❌ 过度使用 `any` 类型

---

## 测试审查清单

合并代码前检查：

- [ ] 新代码有测试覆盖
- [ ] 所有测试通过
- [ ] 覆盖率未下降（80%+）
- [ ] 测试命名清晰、描述性强
- [ ] 无 `skip` 或 `only` 残留
- [ ] Mock 适当使用（不过度 mock）
- [ ] 快速执行（全部测试 < 5 分钟）
- [ ] 测试数据独立（不污染数据库）

---

## 各技术栈测试框架

### Python
- **单元测试**: pytest
- **覆盖率**: pytest-cov
- **Mock**: unittest.mock
- **异步测试**: pytest-asyncio

### Node.js/TypeScript
- **单元测试**: Vitest / Jest
- **覆盖率**: c8 / istanbul
- **Mock**: vi.fn() (Vitest) / jest.fn()

### Vue
- **组件测试**: Vitest + @vue/test-utils
- **E2E 测试**: Playwright / Cypress
