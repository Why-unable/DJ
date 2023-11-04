import re

from django.shortcuts import render

# Create your views here.
import sys
import torch.nn as nn
from . import models
# from .models import ImprovedMLP
from .eval_model.label import Label
from django.http import HttpResponse
import os
import PyPDF2
import tempfile
import docx
import pandas as pd
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
    try:
        text_label, avg_score = get_label_score(text)

    except Exception as e:
        print(e)
        text_label, avg_score = ['666', '999']

    context = {
        'text': text_label,
        'score': avg_score
    }
    return render(request, 'resume/analyse.html', context)


# ===================  两行等号内的函数为resume_analyse服务  =====================

def get_label_score(text):
    split_text = split_the_text(text)
    # 对于每一个句子，得到其分类：
    text_label, text_simi, labels = get_label(split_text)
    print(labels)
    # text_score=get_score(text_label)
    # return score_text
    # return text_label
    top_simi = []
    for i in range(len(text_simi)):
        top_simi.append(text_simi[i][0])
    total_score = [[], [], [], [], [], [], [], [], []]
    mapping_file = "resume/eval_model/weight.txt"
    # 加载映射文件并创建字典
    mapping = {}
    with open(mapping_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                label, weight = line.split(",", 1)
                mapping[int(label)] = float(weight)
    for i in range(len(top_simi)):
        ture_label = (labels[i] // 10 - 1) * 3 + labels[i] % 10
        total_score[ture_label].append(top_simi[i] * mapping[labels[i]])
    avg_score = []
    for t_score in total_score:
        if len(t_score) == 0:
            avg_score.append(0)
        else:
            avg_score.append(sum(t_score) / len(t_score))
    avg_score.append(sum(avg_score))
    return text_label, avg_score


def split_the_text(text):
    sentences = []
    temp_sentence = ""
    temp_length = 0

    for char in text:
        if char not in [' ', '\n']:
            temp_sentence += char
            temp_length += 1

        if char in ['。', '!', ';', '；']:
            if temp_length >= 16 or char in ['。', '!']:
                sentences.append(temp_sentence.strip())
                temp_sentence = ""
                temp_length = 0
        elif temp_length >= 60 and char in [',', '，']:
            sentences.append(temp_sentence.strip())
            temp_sentence = ""
            temp_length = 0

    if temp_sentence:
        sentences.append(temp_sentence.strip())
    print("split_the_text后的：")
    for i in range(len(sentences)):
        print(sentences[i])
    return sentences


def get_label(texts):
    # ...
    my_label = Label()
    text_label, text_score, labels = my_label.get_label(texts)
    text_label_name = get_label_name(text_label)
    return text_label_name, text_score, labels


def get_label_name(texts):
    mapping_file = "resume/eval_model/label.txt"
    # 加载映射文件并创建字典
    mapping = {}
    with open(mapping_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                label, word = line.split(",", 1)
                mapping[int(label)] = word

    pattern = r"(\d+)-(\d+)$"
    text_name = []
    for text in texts:
        text_ori = text[:-4]
        text_label_part = text[-4:]
        matches = re.findall(pattern, text_label_part)
        if matches:
            numbers = [int(match[0]) for match in matches] + [int(match[1]) for match in matches]
            text_ori += "-" + mapping[numbers[0]]
            text_ori += '-' + mapping[(numbers[0] + 1) * 10 + numbers[1]]
            text_name.append(text_ori)
    print("加上名字的：", text_name)
    return text_name


def get_score():
    text_score = []
    # ...
    return text_score


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

# ===================  两行等号内的函数为resume_analyse服务  =====================
