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
        try:
            file = request.FILES.get('file_selector')
        except Exception as e:
            context = {
                'text': '文件格式问题',
                'score': '文件格式问题',
            }
            return render(request, 'resume/analyse.html', context)
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
        text_label, avg_score, comment = get_label_score_version3(text)
    except Exception as e:
        text_label = ['something wrong']
        avg_score = ['something wrong']
        comment = ['something wrong']
        print(e)

    label = ['战略思维', '创造性思维', '逻辑思维', '行动力', '领导力', '沟通能力', '道德与责任', '社交导向', '抗挫力']
    label_comment = zip(label, comment)
    context = {
        'text': text_label,
        'score': avg_score,
        'label_comment': label_comment
    }
    return render(request, 'resume/analyse.html', context)


# ===================  两行等号内的函数为resume_analyse服务  =====================

def get_label_score_origin(text):
    split_text = split_the_text(text)
    # 对于每一个句子，得到其分类：
    text_label, text_simi, labels = get_label(split_text)
    print(labels)
    # 获取各个句子的相似度
    top_simi = []
    for i in range(len(text_simi)):
        # 对于每个句子返回的相似度数组，取最高，也就是[0]的位置
        top_simi.append(text_simi[i][0])

    # 各个类别中，同一类别的各个句子的最高相似度的集合被放在total_score的一个位置
    total_score = [[], [], [], [], [], [], [], [], []]

    # 加载映射文件并创建字典
    mapping_file = "resume/eval_model/weight.txt"
    mapping = {}
    with open(mapping_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                # 标签与权重的对应关系
                label, weight = line.split(",", 1)
                mapping[int(label)] = float(weight)
    for i in range(len(top_simi)):
        true_label = (labels[i] // 10 - 1) * 3 + labels[i] % 10
        total_score[true_label].append(top_simi[i] * mapping[labels[i]])

    # 求每个类别的前三平均
    avg_score = []
    avg_score2 = []
    for t_score in total_score:
        if len(t_score) == 0 or sum(t_score) / len(t_score) < 6:
            avg_score.append(6)
        else:
            if len(t_score) <= 3:
                avg_score.append(sum(t_score) / len(t_score))
            else:
                print("good")
                t_score.sort(reverse=True)
                sum_score = (t_score[0] + t_score[1] + t_score[2]) / 3
                avg_score.append(sum_score)

        # 上述是总分显示
        # 下述是各分
        if len(t_score) == 0 or sum(t_score) / len(t_score) < 6:
            avg_score2.append(6)
        else:
            if len(t_score) < 3:
                bi = 0
                if len(t_score) == 2:
                    bi = 0.95
                elif len(t_score) == 1:
                    bi = 0.88
                avg_score2.append(sum(t_score) * bi / len(t_score))
            else:
                t_score.sort(reverse=True)
                sum_score = (t_score[0] + t_score[1] + t_score[2]) / 3
                if t_score[0] - t_score[1] > 0.5:
                    sum_score += (t_score[0] - t_score[1]) * 0.3
                if t_score[0] - t_score[2] > 1:
                    sum_score += (t_score[0] - t_score[2]) * 0.3
                if sum_score > (t_score[0] * 3):
                    sum_score = t_score[0] - 0.3
                avg_score2.append(sum_score)

    avg_score = [round(ascore, 2) for ascore in avg_score]
    avg_score2 = [round(ascore2, 2) for ascore2 in avg_score2]

    label = ['战略思维', '创造性思维', '逻辑思维', '行动力', '领导力', '沟通能力', '道德与责任', '社交导向', '抗挫力']
    weight = [10.99, 11.85, 11.92, 11.14, 10.94, 11.84, 11.19, 9.52, 10.61]
    comment = ['优秀', '良好', '合格']
    label_cmt = []
    label_score = []
    print(len(avg_score))
    label_comment_cmt = []
    for i in range(len(avg_score2)):
        bili = avg_score2[i] / weight[i]
        if bili >= 0.9:
            label_cmt.append(label[i] + ": " + comment[0])
            label_comment_cmt.append(comment[0])
        elif bili >= 0.8:
            label_cmt.append(label[i] + ": " + comment[1])
            label_comment_cmt.append(comment[1])
        else:
            # 各
            if 0.65 <= bili <= 0.75:
                avg_score2[i] *= (1.06 * (1 + (0.75 - bili)))
            elif 0.6 < bili < 0.65:
                avg_score2[i] *= 1.2
            elif bili < 0.6:
                avg_score2[i] = 6.65
            # 总
            avg_score[i] *= 1.1

            label_cmt.append(label[i] + ": " + comment[2])
            label_comment_cmt.append(comment[2])
        # 可以再乘一个比例因子使得分数高点
        if avg_score2[i] / weight[i] < 0.6:
            label_score.append(label[i] + ": " + str(6.65) + "/" + str(10))
        else:
            label_score.append(label[i] + ": " + str(round(avg_score2[i] / weight[i] * 10, 2)) + "/" + str(10))
    label_score.append('总计：' + str(round(sum(avg_score) * 100 / 90, 2)) + "/" + str(100) + "  (转为百分制)")

    detail_comment = get_comment(label_comment_cmt)
    return label_score, label_cmt, detail_comment


def get_label_score_old(text):
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
        if len(t_score) == 0 or sum(t_score) / len(t_score) < 6:
            avg_score.append(6)
        else:
            if len(t_score) <= 3:
                avg_score.append(sum(t_score) / len(t_score))
            else:
                t_score.sort(reverse=True)
                sum_score = (t_score[0] + t_score[1] + t_score[2]) / 3
                avg_score.append(sum_score)
    avg_score = [round(ascore, 2) for ascore in avg_score]
    # 针对软实力而非硬实力
    # 指标的由来：基于胜任力模型构建、以往文献，分层
    # 针对商科、该领域
    # 研究意义、创新点
    label = ['战略思维', '创造性思维', '逻辑思维', '行动力', '领导力', '沟通能力', '道德与责任', '社交导向', '抗挫力']
    weight = [10.99, 11.85, 11.92, 11.14, 10.94, 11.84, 11.19, 9.52, 10.61]
    comment = ['优秀', '良好', '合格']
    label_cmt = []
    label_score = []
    print(len(avg_score))

    for i in range(len(avg_score)):
        bili = avg_score[i] / weight[i]
        if bili >= 0.9:
            label_cmt.append(label[i] + ": " + comment[0])
        elif bili >= 0.8:
            label_cmt.append(label[i] + ": " + comment[1])
        else:
            avg_score[i] *= 1.16
            label_cmt.append(label[i] + ": " + comment[2])
        # 可以再乘一个比例因子使得分数高点
        if avg_score[i] / weight[i] < 0.6:
            label_score.append(label[i] + ": " + str(6) + "/" + str(10))
        else:
            label_score.append(label[i] + ": " + str(round(avg_score[i] / weight[i] * 10, 2)) + "/" + str(10))
    label_score.append('总计：' + str(round(sum(avg_score) * 100 / 90, 2)) + "/" + str(100) + "  (转为百分制)")
    return label_score, label_cmt


def get_comment(comment):
    mapping_comment_file = "resume/eval_model/comment.csv"
    mapping_comment = pd.read_csv(mapping_comment_file)
    cmt = []
    print(len(comment))
    try:

        for i in range(len(comment)):
            mapping_i = i * 3
            for offset in range(3):
                if comment[i] == mapping_comment['等级'][mapping_i + offset]:
                    cmt.append(mapping_comment['评语'][mapping_i + offset])
    except Exception as e:
        print("when get comment")
        print(e)
    print(cmt)
    print(len(cmt))
    return cmt


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
    print('04th:')
    print(total_score[0], total_score[4])
    print(sum(total_score[4]))
    for t_score in total_score:

        if len(t_score) == 0 or sum(t_score) / len(t_score) < 6:
            avg_score.append(6)
        else:
            if len(t_score) < 3:
                bi = 0
                if len(t_score) == 2:
                    bi = 0.95
                elif len(t_score) == 1:
                    bi = 0.88
                avg_score.append(sum(t_score) * bi / len(t_score))
            else:
                t_score.sort(reverse=True)
                sum_score = (t_score[0] + t_score[1] + t_score[2]) / 3
                if t_score[0] - t_score[1] > 0.5:
                    sum_score += (t_score[0] - t_score[1]) * 0.3
                if t_score[0] - t_score[2] > 1:
                    sum_score += (t_score[0] - t_score[2]) * 0.5
                if sum_score > t_score[0] * 3:
                    sum_score = t_score[0] - 0.3
                avg_score.append(sum_score)
    print(avg_score)
    avg_score = [round(ascore, 2) for ascore in avg_score]
    # 针对软实力而非硬实力
    # 指标的由来：基于胜任力模型构建、以往文献，分层
    # 针对商科、该领域
    # 研究意义、创新点
    label = ['战略思维', '创造性思维', '逻辑思维', '行动力', '领导力', '沟通能力', '道德与责任', '社交导向', '抗挫力']
    weight = [10.99, 11.85, 11.92, 11.14, 10.94, 11.84, 11.19, 9.52, 10.61]
    comment = ['优秀', '良好', '合格']
    label_cmt = []
    label_score = []
    print(len(avg_score))

    for i in range(len(avg_score)):
        bili = avg_score[i] / weight[i]
        if bili >= 0.9:
            label_cmt.append(label[i] + ": " + comment[0])
        elif bili >= 0.8:
            label_cmt.append(label[i] + ": " + comment[1])
        else:
            if 0.65 <= bili <= 0.75:
                avg_score[i] *= (1.06 * (1 + (0.75 - bili)))
            elif bili < 0.65:
                avg_score[i] *= 1.2
            label_cmt.append(label[i] + ": " + comment[2])
        # 可以再乘一个比例因子使得分数高点
        if avg_score[i] / weight[i] < 0.6:
            avg_score[i] = 6.6
            label_score.append(label[i] + ": " + str(6.6) + "/" + str(10))
        else:
            if avg_score[i] / weight[i] >= 1:
                avg_score[i] = weight[i] - 0.3
            label_score.append(label[i] + ": " + str(round(avg_score[i] / weight[i] * 10, 2)) + "/" + str(10))
    print(avg_score)
    print(sum(avg_score))
    label_score.append('总计：' + str(round(sum(avg_score), 2)) + "/" + str(100) + "  (转为百分制)")
    return label_score, label_cmt


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


def get_label_score_version3(text):
    split_text = split_the_text(text)
    # 对于每一个句子，得到其分类：
    text_label, text_simi, labels = get_label(split_text)
    print(labels)
    # 获取各个句子的相似度
    top_simi = []
    for i in range(len(text_simi)):
        # 对于每个句子返回的相似度数组，取最高，也就是[0]的位置
        top_simi.append(text_simi[i][0])

    # 各个类别中，同一类别的各个句子的最高相似度的集合被放在total_score的一个位置
    total_score = [[], [], [], [], [], [], [], [], []]

    # 加载映射文件并创建字典
    mapping_file = "resume/eval_model/weight.txt"
    mapping = {}
    with open(mapping_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                # 标签与权重的对应关系
                label, weight = line.split(",", 1)
                mapping[int(label)] = float(weight)
    for i in range(len(top_simi)):
        true_label = (labels[i] // 10 - 1) * 3 + labels[i] % 10
        total_score[true_label].append(top_simi[i] * mapping[labels[i]])

    # 求每个类别的前三平均
    avg_score = []
    avg_score2 = []
    for t_score in total_score:
        if len(t_score) == 0 or sum(t_score) / len(t_score) < 6:
            avg_score.append(6)
        else:
            if len(t_score) <= 3:
                avg_score.append(sum(t_score) / len(t_score))
            else:
                print("good")
                t_score.sort(reverse=True)
                sum_score = (t_score[0] + t_score[1] + t_score[2]) / 3
                avg_score.append(sum_score)

        # 上述是总分显示
        # 下述是各分
        if len(t_score) == 0 or sum(t_score) / len(t_score) < 6:
            avg_score2.append(6)
        else:
            if len(t_score) < 3:
                bi = 0
                if len(t_score) == 2:
                    bi = 0.95
                elif len(t_score) == 1:
                    bi = 0.88
                avg_score2.append(sum(t_score) * bi / len(t_score))
            else:
                t_score.sort(reverse=True)
                sum_score = (t_score[0] + t_score[1] + t_score[2]) / 3
                if t_score[0] - t_score[1] > 0.5:
                    sum_score += (t_score[0] - t_score[1]) * 0.3
                if t_score[0] - t_score[2] > 1:
                    sum_score += (t_score[0] - t_score[2]) * 0.3
                if sum_score > (t_score[0] * 3):
                    sum_score = t_score[0] - 0.3
                avg_score2.append(sum_score)

    avg_score = [round(ascore, 2) for ascore in avg_score]
    avg_score2 = [round(ascore2, 2) for ascore2 in avg_score2]

    label = ['战略思维', '创造性思维', '逻辑思维', '行动力', '领导力', '沟通能力', '道德与责任', '社交导向', '抗挫力']
    weight = [10.99, 11.85, 11.92, 11.14, 10.94, 11.84, 11.19, 9.52, 10.61]
    comment = ['优秀', '良好', '合格']
    label_cmt = []
    label_score = []
    print(len(avg_score))
    label_comment_cmt = []
    for i in range(len(avg_score2)):
        bili = avg_score2[i] / weight[i]
        if bili >= 0.9:
            label_cmt.append(label[i] + ": " + comment[0])
            label_comment_cmt.append(comment[0])
        elif bili >= 0.8:
            label_cmt.append(label[i] + ": " + comment[1])
            label_comment_cmt.append(comment[1])
        else:
            # 各
            if 0.65 <= bili <= 0.75:
                avg_score2[i] *= (1.06 * (1 + (0.75 - bili)))
            elif 0.6 < bili < 0.65:
                avg_score2[i] *= 1.2
            elif bili < 0.6:
                avg_score2[i] = 6.65
            # 总
        if avg_score[i] / weight[i] < 0.8:
            avg_score[i] *= 1.125

            label_cmt.append(label[i] + ": " + comment[2])
            label_comment_cmt.append(comment[2])
        # 可以再乘一个比例因子使得分数高点
        if avg_score2[i] / weight[i] < 0.6:
            label_score.append(label[i] + ": " + str(6.65) + "/" + str(10))
        else:
            label_score.append(label[i] + ": " + str(round(avg_score2[i] / weight[i] * 10, 2)) + "/" + str(10))
    label_score.append('总计：' + str(round(sum(avg_score) * 100 / 90, 2)) + "/" + str(100) + "  (转为百分制)")

    detail_comment = get_comment(label_comment_cmt)
    return label_score, label_cmt, detail_comment

# ===================  两行等号内的函数为resume_analyse服务  =====================
