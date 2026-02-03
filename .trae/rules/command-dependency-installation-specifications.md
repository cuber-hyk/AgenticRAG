命令和依赖安装规范文档

1. 总则
本规范旨在统一AI项目的依赖安装流程，确保环境隔离和安装效率。
2. Python 依赖安装规范
2.1 虚拟环境管理
• 必须 使用 uv 作为虚拟环境管理工具
• 禁止 使用系统全局 Python 环境直接安装依赖

2.2 依赖安装命令
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# 安装依赖
uv pip install -r requirements.txt
# 或直接安装单个包
uv pip install package_name

2.3 依赖文件管理
• 依赖必须记录在 requirements.txt 中

3. 前端依赖安装规范
3.1 包管理器选择
• 优先 使用 pnpm
• 允许 使用 cnpm
• 严格禁止 使用 npm

3.2 安装命令
# 使用 pnpm（推荐）
pnpm install
# 使用 cnpm（备选）
cnpm install

4. 持续集成配置
示例
      # 安装 uv
      - uses: astral-sh/setup-uv@v1
      
      # Python 依赖
      - run: uv venv
      - run: source .venv/bin/activate
      - run: uv pip install -r requirements.txt
      
      # 前端依赖
      - uses: pnpm/action-setup@v2
      - run: pnpm install

5. 通用命令
采用powershell命令执行
