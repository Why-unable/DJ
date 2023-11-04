import torch
from torch.utils.data import Dataset, DataLoader

# from ..models import ImprovedMLP

from resume.doc2vec.score import Score

import torch.nn as nn


class ImprovedMLP(nn.Module):
    def __init__(self, input_dim, hidden_dims, output_dim, dropout_rate):
        super(ImprovedMLP, self).__init__()

        # 添加更多的隐藏层
        self.hidden_layers = nn.ModuleList()
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            self.hidden_layers.append(nn.Linear(prev_dim, hidden_dim))
            self.hidden_layers.append(nn.ReLU())
            self.hidden_layers.append(nn.BatchNorm1d(hidden_dim))
            self.hidden_layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim

        # 输出层
        self.output_layer = nn.Linear(hidden_dims[-1], output_dim)

    def forward(self, x):
        for layer in self.hidden_layers:
            x = layer(x)
        x = self.output_layer(x)
        return x


class CustomDataset:
    def __init__(self, vectors):
        self.vectors = vectors

    def __len__(self):
        return len(self.vectors)

    def __getitem__(self, index):
        return self.vectors[index], torch.tensor(0)  # 使用0作为标签，因为在预测阶段不需要标签


class Label:
    def __init__(self):
        self.imlp=ImprovedMLP(1,[1,1],1,1)
        try:
            self.lv1_model = torch.load('resume/eval_model/1017_2037/0model_accuracy_0.728.pt')
            self.lv21_model = torch.load('resume/eval_model/1017_2037/1model_accuracy_0.725.pt')
            self.lv22_model = torch.load('resume/eval_model/1017_2037/2model_accuracy_0.681.pt')
            self.lv23_model = torch.load('resume/eval_model/1017_2037/3model_accuracy_0.750.pt')
        except Exception as e:
            print("label_init_error:", e)
        # model加载

    def get_label(self, texts):

        def get_label_lv1(texts):

            text_label_lv1 = []

            # 调用doc2vec
            sc1 = Score()
            for text in texts:
                # 获取向量表示
                # print("get_vector前一步")
                vector, simi = sc1.get_vector(text, 0)
                # print("get_vector后一步")
                # print(vector)
                # 获取标签
                if vector[0] != -1:
                    dataset = CustomDataset([vector])
                    data_loader = DataLoader(dataset, batch_size=1, shuffle=False)

                    self.lv1_model.eval()  # 将模型设置为评估模式
                    with torch.no_grad():
                        for batch in data_loader:
                            inputs, _ = batch
                            outputs = self.lv1_model(inputs)
                            predicted_labels = torch.argmax(outputs, dim=1)
                            new_text=text + "-" + str(predicted_labels.item())
                            text_label_lv1.append(new_text)
            return text_label_lv1

        def get_label_lv2(text_label_lv1):
            text_label_lv2 = []
            simis = []
            labels=[]
            sc2 = Score()
            for text in text_label_lv1:
                # 获取向量表示
                last_dash_index = text.rfind('-')
                ori_text = text[:last_dash_index]
                label_lv1= int(text[last_dash_index + 1:])
                # print("第二次get_vector前一步")
                vector, simi = sc2.get_vector(ori_text, label_lv1+1)

                # 获取标签
                if vector[0] != -1:
                    simis.append(simi)
                    dataset = CustomDataset([vector])
                    data_loader = DataLoader(dataset, batch_size=1, shuffle=False)

                    self.lv1_model.eval()  # 将模型设置为评估模式
                    # print("第二次get_vector时，开始评估的前一步")
                    with torch.no_grad():
                        for batch in data_loader:
                            inputs, _ = batch
                            outputs=0
                            if label_lv1==0:
                                outputs = self.lv21_model(inputs)
                            elif label_lv1==1:
                                outputs = self.lv22_model(inputs)
                            elif label_lv1==2:
                                outputs = self.lv23_model(inputs)
                            predicted_labels = torch.argmax(outputs, dim=1)
                            # print("Predicted Label:", predicted_labels.item())
                            new_text=text + "-" + str(predicted_labels.item())
                            text_label_lv2.append(new_text)
                            labels.append((label_lv1+1)*10+predicted_labels.item())
            return text_label_lv2, simis, labels

        # action(label)
        text_label_lv1 = get_label_lv1(texts)
        text_label_lv2 = get_label_lv2(text_label_lv1)
        return text_label_lv2


# label = Label()
