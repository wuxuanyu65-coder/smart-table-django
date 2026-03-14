from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm

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
