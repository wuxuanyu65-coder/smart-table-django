# SmartTable Django

轻量服务端渲染餐厅点餐系统。采用 Django Templates + HTMX 的渐进增强方式构建交互；UI 使用 Bootstrap。数据库默认 SQLite（可切换到生产数据库）。

## 技术栈
- Python 3.11/3.12
- Django 5（MTV、Auth、Admin）
- Django Templates + HTMX（无 SPA，服务端渲染为主）
- Bootstrap 5（响应式 UI）
- SQLite（开发环境）

## 目录结构
- smarttable/：项目配置（settings/urls/asgi/wsgi）
- users/：用户与角色（customer/staff/manager）
- tables/：餐桌表与二维码链接
- menu/：菜单、膳食信息、收藏
- orders/：购物车、订单与明细
- templates/：全局模板
  - base.html：站点基础布局（Bootstrap + HTMX）
  - partials/navbar.html、partials/footer.html：可复用布局片段
  - 按应用归档：templates/menu/*、templates/orders/*、templates/users/*
- static/：静态资源
  - css/layout.css、css/components.css、css/styles.css
  - js/htmx-csrf.js（统一 HTMX CSRF 头注入）、js/main.js

## 快速开始（Windows PowerShell）
1. 克隆并进入目录  
   `git clone <YOUR_REPO_URL>` → `cd smart-table-django-1`
2. 创建并激活虚拟环境  
   `py -3 -m venv .venv`  
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`  
   `.\.venv\Scripts\Activate.ps1`
3. 安装依赖  
   `py -3 -m pip install -r requirements.txt`
4. 迁移数据库  
   `py -3 manage.py migrate`
5. 可选：写入演示菜单  
   `py -3 manage.py seed_demo`
6. 创建管理员账号（用于 /admin）  
   `py -3 manage.py createsuperuser`
7. 启动开发服务器  
   `py -3 manage.py runserver`

访问入口：
- 菜单页：`http://127.0.0.1:8000/menu`
- 购物车：`http://127.0.0.1:8000/orders/cart`
- 登录/注册：`/accounts/login`、`/accounts/signup`
- 后台管理：`/admin`

## 快速开始（macOS/Linux）
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # 可选
python manage.py createsuperuser
python manage.py runserver
```

## 已实现功能
- 菜单浏览、分类列表、HTMX “+/-” 无刷新更新购物车数量与当前菜品数量
- 购物车、下单与订单成功页
- 认证：登录/注册页面；结账 checkout 需要登录
- 管理后台可维护 MenuItem、DietaryInfo、Table、Order、OrderItem
- 基础可访问性：表单 label/错误信息、aria-live 更新、可见焦点
- 单元测试：基础模型逻辑（见 `menu/tests.py`、`orders/tests.py`）

## 课程作业对齐
- 后端：Django + 认证 + 数据库模型 + 表单/输入处理
- 前端：Django 模板继承、命名 URL、Bootstrap 响应式、HTMX 增强交互
- 可访问性：语义化结构、label 绑定、可见焦点、购物车 aria-live
- 性能/可持续：按需 JS/CSS，组件化样式，后续可接入 collectstatic 与缓存
- 代码质量：模板片段复用、逻辑在视图、静态资源集中、基本单元测试

## 常见问题
- 激活脚本受限：使用 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- 端口占用：`manage.py runserver 8001`
- 模板/静态不生效：确认 `TEMPLATES.DIRS` 指向 `templates/`，`STATICFILES_DIRS` 指向 `static/`

## 生产准备（简要）
- 环境变量：`DJANGO_SECRET_KEY`、`DJANGO_DEBUG=false`、`ALLOWED_HOSTS` 设置域名/IP
- 静态文件（Nginx/WhiteNoise）：`python manage.py collectstatic`
- 数据库切换：在 `smarttable/settings.py` 配置生产数据库

## 开发脚本
- 运行测试：`python manage.py test`
- 生成迁移：`python manage.py makemigrations`
- 应用迁移：`python manage.py migrate`

## 贡献
欢迎通过 PR 提交改进（组件化模板、订单历史、Dashboard、Channels 实时状态等）。遇到问题请在 Issues 反馈并附复现步骤。
