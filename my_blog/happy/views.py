from django.shortcuts import render

# Create your views here.

# 导入 HttpResponse 模块
from django.http import HttpResponse


# 视图函数
def newyear(request):
    msg = 'happy'
    if request.method == 'POST':
        msg = "happy_NewYear"

    context = {
        'test': msg
    }
    return render(request, 'happy/newyear.html', context)
