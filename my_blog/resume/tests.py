'''
from django.test import TestCase

# Create your tests here.

from doc2vec import *
from eval_model.eval_MLP import ImprovedMLP
from eval_model.label import Label

lb = Label()
# , '协助开展活动，布置会场，筹备工作', '捍卫公司/员工的底线要求，温和坚定地解决问题', '善于 PS 后期处理'
test = ['负责预算管理制度和预算编制指引文档的编写和宣贯','骗你的我是傻子','善于 PS 后期处理']
test3x=['有责任心','重视团队协作','皮实，不玻璃心','能够在快节奏、充满活力，结果导向的环境中工作','积极响应客户要求','树立良好的企业形象','综合素质扎实、乐观外向','抗压和适应能力强']
print(lb.get_label(test3x))


有责任心, 0
重视团队协作, 0
皮实，不玻璃心, 2
能够在快节奏、充满活力，结果导向的环境中工作, 2
积极响应客户要求, 0
树立良好的企业形象, 0
综合素质扎实、乐观外向, 1
抗压和适应能力强, 2
'''

# import re
#
# # 输入字符串
# my_string = "abc-5-7"
# text = "abcdf"
# text_ori = text[:-4]
# text_label=text[-4:]
# print(text_ori,text_label)
# # 使用正则表达式提取末尾的两个数字
# pattern = r"(\d+)-(\d+)$"
# matches = re.findall(pattern, my_string)
#
# # 输出提取到的两个数字
# if matches:
#     numbers = [int(match[0]) for match in matches] + [int(match[1]) for match in matches]
#     print("提取到的数字:", numbers)
# else:
#     print("未找到匹配的数字")


total_score = [[], [], [], [], [], [], [], []]
total_score[1].append(1)
avg_score=[]
for t_score in total_score:
    if len(t_score)==0:
        avg_score.append(0)
    else:
        avg_score.append(sum(t_score)/len(t_score))
print(total_score,len(total_score[1]))
print(avg_score)
