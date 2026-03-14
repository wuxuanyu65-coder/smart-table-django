from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    """
    首页视图
    
    功能:
    - 简单的健康检查或欢迎页面
    
    返回:
    - HttpResponse: 包含 "Hello, world!" 文本
    """
    return HttpResponse("Hello, world!")
