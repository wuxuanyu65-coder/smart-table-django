# Smart Table 项目实施报告

## 1. 引言 (Introduction)

**项目概述 (Project Overview):**
SmartTable 是一个现代化的基于二维码的餐厅点餐系统，旨在优化用餐体验。它解决了餐饮行业的常见痛点，如服务等待时间长、顾客与厨房之间的沟通错误以及人工点餐效率低下的问题。通过允许顾客直接使用智能手机点餐并为厨房员工提供实时仪表盘，SmartTable 提升了运营效率和顾客满意度。

**设计规范调整 (Adjustments to Design Specification):**
核心功能保持了对原始设计规范的忠实。然而，我们通过集成 **HTMX** 增强了交互性，实现了无需完全刷新页面的动态内容更新（例如：添加商品到购物车、更新订单状态），提供了比原计划使用标准 Django 模板更流畅的用户体验。

**项目链接 (Project Links):**
*   **代码仓库:** [在此处插入 GitHub/GitLab 链接]
*   **部署应用:** [在此处插入 PythonAnywhere/Heroku 链接]

---

## 2. 更新后的设计规范 (Updated Design Specification)

*(说明：请按照说明在此处插入您的图表)*

**2.1 用户故事 (User Stories):**
[在此处粘贴 MoSCoW 列表]

**2.2 系统架构图 (System Architecture Diagram):**
[在此处粘贴架构图]

**2.3 ER 图 (ER Diagram):**
[在此处粘贴数据库 ER 图]

**2.4 网站地图 (Sitemap):**
[在此处粘贴网站地图]

**2.5 线框图 (Wireframes):**
[在此处粘贴 4 张带标注的线框图]

---

## 3. 实现亮点 (Implementation Highlights)

**3.1 主要组件与核心功能 (Main Components & Key Features):**
该系统基于 Django 框架开发，实现了完整的餐厅点餐业务流程。核心功能及后端交互逻辑如下：

*   **用户认证系统 (User Authentication System)**:
    *   **功能**: 实现了基于 Django 内置 `AbstractUser` 的自定义用户模型，支持用户注册、登录、个人资料管理及注销功能。区分了普通顾客和管理员（员工）权限。
    *   **后端交互 (CRUD)**: 使用 `User.objects.create_user()` 创建新用户；利用 `authenticate()` 和 `login()` 处理会话安全；通过 `@login_required` 装饰器保护敏感视图。

*   **菜单展示与管理 (Menu Display & Management)**:
    *   **功能**: 顾客端支持按类别浏览菜品，查看详细描述、价格及过敏原信息。员工端具备完整的后台管理功能，可对菜品进行增删改查。
    *   **后端交互 (CRUD)**:
        *   **Read**: 视图通过 `MenuItem.objects.all()` 或 `filter()` 获取菜品列表。
        *   **Create**: 使用 `MenuItemForm` 处理表单数据，调用 `.save()` 将新菜品写入数据库。
        *   **Update/Delete**: 利用 `get_object_or_404()` 获取特定对象，配合 `.save()` 更新或 `.delete()` 删除数据。

*   **购物车与订单提交流程 (Shopping Cart & Order Submission)**:
    *   **功能**: 实现了基于 `Django Session` 的持久化购物车，允许用户跨页面保留已选商品。结账流程将购物车内的临时数据转化为数据库中的持久化订单记录。
    *   **后端交互 (CRUD)**:
        *   **Session**: 购物车数据存储在 `request.session['cart']` 中，不直接读写数据库，提高性能。
        *   **Create**: 提交订单时，使用 `transaction.atomic()` 确保原子性：先创建 `Order` 主表记录，再批量创建 `OrderItem` 关联记录，最后清空 Session 购物车。

*   **员工后台实时订单查看 (Staff Real-time Dashboard)**:
    *   **功能**: 提供专用的厨房看板，通过 **HTMX** 轮询技术实时刷新待处理订单，支持一键更新订单状态（如“准备中”、“已完成”）。
    *   **后端交互 (CRUD)**:
        *   **Read**: 通过 `Order.objects.filter(status='pending').order_by('-created_at')` 筛选最新的待处理订单。
        *   **Update**: 员工点击状态按钮时，后端接收请求并执行 `order.status = new_status; order.save()` 更新状态字段。

