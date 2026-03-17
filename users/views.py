from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
import json

class SignUpView(CreateView):
    """
    用户注册视图
    
    功能:
    - 展示用户注册表单
    - 处理新用户创建逻辑
    
    属性:
    - template_name: 使用的模板文件 (users/signup.html)
    - form_class: 使用的表单类 (CustomUserCreationForm)
    - success_url: 注册成功后的重定向 URL (登录页)
    """
    template_name = "users/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")


@login_required
def profile_view(request):
    """
    用户个人中心视图
    
    功能:
    - 展示用户信息
    - 更新过敏原设置 (ManyToMany)
    """
    from menu.models import Allergen
    all_allergens = Allergen.objects.all()

    if request.method == "POST":
        selected_ids = request.POST.getlist("allergens")
        # Clear existing and add selected
        request.user.allergens.clear()
        if selected_ids:
            request.user.allergens.add(*selected_ids)
        return redirect("profile")
        
    user_allergens = request.user.allergens.all()
    
    return render(request, "users/profile.html", {
        "all_allergens": all_allergens,
        "user_allergens": user_allergens
    })
