from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.db.models import ProtectedError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import MenuItem, Favorite
from .forms import MenuItemForm
from tables.models import Table


@ensure_csrf_cookie
def menu_list(request):
    """
    顾客端菜单展示视图
    
    功能:
    1. 展示所有上架的菜品 (is_available=True)
    2. 支持按分类 (category) 筛选
    3. 获取当前购物车的商品数量并显示
    4. 支持 HTMX 局部刷新 (仅更新菜单网格部分)
    5. 处理桌号逻辑: 从 URL 参数获取 table 并存入 session
    
    参数:
    - request: HTTP 请求对象，包含 GET 参数 cat (分类), table (桌号)
    
    返回:
    - 渲染 menu/menu.html 或 menu/_grid.html (HTMX 请求时)
    """
    # 处理桌号逻辑 (QR Code scan -> ?table=X)
    table_number = request.GET.get("table")
    if table_number:
        request.session["table_id"] = table_number
    
    # 获取当前桌号用于显示
    current_table_id = request.session.get("table_id", "1")
    
    cat = request.GET.get("cat")
    # SHOW ALL items, even unavailable ones (to display "Sold Out")
    base_qs = MenuItem.objects.all()
    if cat:
        base_qs = base_qs.filter(category=cat)
    items = list(base_qs) # Convert to list for Python sorting

    # 获取当前用户的收藏列表
    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(Favorite.objects.filter(user=request.user).values_list("item_id", flat=True))
    
    # 将收藏状态附加到 items 上 (注意: 这不是 Model 字段，是运行时属性)
    for it in items:
        it.is_favorite = it.id in user_favorites

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    qty_by_id = {int(k): v for k, v in cart.items() if str(k).isdigit() or isinstance(k, int)}
    for it in items:
        it.current_qty = qty_by_id.get(it.id, 0)

    # Sort categories in a specific order: Starters -> Mains -> Sides -> Desserts -> Drinks -> Others
    priority_order = ["Starters", "Mains", "Sides", "Desserts", "Drinks"]
    
    # Distinct categories for filter chips (use full available set)
    all_cats = (
        MenuItem.objects.all()
        .values_list("category", flat=True)
        .distinct()
    )
    
    # Manual sort
    categories = sorted(all_cats, key=lambda x: priority_order.index(x) if x in priority_order else 999)

    # Sort items: 
    # 1. Category Priority
    # 2. Availability (Available first)
    # 3. Name
    def item_sort_key(x):
        cat_score = priority_order.index(x.category) if x.category in priority_order else 999
        avail_score = 0 if x.is_available else 1
        return (cat_score, avail_score, x.name)

    items = sorted(items, key=item_sort_key)

    # HTMX partial: return only the grid items to swap into #menu-grid
    if request.headers.get("HX-Request") == "true":
        return render(request, "menu/_grid.html", {"items": items})

    return render(request, "menu/menu.html", {"items": items, "categories": categories, "table_id": current_table_id})


@login_required
@require_POST
def toggle_favorite(request, item_id):
    """
    切换收藏状态视图 (HTMX)
    
    功能:
    - 如果已收藏则删除，未收藏则添加
    - 返回更新后的心形图标 HTML
    """
    item = get_object_or_404(MenuItem, id=item_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, item=item)
    
    if not created:
        # 已经存在，则删除 (Toggle Off)
        fav.delete()
        is_fav = False
    else:
        # 新建成功 (Toggle On)
        is_fav = True
        
    # 返回 SVG 图标 HTML
    # 使用 Bootstrap Icons
    filled_heart = '<i class="bi bi-heart-fill text-danger fs-5"></i>'
    empty_heart = '<i class="bi bi-heart text-white fs-5"></i>'

    return HttpResponse(filled_heart if is_fav else empty_heart)