**3.2 前端交互 (Front-end Interactivity):**
为了提供流畅且现代的用户体验，我们采用了轻量级的前端技术栈，重点利用 **HTMX** 库来实现 AJAX 风格的动态交互，辅以少量的原生 JavaScript 和 Bootstrap 组件。

*   **动态购物车更新 (Dynamic Cart Updates via AJAX/HTMX)**:
    *   **实现机制**: 传统的购物车操作通常需要页面刷新，这会打断用户的点餐流程。我们使用 HTMX 的 `hx-post` 属性拦截表单提交，向后端发送异步请求。
    *   **交互细节**: 当用户点击“添加”按钮时，后端更新 Session 数据并返回一个新的购物车徽章 HTML 片段。HTMX 自动将旧的徽章替换为新的数量（`hx-target="#cart-badge"`，`hx-swap="outerHTML"`），同时触发一个 Toast 提示框显示“添加成功”，整个过程页面无刷新。

*   **实时仪表盘轮询 (Real-time Dashboard Polling)**:
    *   **实现机制**: 厨房端需要实时感知新订单。我们利用 HTMX 的轮询功能 (`hx-trigger="every 5s"`)，每隔 5 秒自动向服务器请求最新的订单列表 HTML。
    *   **交互细节**: 服务器返回最新的订单列表局部模板，HTMX 使用 `hx-swap="innerHTML"` 仅更新订单列表区域。这确保了厨房员工无需手动刷新即可看到最新订单，减少了漏单风险。

*   **表单验证与反馈 (Form Validation & Feedback)**:
    *   **实现机制**: 在用户注册或添加菜品时，我们结合了 HTML5 的客户端验证（`required`, `type="email"`）和 Django 的服务端验证。
    *   **交互细节**: 如果服务端验证失败（例如用户名已存在），后端返回带有错误信息的表单片段，HTMX 将其动态替换到当前表单位置，并在字段下方高亮显示错误信息，无需页面跳转，提升了填写的便捷性。

*   **模态框交互 (Modal Interactions)**:
    *   **实现机制**: 对于关键操作（如过敏原警告），我们使用 Bootstrap Modal 结合 HTMX。
    *   **交互细节**: 当用户尝试添加含有过敏原的菜品时，后端检测到风险并返回一个模态框的 HTML，HTMX 将其插入 DOM 并自动触发显示。用户必须确认后才能继续，这种强制性的交互流程有效保障了用餐安全。

**3.3 界面与用户体验 (Look and Feel - UI/UX):**
为了确保在各种设备上的一致性和美观性，我们采用了 **Bootstrap 5** 前端框架，并进行了深度的自定义。

*   **响应式设计 (Responsive Design)**:
    *   **Bootstrap Grid**: 广泛使用 Bootstrap 的网格系统（`col-md-`, `col-lg-`），确保布局在手机端（单列堆叠）和桌面端（多列并排）之间自动适配。例如，菜单网格在移动设备上每行显示 1 个项目，而在大屏幕上自动调整为 3-4 个。
    *   **移动优先 (Mobile-First)**: 考虑到主要用户群体是使用手机点餐的顾客，所有交互元素（按钮、导航栏）都针对触控进行了优化，确保点击区域足够大且易于操作。

*   **玻璃拟态设计 (Glassmorphism Theme)**:
    *   **视觉风格**: 我们并未直接使用 Bootstrap 的默认样式，而是通过 `static/css/styles.css` 实现了一套现代化的“玻璃拟态”主题。利用 CSS 的 `backdrop-filter: blur()` 属性，创建了具有半透明磨砂效果的卡片背景，配合深色背景和鲜艳的强调色，提升了视觉层次感和科技感。
    *   **无障碍考量**: 尽管使用了半透明背景，我们仍通过精心调整文字颜色对比度（符合 WCAG 标准），确保内容清晰可读。

**3.4 代码质量与结构 (Code Quality & Structure):**
项目遵循 Django 的最佳实践，强调代码的可维护性和可扩展性。

