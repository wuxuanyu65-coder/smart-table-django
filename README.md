# SmartTable Django

轻量服务端渲染餐厅点餐系统。前端采用 Django Templates + HTMX + Alpine.js，后端采用 Django(MTV)，数据库默认 SQLite（可切换到生产数据库）。

## 技术栈
- Django 5（MTV、Auth）
- Django Templates + HTMX + Alpine.js（增强交互，无需大型前端框架）
- SQLite 开发数据库（生产可切换 Postgres/MySQL）

## 目录结构
- smarttable/：项目配置(settings/urls/asgi/wsgi)
- users/：用户与角色（customer/staff/manager）
- tables/：餐桌表与二维码链接
- menu/：菜单、膳食信息、收藏
- orders/：购物车、订单与明细
- templates/base.html：全局基础模板（引入 HTMX/Alpine/样式）
- static/：静态资源（css/js）

## 系统需求
- Python 3.11/3.12
- Windows/Mac/Linux 任一
- 不需要 Conda；推荐 venv（避免环境钩子问题）

## 快速开始（Windows PowerShell）
1. 克隆仓库并进入目录
   - `git clone <YOUR_REPO_URL>`
   - `cd smart-table-django`
2. 创建并激活虚拟环境
   - `py -m venv .venv`
   - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
   - `.\.venv\Scripts\Activate.ps1`
3. 安装依赖
   - `python -m pip install -U pip`
   - `python -m pip install -r requirements.txt`
4. 迁移数据库
   - `python manage.py makemigrations users tables menu orders`
   - `python manage.py migrate`
5. 创建管理员账号（用于 /admin）
   - `python manage.py createsuperuser`
6. 写入演示菜单（可选）
   - `python manage.py seed_demo`
7. 启动开发服务器
   - `python manage.py runserver`
8. 访问
   - 菜单页：`http://127.0.0.1:8000/menu`
   - 购物车：`http://127.0.0.1:8000/orders/cart`
   - 登录/注册：`http://127.0.0.1:8000/accounts/login`，`/accounts/signup`
   - 后台管理：`http://127.0.0.1:8000/admin`

## 快速开始（macOS/Linux）
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python manage.py makemigrations users tables menu orders
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # 可选
python manage.py runserver
```

## 主要功能与路径
- 菜单浏览与加购：`/menu`（HTMX “+/-” 更新右上角购物车角标）
- 购物车与结账：`/orders/cart` → 提交到 `/orders/checkout` → 成功页 `/orders/success/<id>`
- 管理后台：`/admin` 可维护 MenuItem、DietaryInfo、Table、Order、OrderItem

## 常见问题
- “pip/conda 未找到”：使用 `python -m pip ...`；无需 Conda。若激活脚本受限，用 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`。
- 端口占用：`python manage.py runserver 8001`
- 模板/静态不生效：确认 `templates/base.html` 已加载 HTMX/Alpine，且 `STATICFILES_DIRS` 指向 `static/`。

## 生产准备（简要）
- 环境变量：
  - `DJANGO_SECRET_KEY` 强随机值
  - `DJANGO_DEBUG=false`
  - `ALLOWED_HOSTS` 设为你的域名/IP
- 静态文件（如使用 Nginx/WhiteNoise）：`python manage.py collectstatic`
- 数据库切换：在 `smarttable/settings.py` 配置生产数据库。

## 分支与协作（建议）
- 默认主干：`main`
- 特性分支：`feature/<topic>`；修复分支：`fix/<topic>`
- 通过 PR 合并到主干；开启分支保护与线性历史（Squash 或 Rebase）

## 联系与支持
遇到问题请在 Issues 反馈，或在 PR 中描述你的修改和可复现步骤。欢迎贡献菜单管理、后厨看板、实时状态推送（Django Channels）等增强功能。
