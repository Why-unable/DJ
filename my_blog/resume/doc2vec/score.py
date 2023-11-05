import jieba
from gensim.models import Doc2Vec
import pandas as pd


class Score:
    def __init__(self):
        # self.cans0 = [0.05, 250]
        # self.cans1 = [0.01, 300]
        # self.cans2 = [0.01, 200]
        # self.cans3 = [0.01, 300]
        self.cans0 = [0.1, 100]
        self.cans1 = self.cans0
        self.cans2 = self.cans0
        self.cans3 = self.cans0
        # self.model0 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model0.bin')
        # self.model1 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model1.bin')
        # self.model2 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model2.bin')
        # self.model3 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model3.bin')

        self.model0 = Doc2Vec.load('resume/doc2vec/1104_2256/doc2vec_model1104.bin')
        self.model1 = self.model0
        self.model2 = self.model0
        self.model3 = self.model0
        self.stopwords = []
        with open('resume/doc2vec/stop_list.txt', 'r', encoding='utf-8') as file:
            for line in file:
                self.stopwords.append(line.strip())

    def tokenize(self, text):
        # 分词实现
        words = list(jieba.cut(text))
        # 去除停用词
        tokens = [word for word in words if word not in self.stopwords]
        return tokens

    def get_most_simi(self, vector, type):
        train_file = ''
        have = False
        simi = []
        if type == 0:
            train_file = 'resume/doc2vec/sentences/1003data/train.csv'
            train_data = pd.read_csv(train_file)
            most_similar_docs = self.model0.docvecs.most_similar([vector], topn=6)
            for doc_id, similarity in most_similar_docs:
                # print(train_data['text'][doc_id])
                # print("Similarity:", similarity)
                simi.append(similarity)
                if similarity > 0.45 and doc_id < 1904:
                    have = True

        elif type == 1:
            train_file = 'resume/doc2vec/sentences/1013data1/total/train.csv'
            train_data = pd.read_csv(train_file)
            most_similar_docs = self.model1.docvecs.most_similar([vector], topn=6)
            for doc_id, similarity in most_similar_docs:
                simi.append(similarity)
                if similarity > 0.5:
                    have = True
                # else :
                #     print(1,similarity)
        elif type == 2:
            train_file = 'resume/doc2vec/sentences/1013data2/total/train.csv'
            train_data = pd.read_csv(train_file)
            most_similar_docs = self.model2.docvecs.most_similar([vector], topn=6)
            for doc_id, similarity in most_similar_docs:
                simi.append(similarity)
                if similarity > 0.5:
                    have = True
                # else :
                #     print(2,similarity)
        elif type == 3:
            train_file = 'resume/doc2vec/sentences/1013data3/total/train.csv'
            train_data = pd.read_csv(train_file)
            most_similar_docs = self.model3.docvecs.most_similar([vector], topn=6)
            for doc_id, similarity in most_similar_docs:
                simi.append(similarity)
                if similarity > 0.5:
                    have = True
                # else :
                #     print(3,similarity)

        if not have:
            return have, [0, 0]
        else:
            return have, simi

    def get_vector(self, text, type):

        try:
            tokenize_text = self.tokenize(text)
            if type == 0:
                vector = self.model0.infer_vector(tokenize_text, alpha=self.cans0[0], epochs=self.cans0[1])
                have, simi = self.get_most_simi(vector, type)
                if have:
                    return vector, simi

            elif type == 1:
                vector = self.model1.infer_vector(tokenize_text, alpha=self.cans1[0], epochs=self.cans1[1])
                have, simi = self.get_most_simi(vector, type)
                if have:
                    return vector, simi

            elif type == 2:
                vector = self.model2.infer_vector(tokenize_text, alpha=self.cans2[0], epochs=self.cans2[1])
                have, simi = self.get_most_simi(vector, type)
                if have:
                    return vector, simi

            elif type == 3:
                vector = self.model3.infer_vector(tokenize_text, alpha=self.cans3[0], epochs=self.cans3[1])
                have, simi = self.get_most_simi(vector, type)
                if have:
                    return vector, simi

            return [-1, -1], 0

        except Exception as e:
            print("get_vector:", e)

    def get_simi(self, vector, type):

        if type == 0:
            most_similar_docs = self.model0.docvecs.most_similar([vector], topn=6)
        elif type == 1:
            most_similar_docs = self.model1.docvecs.most_similar([vector], topn=6)
        elif type == 2:
            most_similar_docs = self.model2.docvecs.most_similar([vector], topn=6)
        elif type == 3:
            most_similar_docs = self.model3.docvecs.most_similar([vector], topn=6)
        return most_similar_docs
