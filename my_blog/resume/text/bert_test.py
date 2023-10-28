import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification

# 加载BERT模型的配置文件和权重
config_path = 'path/to/bert_config.json'
checkpoint_path = 'path/to/bert_model.ckpt'
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = TFBertForSequenceClassification.from_pretrained(config_path, checkpoint_path)

# 文本数据
text = "这是一段中文文本"

# 文本预处理和编码
input_ids = tokenizer.encode(text, add_special_tokens=True, truncation=True, max_length=128, padding='max_length')
input_ids = tf.constant(input_ids)[None, :]  # 添加批处理维度

# 使用BERT模型进行预测
outputs = model(input_ids)
logits = outputs.logits
predictions = tf.argmax(logits, axis=-1).numpy()[0]

# 输出分类结果
print("预测类别:", predictions)