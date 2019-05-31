"""
@Coding: uft-8
@Time: 2019-05-29 15:15
@Author: Ryne Chen
@File: pyltp_sample.py
@Python Version: 3.6
"""

import os
from pyltp import Segmentor
from pyltp import SentenceSplitter
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller

# 0. 初始化路径
# ltp模型目录的路径
LTP_DATA_DIR = '../ltp_data_v3.4.0'
# 分词模型路径，模型名称为`cws.model`
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
# 词性标注模型路径，模型名称为`pos.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
# 命名实体识别模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
# 依存句法分析模型路径，模型名称为`parser.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
# 语义角色标注模型目录路径，模型目录为`srl`
srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')

# 1. 分句
sents = SentenceSplitter.split('元芳你怎么看？我就趴窗口上看呗！')
print('\n'.join(sents))

# 2. 分词
# 初始化实例
segmentor = Segmentor()
# 加载模型
segmentor.load(cws_model_path)
# 分词
words = segmentor.segment('元芳你怎么看')
print('\t'.join(words))
# 释放模型
segmentor.release()

'''
标注查询表：https://ltp.readthedocs.io/zh_CN/latest/appendix.html#id6
'''
# 3. 词性标注
# 初始化实例
postagger = Postagger()
# 加载模型
postagger.load(pos_model_path)
# 分词结果
words = ['元芳', '你', '怎么', '看']
# 词性标注
postags = postagger.postag(words)
print('\t'.join(postags))
# 释放模型
postagger.release()

# 4. 命名实体识别
# 初始化实例
recognizer = NamedEntityRecognizer()
# 加载模型
recognizer.load(ner_model_path)
words = ['元芳', '你', '怎么', '看']
postags = ['nh', 'r', 'r', 'v']
# 命名实体识别
netags = recognizer.recognize(words, postags)
print('\t'.join(netags))
# 释放模型
recognizer.release()

# 5. 依存句法分析
# 初始化实例
parser = Parser()
# 加载模型
parser.load(par_model_path)
words = ['元芳', '你', '怎么', '看']
postags = ['nh', 'r', 'r', 'v']
# 句法分析
arcs = parser.parse(words, postags)
print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
# 释放模型
parser.release()

# 6. 语义角色标注
# 初始化实例
labeller = SementicRoleLabeller()
# 加载模型
labeller.load(srl_model_path)
words = ['元芳', '你', '怎么', '看']
postags = ['nh', 'r', 'r', 'v']
# 语义角色标注
# arcs 使用依存句法分析的结果
roles = labeller.label(words, postags, arcs)
# 打印结果
for role in roles:
    print(role.index, "".join(
        ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
# 释放模型
labeller.release()
