from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

# 视图函数
from .models import ResumeShow


def resume_list(request):
    # return HttpResponse("Hello World!")
    resumes = ResumeShow.objects.all()
    # 需要传递给模板（templates）的对象
    context = {'resumes': resumes}
    # render函数：载入模板，并返回context对象
    return render(request, 'resume/list.html', context)


def resume_detail(request, id):
    # 取出相应的文章
    resume = ResumeShow.objects.get(id=id)
    # 需要传递给模板的对象
    context = {'resume': resume}
    # 载入模板，并返回context对象
    return render(request, 'resume/detail.html', context)


def resume_analyse(request):
    if request.method == 'POST':
        file = request.FILES.get('file_selector')
        if file:
            # 在这里你可以对文件进行处理
            # 例如，读取文件内容
            file_content = file.read().decode('utf-8')

            # 对文件内容进行处理
            # ...
            text = "文件已处理：" + file.name
            print(text)
            print(file_content)
        else:
            text = "未选择文件"
    else:
        text = "？？？？？？未处理"
        print(text)

    context = {'text': text}
    return render(request, 'resume/analyse.html', context)
