"""
@Coding: uft-8
@Time: 2019-05-29 18:10
@Author: Ryne Chen
@File: try_pyltp.py 
@Python Verson: 3.6
"""

import os
from pyltp import Segmentor
from pyltp import SentenceSplitter
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
import jieba
from pyltp import SementicRoleLabeller
from collections import defaultdict

# 初始化路径
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

s = '''
美国贸易代表莱特希泽星期五表示，他已收到总统特朗普的指示，对其余尚未加征关税的所有中国商品加征关税，星期一将公布细节。
此后特朗普发推特呼吁中国现在就采取行动(向美方让步)。
关于中美下一步何时磋商，美财政部长姆努钦对媒体回应说：“目前还没有这方面的安排。”
美方是挑起贸易战的一方，自恃实力强大，相信它的关税大棒足以压垮中国。
中方的回应则是太极哲学的示范版，坚守原则，不主动打也不惧战，用更大的承受力瓦解对方的攻击力，增加其他情况出现的可能性。
美方攻势猛烈，但这种攻势在经济学上充满了非理性，对美国经济将导致常识性的自伤。
美方显然寄希望于人类贸易史上从未有过的凶猛关税战可以一举摧毁中国的意志，以短时间内的损失换取中国接受不平等协议，铸就美国现政府的“辉煌大业”。
美国的做法是赌博。
美方不断发声，一个动作接一个动作，表现出的其实是他们急切希望这一切迅速生效的焦虑。

'''


# 加载文本
def load_text(text_path):
    """
    :param text_path: 文本路径
    :return: 文本内容，type=string
    """
    sentence = ''
    with open(text_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.strip():
                sentence += line.strip()
    return sentence


# 分句
def sentence_splitter(sentences):
    """
    :param sentences: 文本内容，type=string
    :return: 句子列表
    """
    sents = SentenceSplitter.split(sentences)

    sents_list = list(sents)

    return sents_list


# 分词1: ltp
def cut_words_ltp(sentence):
    segmentor = Segmentor()
    segmentor.load(cws_model_path)
    words = segmentor.segment(sentence)
    segmentor.release()
    return list(words)


# 分词2: jieba
def cut_words_jieba(sentence):
    words = jieba.cut(sentence)
    return list(words)


# 词性标注
def get_postags(words):
    postagger = Postagger()
    postagger.load(pos_model_path)
    postags = postagger.postag(words)
    postagger.release()
    return list(postags)


# 命名实体识别
def get_ner(words, postags):
    recognizer = NamedEntityRecognizer()
    recognizer.load(ner_model_path)
    netags = recognizer.recognize(words, postags)
    # for word, ntag in zip(words, tags):
    #     print(word + '/' + ntag)
    recognizer.release()
    return list(netags)


# 依存句法分析
def get_parsing(words, postags):
    parser = Parser()
    parser.load(par_model_path)
    arcs = parser.parse(words, postags)
    parser.release()
    return [(arc.head, arc.relation) for arc in arcs]


# 加载"说"的相关词
def load_saying_words(saying_words_path):
    saying_list = []
    with open(saying_words_path, 'r') as f:
        for line in f.readlines():
            if line.strip():
                saying_list.append(line.strip())
    # print(saying_list)
    # print(len(saying_list))
    return saying_list


# 匹配句子中的"说"
def match_saying_words(words, saying_list):
    match = []
    for index, word in enumerate(words):
        if word in saying_list:
            match.append((word, index))
    return match


# 提取单个句子
def extract_single_sentence(saying_list, sentence):
    opinions = defaultdict(str)

    words = cut_words_ltp(sentence)

    match_words = match_saying_words(words, saying_list)

    if match_words:
        print(words)
        print(match_words)
        # 获取词性标注
        postags = get_postags(words)
        # print(postags)
        # 获取ner
        netags = get_ner(words, postags)
        print(netags)
        # 获取依存分析
        arcs = get_parsing(words, postags)
        print(arcs)

        names = get_name(words, netags)

        for name, position in names.items():
            # print(name, position)
            start = position[0]
            end = position[1]

            for w in match_words:
                saying_index = w[1]

                head = arcs[saying_index][0]
                relation = arcs[saying_index][1]

                if head == start and relation == 'HED':
                    # print(saying_index)
                    opinion = ''.join(words[saying_index + 2:])
                    opinions[name] = opinion

        return opinions


# 获取人名
def get_name(words, netags):
    names = defaultdict(tuple)
    for start_index, ner in enumerate(netags):
        if ner == 'S-Nh':
            name = words[start_index]
            names[name] = (start_index, start_index)

        if ner == 'B-Nh':
            end_netags = netags[start_index:]
            end_index = start_index + end_netags.index('E-Nh')
            name = ''.join(words[start_index: end_index + 1])
            names[name] = (start_index, end_index)

        if ner == 'S-Ni':
            name = words[start_index]
            names[name] = (start_index, start_index)

        if ner == 'B-Ni':
            end_netags = netags[start_index:]
            end_index = start_index + end_netags.index('E-Ni')
            name = ''.join(words[start_index: end_index + 1])
            names[name] = (start_index, end_index)

        # if ner == 'S-Ns':
        #     name = words[start_index]
        #     names[name] = (start_index, start_index)

    return names


saying_words_path = 'saying_verbs_cleaned.txt'
saying_list = load_saying_words(saying_words_path)

text_path = 'test_chinese_news.txt'
sentences = load_text(text_path)

sents_list = sentence_splitter(sentences)
# print(sents_list)


# l = """
# 博索纳罗还表示，“我一直说，公共安全从家里开始的。”
# """
# print(l)

for sent in sents_list:
    print(sent)
    opinions = extract_single_sentence(saying_list, sent)
    if opinions:
        for name, op in opinions.items():
            print("人物：{}\n言论：{}".format(name, op))
    print('*' * 80)
#
# for sent in sents_list:
#     extract_single_sentence(saying_list, sent)

#     words = cut_words_ltp(sent)
#     # words = cut_words_jieba(sent)
#     print(words)
#     postags = get_postags(words)
#     print(postags)
#     netags = get_ner(words, postags)
#     print(netags)
#     arcs = get_parsing(words, postags)
#     # arc.head 表示依存弧的父节点词的索引，arc.relation 表示依存弧的关系
#     print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
#     print('*' * 40)
