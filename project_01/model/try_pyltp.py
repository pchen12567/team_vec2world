"""
@Coding: uft-8
@Time: 2019-05-29 18:10
@Author: Ryne Chen
@File: try_pyltp.py 
@Python Version: 3.6
"""

import os
from pyltp import Segmentor
from pyltp import SentenceSplitter
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
import jieba
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


# 加载测试用文本
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
    sents_list = []
    sents = SentenceSplitter.split(sentences)

    for sent in sents:
        if sent.strip():
            clean_sent = sent.strip().replace(u'\u3000', u' ').replace(u'\xa0', u' ')
            sents_list.append(clean_sent)
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
def match_saying_words(words, saying_list, postags):
    match = []
    for index, word in enumerate(words):
        # 根据词性标注筛选出动词"说"
        if word in saying_list and postags[index] == 'v':
            match.append((word, index))
    return match


# 提取全文的人名和组织名
def get_total_names(sents_list):
    # 初始化人名字典
    total_names = defaultdict(list)

    for sentence in sents_list:
        # 分词
        words = cut_words_ltp(sentence)
        # 词性标注
        postags = get_postags(words)
        # NER
        netags = get_ner(words, postags)

        for start_index, ner in enumerate(netags):
            # 单个词构成的人名
            if ner == 'S-Nh':
                name = words[start_index]
                name_seg = [name]
                total_names[name] = name_seg

            # 多个词构成的人名
            if ner == 'B-Nh':
                end_netags = netags[start_index:]
                end_index = start_index + end_netags.index('E-Nh')
                name = ''.join(words[start_index: end_index + 1])
                name_seg = words[start_index: end_index + 1]
                total_names[name] = name_seg

            # 单个词构成的组织名
            if ner == 'S-Ni':
                name = words[start_index]
                name_seg = [name]
                total_names[name] = name_seg

            # 多个词构成的组织名
            if ner == 'B-Ni':
                end_netags = netags[start_index:]
                end_index = start_index + end_netags.index('E-Ni')
                name = ''.join(words[start_index: end_index + 1])
                name_seg = words[start_index: end_index + 1]
                total_names[name] = name_seg

            # 单个词构成的地名
            # if ner == 'S-Ns':
            #     name = words[start_index]
            #     name_seg = [name]
            #     total_names[name] = name_seg
            #
            # 多个词构成的地名
            # if ner == 'B-Ns':
            #     end_netags = netags[start_index:]
            #     end_index = start_index + end_netags.index('E-Ns')
            #     name = ''.join(words[start_index: end_index + 1])
            #     name_seg = words[start_index: end_index + 1]
            #     total_names[name] = name_seg

    # 返回人名字典，key=人名string，value=人名片段list
    return total_names


# # 获取单句的人名和组织名
# def get_names_with_position(words, netags):
#     names_with_position = []
#
#     for start_index, ner in enumerate(netags):
#         # 单个词构成的人名
#         if ner == 'S-Nh':
#             name = words[start_index]
#             position = (start_index, start_index)
#             names_with_position.append((name, position))
#
#         # 多个词构成的人名
#         if ner == 'B-Nh':
#             end_netags = netags[start_index:]
#             end_index = start_index + end_netags.index('E-Nh')
#             name = ''.join(words[start_index: end_index + 1])
#             position = (start_index, end_index)
#             names_with_position.append((name, position))
#
#         # 单个词构成的组织名
#         if ner == 'S-Ni':
#             name = words[start_index]
#             position = (start_index, start_index)
#             names_with_position.append((name, position))
#
#         # 多个词构成的组织名
#         if ner == 'B-Ni':
#             end_netags = netags[start_index:]
#             end_index = start_index + end_netags.index('E-Ni')
#             name = ''.join(words[start_index: end_index + 1])
#             position = (start_index, end_index)
#             names_with_position.append((name, position))
#
#     return names_with_position


