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
该系统使用 Django 的 MVT 架构构建，包含三个主要应用：
*   **Users (`users/models.py`)**: 处理自定义用户认证和个人资料管理。
*   **Menu (`menu/models.py`, `menu/views.py`)**: 管理菜单类别、菜品和过敏原。支持员工对菜单进行 CRUD 操作。
*   **Orders (`orders/models.py`, `orders/views.py`)**: 核心引擎，管理购物车（基于会话）、订单创建和实时状态跟踪。
*   **Admin Dashboard**: 专为厨房员工设计的视图，用于查看实时订单，利用 HTMX 每 5 秒轮询一次以获取新订单，无需手动刷新。

**3.2 前端交互 (Front-end Interactivity):**
我们利用 **HTMX** 实现了现代化的响应式前端，而无需引入完整的 SPA 框架（如 React）的复杂性。关键的交互功能包括：
*   **动态购物车更新**: 添加商品会立即更新购物车计数 (`orders/views.py` `cart_add`)。
*   **实时仪表盘**: 厨房仪表盘自动轮询服务器 (`hx-trigger="every 5s"`) 以显示新订单。
*   **状态管理**: 员工可以一键更新订单状态（待处理 -> 准备中 -> 就绪），即时反映在界面上。

**3.3 界面与用户体验 (Look and Feel - UI/UX):**
界面使用 **Bootstrap 5** 构建，采用响应式、移动优先的布局。我们实现了一个自定义的 **玻璃拟态 (Glassmorphism)** 设计主题 (`static/css/styles.css`)，其特点是带有背景模糊效果的半透明卡片、暗黑模式美学和鲜艳的强调色，确保在移动设备和厨房显示器上都能获得视觉上的吸引力。

**3.4 代码质量与结构 (Code Quality & Structure):**
*   **模块化设计**: 功能被拆分为独立的应用 (`users`, `menu`, `orders`)。
*   **模板继承**: 所有页面继承自 `base.html` 以确保一致的布局和资源加载。
*   **DRY 原则**: 可重用的组件（如 `navbar.html`, `_grid.html`）被分离为局部模板。
*   **安全性**: 使用 Django 内置的装饰器 (`@login_required`, `@user_passes_test`) 确保健壮的访问控制。

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
