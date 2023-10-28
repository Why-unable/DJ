# import jieba
#
#
# def tokenize(split_text, stopwords):
#
#     tokens_list = []
#     for text in split_text:
#         # 分词实现
#         words = list(jieba.cut(text))
#         # 去除停用词
#         tokens = [word for word in words if word not in stopwords]
#         tokens_list.append(tokens)
#
#     return tokens_list