# 优化单句中人名提取函数，可以减少通过NER提取人名失败的情况
# 获取单句的人名和组织名
def get_names_with_position(sentence, words, total_names):
    # 初始化返回列表
    names_with_position = []

    # 遍历全文的人名
    for name, name_seg in total_names.items():
        # 当前句包含人名
        if name in sentence:
            # 单个词构成的人名
            if len(name_seg) == 1:
                # 遍历当前句
                for index, w in enumerate(words):
                    # 提取所有单词构成的人名及其位置
                    if w == name:
                        position = (index, index)
                        names_with_position.append((name, position))

            # 多个词构成的人名
            if len(name_seg) > 1:
                # 遍历当前句
                for start_index, w in enumerate(words):
                    # 提取所有多词构成的人名及其位置
                    if w == name_seg[0]:
                        end_index = start_index + len(name_seg) - 1
                        position = (start_index, end_index)
                        names_with_position.append((name, position))

    # 返回人名和位置结果列表，元素为元组(name, (start_index, end_index))
    return names_with_position


# 获取言论
def get_opinions(words, match_words, names_with_position, arcs):
    # 初始化返回列表
    opinions = []

    # 第一步，根据句子中的人名获取对应言论
    # 遍历句子中的所有人名
    for (name, position) in names_with_position:
        # 获得人名的位置
        start_index = position[0]
        end_index = position[1]

        # 通过人名的 arc.relation = 'SBV' 找言论
        if arcs[end_index][1] == 'SBV':
            # 获取言论初始位置，假设为 SBV 指向的 head 位置
            opinion_index = arcs[end_index][0]

            # 判断言论初始位置是否为标点符号或 arc.relation = 'RAD'
            # 如果是，则其位置往下顺延一位
            if arcs[opinion_index][1] == 'WP' or 'RAD':
                opinion_index += 1

            # 获取完整言论并保存
            opinion = ''.join(words[opinion_index:])
            opinions.append((name, opinion))

            # 获取当前言论的"说"
            # 获取"说"的位置，假设在人名末尾后一位
            saying_index = end_index + 1
            # 获取"说"
            saying = words[saying_index]

            # 将获取的"说"及其位置在"说"的列表中进行匹配
            if (saying, saying_index) in match_words:
                # 将匹配成功的"说"从列表中移除，避免二次匹配
                match_words.remove((saying, saying_index))

    # 第二步，根据句子中的"说"来找对应人名和言论
    # 遍历所有的"说"
    for (saying, position) in match_words:
        # 获取"说"的主体位置
        head_index = arcs[position][0]
        # 获取"说"的 arc.relation
        saying_relation = arcs[position][1]

        # 当"说"的 arc.relation = 'COO' 并且其 arc.head 指向的位置为自身时
        if saying_relation == 'COO' and head_index == position:
            # 获取新的"说"的位置，假设为当前"说"的前一位
            new_saying_index = head_index - 1

            # 获取新"说"的 arc.head 指向位置
            new_head_index = arcs[new_saying_index][0]
            # 获取新"说"的 arc.relation
            new_saying_relation = arcs[new_saying_index][1]

            # 获取言论的初始位置，假设为当前"说"的下一位
            opinion_index = position + 1

            # 判断言论的起始位置是否为标点符号
            # 如果是，则其位置往下顺延一位
            if arcs[opinion_index][1] == 'WP':
                opinion_index += 1

            # 获取完整言论
            opinion = ''.join(words[opinion_index:])

            # 根据 VOB 找到人名
            if new_saying_relation == 'VOB':
                name = words[new_head_index]

                # 保存人名及其言论
                opinions.append((name, opinion))

        # 当"说"的 arc.relation = 'VOB' 时
        if saying_relation == 'VOB':
            # 获取言论的初始位置，假设为"说"的下一位
            opinion_index = position + 1

            # 判断言论的起始位置是否为标点符号
            # 如果是，则其位置往下顺延一位
            if arcs[opinion_index][1] == 'WP':
                opinion_index += 1

            # 获取完整言论
            opinion = ''.join(words[opinion_index:])

            # if arcs[head_index][1] == 'ATT':
            #     head_index = arcs[head_index][0]

            # 判断人名的位置是否为标点符号
            # 如果是，则其位置往下顺延一位
            if arcs[head_index][1] == 'WP':
                head_index += 1

            if arcs[head_index][1] == 'ATT':
                head_index += 1

            # 获取人名
            name = words[head_index]

            # 保存人名及其言论
            opinions.append((name, opinion))

    # 返回言论结果列表，元素为元组(name, opinion)
    return opinions


