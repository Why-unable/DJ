import jieba
from gensim.models import Doc2Vec


class Score:
    def __init__(self):
        self.cans0 = [0.05, 250]
        self.cans1=[0.01, 300]
        self.cans2 = [0.01, 200]
        self.cans3=[0.01, 300]
        self.model0=Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model0.bin')
        self.model1 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model1.bin')
        self.model2 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model2.bin')
        self.model3 = Doc2Vec.load('resume/doc2vec/1017_2037/doc2vec_model3.bin')
        self.stopwords=[]
        with open('resume/doc2vec/stop_list.txt', 'r', encoding='utf-8') as file:
            for line in file:
                self.stopwords.append(line.strip())

    def tokenize(self, text):
        # 分词实现
        words = list(jieba.cut(text))
        # 去除停用词
        tokens = [word for word in words if word not in self.stopwords]
        # print('是的我是萨哈子',tokens)
        return tokens

    def get_vector(self, text, type):

        tokenize_text=self.tokenize(text)
        # print("??>>")
        if type == 0:
            return self.model0.infer_vector(tokenize_text, alpha=self.cans0[0], epochs=self.cans0[1])
        elif type == 1:
            return self.model1.infer_vector(tokenize_text, alpha=self.cans1[0], epochs=self.cans1[1])
        elif type == 2:
            return self.model2.infer_vector(tokenize_text, alpha=self.cans2[0], epochs=self.cans2[1])
        elif type == 3:
            return self.model3.infer_vector(tokenize_text, alpha=self.cans3[0], epochs=self.cans3[1])

    def get_simi(self, vector, type):
        if type == 0:
            most_similar_docs = self.model0.docvecs.most_similar([vector], topn=6)
        elif type==1:
            most_similar_docs = self.model1.docvecs.most_similar([vector], topn=6)
        elif type==2:
            most_similar_docs = self.model2.docvecs.most_similar([vector], topn=6)
        elif type==3:
            most_similar_docs = self.model3.docvecs.most_similar([vector], topn=6)
        return most_similar_docs


