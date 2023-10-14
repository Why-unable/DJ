from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import os
import PyPDF2
import tempfile
import docx
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
            # 获取文件扩展名
            file_extension = os.path.splitext(file.name)[1].lower()

            # 判断文件扩展名
            if file_extension == '.pdf':
                # 处理 PDF 文件
                file_content = read_pdf_content(file)
                text = file_content

            elif file_extension == '.doc' or file_extension == '.docx':
                # 将 Word 文件保存到临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(file.read())
                temp_file_path = temp_file.name
                temp_file.close()  # 关闭临时文件

                file_content = read_doc_content(temp_file_path)
                text = file_content

                os.remove(temp_file_path)  # 删除临时文件

            elif file_extension == '.txt':
                file_content = file.read().decode('utf-8')
                text = file_content
            else:
                # 不支持的文件格式
                text = "不支持的文件格式：" + file.name
        else:
            text = "未选择文件"
    else:
        text = "未选择文件"
        print(text)

    context = {'text': text}
    return render(request, 'resume/analyse.html', context)


def read_pdf_content(file):
    reader = PyPDF2.PdfReader(file)
    num_pages = len(reader.pages)

    content = ""
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        page_content = page.extract_text()
        content += page_content

    return content


def read_doc_content(file_path):
    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs]
    content = "\n".join(paragraphs)
    return content