# 提取单个句子
def extract_single_sentence(saying_list, sentence, total_names):
    words = cut_words_ltp(sentence)

    # 获取词性标注
    postags = get_postags(words)

    # 获取ner
    netags = get_ner(words, postags)

    # 获取依存分析
    arcs = get_parsing(words, postags)

    # 获取当前句子中的"说"
    match_words = match_saying_words(words, saying_list, postags)

    if not match_words and "：" not in sentence:
        return False

    # print("匹配到的说", match_words)
    #
    # print("词性标注情况")
    # print([(str(index) + words[index], pos) for index, pos in enumerate(postags)])
    #
    # print("命名实体识别情况")
    # print([(str(index) + words[index], net) for index, net in enumerate(netags)])
    #
    # print("依存句法分析情况")
    # print([(str(index) + words[index], arc) for index, arc in enumerate(arcs)])

    # 获取当前句子中的人名及其位置
    names_with_position = get_names_with_position(sentence, words, total_names)
    # print('人名:', names_with_position)

    res = get_opinions(words, match_words, names_with_position, arcs)

    return res


def main():
    news = """在今天商务部举行的例行发布会上，有媒体表示：IMF近日发布的研究报告称，美国加征关税造成的成本几乎全部由美国企业承担了，但美国总统特朗普称，中国在为美国加征的关税买单。对此，新闻发言人高峰表示：美方的贸易霸凌主义最终损害的是美国自身，买单的是美国的消费者和企业。

    　　高峰表示，中美贸易不平衡，主要是由于美国出口管制等非经济因素以及储蓄率低等原因造成的，加征关税根本解决不了贸易不平衡问题。

    　　关于美国单方面加征关税的影响，高峰强调，美方的贸易霸凌做法最终损害的是美国自身，买单的是美国的消费者和企业，纽约联储经济学家最近的预测表明，美方加征关税措施，将使每个美国家庭每年平均损失831美元。

    　　高峰表示，美国一些智库的研究也显示，如果美方的措施持续下去，会导致美国的GDP增速下滑、就业和投资减少、国内物价上升，美国商品在海外的竞争力下降，已经有越来越多的美国企业、消费者感受到加征关税的影响。

    　　与此同时，高峰再次强调了中方关于中美经贸磋商的立场：中方绝不会接受任何有损国家主权和尊严的协议，在重大原则问题上，中方绝对不会让步，如果要达成协议，美方需要拿出诚意，妥善解决中方提出的核心关切，在平等相待、相互尊重的基础上继续磋商。
    """

    # saying_words_path = 'saying_verbs_cleaned.txt'
    saying_words_path = 'saying_verbs.txt'
    saying_list = load_saying_words(saying_words_path)

    # text_path = 'test_chinese_news.txt'
    # sentences = load_text(text_path)
    # sents_list = sentence_splitter(sentences)

    sents_list = sentence_splitter(news)
    total_names = get_total_names(sents_list)
    print('全部人名', total_names.items())
    for sent in sents_list:
        print(sent)
        opinions = extract_single_sentence(saying_list, sent, total_names)
        if opinions:
            print('提取成功')
            for (name, op) in opinions:
                print("人物：{}\n言论：{}".format(name, op))
        else:
            print('---抱歉，没有找到说---')
        print('*' * 80)


if __name__ == '__main__':
    main()