@login_required
def favorites_list(request):
    """
    收藏夹列表页
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('item')
    items = [f.item for f in favorites]
    
    # Sort items by category to make _grid.html grouping work
    items.sort(key=lambda x: x.category)
    
    # Re-use item properties logic if needed (e.g. qty in cart)
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    qty_by_id = {int(k): v for k, v in cart.items() if str(k).isdigit() or isinstance(k, int)}
    
    for it in items:
        it.current_qty = qty_by_id.get(it.id, 0)
        it.is_favorite = True  # Obviously
        
    return render(request, "menu/favorites.html", {"items": items})


from django.db.models import Count, Sum
from django.utils import timezone
from orders.models import Order

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """
    管理后台首页视图
    
    功能:
    - 展示管理后台概览 (实时数据)
    - 统计: 
        1. 待处理订单数 (Pending)
        2. 准备中订单数 (Preparing)
        3. 今日总订单数
        4. 今日总收入
    
    返回:
    - 渲染 admin_dashboard.html
    """
    # 1. 获取当前时间 (Today)
    today = timezone.now().date()
    
    # 2. 统计状态
    # Filter orders from today
    today_orders = Order.objects.filter(order_time__date=today)
    
    # Total revenue today
    today_revenue = today_orders.aggregate(total=Sum('total_price'))['total'] or 0.00
    
    # Total orders today
    today_order_count = today_orders.count()
    
    # Live Status Counts (All time or just active ones, usually all active ones regardless of date)
    active_orders = Order.objects.filter(status__in=[Order.Status.PENDING, Order.Status.PREPARING])
    pending_count = active_orders.filter(status=Order.Status.PENDING).count()
    preparing_count = active_orders.filter(status=Order.Status.PREPARING).count()
    
    context = {
        "today_revenue": today_revenue,
        "today_order_count": today_order_count,
        "pending_count": pending_count,
        "preparing_count": preparing_count,
    }
    
    return render(request, "admin_dashboard.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
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


def get_grouped_allergens(form):
    """
    Helper function to group form allergen widgets by category
    Returns a dict: {category_code: {'label': label, 'widgets': [widget, ...]}}
    """
    from .models import Allergen
    
    # 1. Get all allergens to map ID -> Category
    # Use distinct to avoid duplicates if any, though ID is unique
    allergens = Allergen.objects.all()
    allergen_cat_map = {a.id: a.category for a in allergens}
    
    # 2. Initialize groups in specific order based on Choices
    groups = {}
    for code, label in Allergen.Category.choices:
        groups[code] = {
            'label': label,
            'widgets': []
        }
    
    # 3. Iterate over the bound field widgets
    # form['allergens'] yields BoundWidget objects
    if 'allergens' not in form.fields:
        return groups

    for widget in form['allergens']:
        try:
            # widget.data['value'] is the ID (ModelChoiceIteratorValue)
            val = int(str(widget.data['value']))
            cat = allergen_cat_map.get(val, Allergen.Category.OTHER)
        except (ValueError, TypeError, AttributeError):
            cat = Allergen.Category.OTHER
            
        if cat in groups:
            groups[cat]['widgets'].append(widget)
        else:
            # Fallback for unknown categories
            if Allergen.Category.OTHER in groups:
                groups[Allergen.Category.OTHER]['widgets'].append(widget)
    
    # Remove empty groups if desired, or keep them to show headers
    # Let's keep them consistent
    return groups


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_allergen(request):
    """
    动态添加新过敏原 (AJAX/HTMX)
    """
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            from .models import Allergen
            # Check if exists (case-insensitive)
            obj, created = Allergen.objects.get_or_create(name__iexact=name, defaults={"name": name})
            if created:
                # Return the new option as HTML
                return HttpResponse(f"""
                    <div class="col-6">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="allergens" value="{obj.id}" id="id_allergens_{obj.id}" checked>
                            <label class="form-check-label" for="id_allergens_{obj.id}">
                                {obj.name}
                            </label>
                        </div>
                    </div>
                """)
            else:
                # Already exists, return nothing or error (handled by frontend)
                return HttpResponse(status=204) 
    return HttpResponse(status=400)


@login_required
@user_passes_test(lambda u: u.is_staff)
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
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu-manage")
    else:
        form = MenuItemForm()
    
    grouped_allergens = get_grouped_allergens(form)
    
    return render(request, "menu_management/form.html", {
        "form": form, 
        "title": "Add Menu Item",
        "grouped_allergens": grouped_allergens
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
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
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("menu-manage")
    else:
        form = MenuItemForm(instance=item)
    
    grouped_allergens = get_grouped_allergens(form)
        
    return render(request, "menu_management/form.html", {
        "form": form, 
        "title": "Edit Menu Item", 
        "item": item,
        "grouped_allergens": grouped_allergens
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_menu_item(request, pk):
    """
    删除菜品视图
    
    功能:
    - 删除指定 ID (pk) 的菜品
    - 处理 ProtectedError (当菜品被订单关联时)
    
    参数:
    - pk: 菜品的主键 ID
    
    返回:
    - 重定向到菜单管理列表 (menu-manage)
    """
    item = get_object_or_404(MenuItem, pk=pk)
    try:
        item.delete()
        messages.success(request, "Menu item deleted successfully.")
    except ProtectedError:
        messages.error(request, f"Cannot delete '{item.name}' because it is part of existing orders. Please mark it as unavailable instead.")
    
    return redirect("menu-manage")
