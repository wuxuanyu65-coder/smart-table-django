from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import MenuItem
from .forms import MenuItemForm


@ensure_csrf_cookie
def menu_list(request):
    """
    顾客端菜单展示视图
    
    功能:
    1. 展示所有上架的菜品 (is_available=True)
    2. 支持按分类 (category) 筛选
    3. 获取当前购物车的商品数量并显示
    4. 支持 HTMX 局部刷新 (仅更新菜单网格部分)
    
    参数:
    - request: HTTP 请求对象，包含 GET 参数 cat (分类)
    
    返回:
    - 渲染 menu/menu.html 或 menu/_grid.html (HTMX 请求时)
    """
    cat = request.GET.get("cat")
    base_qs = MenuItem.objects.filter(is_available=True)
    if cat:
        base_qs = base_qs.filter(category=cat)
    items = base_qs.order_by("name")

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    qty_by_id = {int(k): v for k, v in cart.items() if str(k).isdigit() or isinstance(k, int)}
    for it in items:
        it.current_qty = qty_by_id.get(it.id, 0)

    # Distinct categories for filter chips (use full available set)
    categories = (
        MenuItem.objects.filter(is_available=True)
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )

    # HTMX partial: return only the grid items to swap into #menu-grid
    if request.headers.get("HX-Request") == "true":
        return render(request, "menu/_grid.html", {"items": items})

    return render(request, "menu/menu.html", {"items": items, "categories": categories})


def admin_dashboard(request):
    """
    管理后台首页视图
    
    功能:
    - 展示管理后台概览 (目前为静态页面)
    
    返回:
    - 渲染 admin_dashboard.html
    """
    return render(request, "admin_dashboard.html")


def menu_manage(request):
    """
    商家端菜单管理列表视图
    
    功能:
    - 展示所有菜品 (包括下架的)
    - 提供编辑和删除操作的入口
    
    返回:
    - 渲染 menu_management/list.html，包含 items 上下文
    """
    items = MenuItem.objects.all().order_by("name")
    return render(request, "menu_management/list.html", {"items": items})


def add_menu_item(request):
    """
    添加新菜品视图
    
    功能:
    - GET: 展示添加菜品的空表单
    - POST: 验证并保存新菜品数据
    
    返回:
    - 成功: 重定向到菜单管理列表 (menu-manage)
    - 失败/GET: 渲染 menu_management/form.html
    """
    if request.method == "POST":
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("menu-manage")
    else:
        form = MenuItemForm()
    return render(request, "menu_management/form.html", {"form": form, "title": "Add Menu Item"})


def edit_menu_item(request, pk):
    """
    编辑菜品视图
    
    功能:
    - GET: 展示包含现有数据的编辑表单
    - POST: 更新指定 ID (pk) 的菜品数据
    
    参数:
    - pk: 菜品的主键 ID
    
    返回:
    - 成功: 重定向到菜单管理列表 (menu-manage)
    - 失败/GET: 渲染 menu_management/form.html
    """
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("menu-manage")
    else:
        form = MenuItemForm(instance=item)
    return render(request, "menu_management/form.html", {"form": form, "title": "Edit Menu Item", "item": item})


def delete_menu_item(request, pk):
    """
    删除菜品视图
    
    功能:
    - 删除指定 ID (pk) 的菜品
    
    参数:
    - pk: 菜品的主键 ID
    
    返回:
    - 重定向到菜单管理列表 (menu-manage)
    """
    item = get_object_or_404(MenuItem, pk=pk)
    item.delete()
    return redirect("menu-manage")
