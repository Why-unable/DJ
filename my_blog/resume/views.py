from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import os
import PyPDF2
import tempfile
import docx
# 视图函数
from django.utils.html import linebreaks

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

    text_score = get_label_score(text)
    # print(text_score)
    context = {'text': text_score}
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


def get_label_score(text):
    split_text = split_the_text(text)
    # 对于每一个句子，得到其分类：
    # text_label=get_label(every_text)
    # text_score=get_score(text_label)
    # return score_text
    return split_text


def split_the_text(text):
    sentences = []
    temp_sentence = ""
    temp_length = 0

    for char in text:
        temp_sentence += char
        temp_length += 1

        if char in ['。', '；', ';']:
            sentences.append(temp_sentence.strip())
            temp_sentence = ""
            temp_length = 0
        elif temp_length >= 30 and '，' in temp_sentence:
            parts = temp_sentence.split('，', 1)
            sentences.append(parts[0].strip())
            temp_sentence = parts[1].strip()
            temp_length = len(temp_sentence)

    if temp_sentence:
        sentences.append(temp_sentence.strip())

    return sentences


def get_label():
    text_label = []
    # ...

    return text_label


def get_score():
    text_score = []
    # ...
    return text_score
