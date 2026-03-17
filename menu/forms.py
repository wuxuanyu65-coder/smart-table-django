from django import forms
from .models import MenuItem

class MenuItemForm(forms.ModelForm):
    """
    菜品表单
    
    用于添加和编辑菜品 (MenuItem) 的表单类
    定义了使用的模型字段以及前端显示的样式部件 (widgets)
    """
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'image', 'is_available', 
                  'is_vegetarian', 'is_vegan', 'is_gluten_free', 'allergens']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegetarian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_gluten_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allergens': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