*   **模块化应用结构 (Modular App Structure)**:
    *   功能逻辑被清晰地拆分为三个独立的应用：`users`（认证）、`menu`（商品管理）和 `orders`（交易流程）。每个应用拥有独立的 `models.py`, `views.py`, `urls.py`，降低了耦合度。

*   **模板继承与复用 (Template Inheritance & DRY)**:
    *   **base.html**: 创建了一个全局基础模板 `base.html`，包含通用的 HTML 结构、导航栏、页脚以及 CSS/JS 资源引用。所有其他页面通过 `{% extends 'base.html' %}` 继承此模板，避免了重复代码。
    *   **Partial Templates**: 将重复使用的 UI 组件（如导航栏 `navbar.html`、菜品卡片 `_grid.html`）提取为局部模板，通过 `{% include %}` 引入，提高了代码复用率。

*   **前后端分离 (Separation of Concerns)**:
    *   **静态文件**: 所有的样式表（CSS）和脚本（JavaScript）都存放在 `static/` 目录下，而不是硬编码在 HTML 模板中，保持了页面结构的整洁。
    *   **逻辑分离**: 业务逻辑封装在 `views.py` 和 `models.py` 中，模板仅负责展示数据，不包含复杂的 Python 逻辑。

*   **URL 命名与反向解析 (URL Naming & Reverse Resolution)**:
    *   **Namespacing**: 所有的 URL 模式都定义了 `name` 属性（如 `name='cart_add'`），并在应用层面使用了 `app_name` 命名空间。
    *   **Reverse Resolution**: 在模板中始终使用 `{% url 'orders:cart_add' %}` 动态生成链接，在视图中使用 `reverse()` 函数。这消除了硬编码 URL 路径带来的维护风险，即使后续修改 URL 结构，也不需要手动更新代码中的链接。

---

## 4. 测试 (Testing)

**4.1 已实现的单元测试 (Unit Tests Implemented):**
我们实现了覆盖关键业务逻辑的全面单元测试：
*   **Menu Tests (`menu/tests.py`)**: 验证模型字符串表示、过敏原处理和菜单项创建流程。
*   **Order Tests (`orders/tests.py`)**: 测试结账流程，确保从购物车会话正确创建订单，并验证管理视图的权限逻辑。

**4.2 运行测试指南 (Instructions for Running Tests):**
要在终端执行测试套件，请运行以下命令：
```bash
python manage.py test
```

**4.3 系统测试结果 (System Testing Results):**
*(请在此处插入终端显示“OK”的测试运行截图)*

---

## 5. 无障碍报告 (Accessibility Report)

**(从设计中选择实现的 3 个功能)**

**已实现的改进 (Improvements Implemented):**

**改进点 1: 目标尺寸 (Target Size - WCAG 2.5.8)**
我们确保所有交互元素，特别是面向移动端的顾客菜单，具有足够的目标尺寸。
*   **实现方式**: “加入购物车”按钮和导航链接利用了 Bootstrap 的宽大内边距和 `btn-lg` 类，确保它们在触摸屏上易于点击（超过 24x24 像素的最小值）。
*   *(请插入显示大号“添加”按钮的菜单页面截图)*

**改进点 2: 颜色对比度 (Colour Contrast - WCAG 1.4.3)**
我们精心调整了调色板，以确保文本在背景上的可读性，特别是在玻璃拟态主题中。
*   **实现方式**: 在 `styles.css` 中，我们定义了自定义变量（例如 `--st-muted`），以确保即使是管理仪表盘中“未激活”的导航标签，在深色背景下也能保持至少 4.5:1 的对比度。深色半透明卡片上的白色文本提供了高可见性。
*   *(请插入管理仪表盘导航或菜单卡片的截图)*

**改进点 3: 状态信息 (Status Messages - WCAG 4.1.3)**
系统为用户操作提供即时、果断的反馈，无需转移焦点。
*   **实现方式**: 当用户添加包含其过敏原的商品时，会立即出现一个 **模态对话框**（通过 HTMX 交换）进行警告。此外，成功的订单提交会通过清晰的成功消息进行确认。这些动态更新是程序化的，可以被屏幕阅读器拦截。
*   *(请插入过敏原警告模态框或订单成功消息的截图)*
