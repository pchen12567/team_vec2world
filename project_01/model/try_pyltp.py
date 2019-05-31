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
from pyltp import SementicRoleLabeller

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
def match_saying_words(words, saying_list, postags):
    match = []
    for index, word in enumerate(words):
        if word in saying_list and postags[index] == 'v':
            match.append((word, index))
    return match


# 提取单个句子
def extract_single_sentence(saying_list, sentence):
    words = cut_words_ltp(sentence)

    # 获取词性标注
    postags = get_postags(words)

    match_words = match_saying_words(words, saying_list, postags)

    # 获取ner
    netags = get_ner(words, postags)

    # 获取依存分析
    arcs = get_parsing(words, postags)

    if not match_words:
        print("----不包含'说'----")
        return False

    # print("匹配到的说", match_words)

    # print("词性标注情况")
    # print([(str(index) + words[index], pos) for index, pos in enumerate(postags)])

    # print("命名实体识别情况")
    # print([(str(index) + words[index], net) for index, net in enumerate(netags)])

    # print("依存句法分析情况")
    # print([(str(index) + words[index], arc) for index, arc in enumerate(arcs)])

    names = get_names(words, netags)
    print('人名:', names)

    res = get_opinions(words, match_words, names, arcs)

    return res


# 获取言论
def get_opinions(words, match_words, names, arcs):
    opinions = []

    for (name, position) in names:
        start_index = position[0]
        end_index = position[1]

        # if "：" in words:
        #     print('condition one')
        #     opinion_index = words.index('：')
        #     opinion = ''.join(words[opinion_index + 1:])
        #     opinions[name] = opinion

        # 通过人名的 arc.relation = 'SBV' 找言论
        if arcs[end_index][1] == 'SBV':
            opinion_index = arcs[end_index][0]

            if arcs[opinion_index][1] == 'WP':
                opinion_index += 1

            opinion = ''.join(words[opinion_index:])
            opinions.append((name, opinion))

        # for w in match_words:
        #     saying_index = w[1]
        #
        #     head = arcs[saying_index][0]
        #     relation = arcs[saying_index][1]
        #
        #     if head == start_index and relation == 'HED':
        #         # print('condition two')
        #         opinion = ''.join(words[saying_index + 2:])
        #         opinions.append((name, opinion))
        #
        #     elif arcs[head][1] == 'ATT' and relation == 'HED':
        #         # print('condition 3')
        #         person_index = arcs[head][0]
        #
        #         if arcs[person_index][1] == 'WP':
        #             print('i am in')
        #             person_index += 1
        #
        #         if name.startswith(words[person_index]):
        #             opinion = ''.join(words[saying_index + 2:])
        #             opinions.append((name, opinion))

    return opinions


# 获取人名
def get_names(words, netags):
    names = []
    for start_index, ner in enumerate(netags):
        # 单个词构成的人名
        if ner == 'S-Nh':
            name = words[start_index]
            position = (start_index, start_index)
            names.append((name, position))

        # 多个词构成的人名
        if ner == 'B-Nh':
            end_netags = netags[start_index:]
            end_index = start_index + end_netags.index('E-Nh')
            name = ''.join(words[start_index: end_index + 1])
            position = (start_index, end_index)
            names.append((name, position))

        # 单个词构成的组织名
        if ner == 'S-Ni':
            name = words[start_index]
            position = (start_index, start_index)
            names.append((name, position))

        # 多个词构成的组织名
        if ner == 'B-Ni':
            end_netags = netags[start_index:]
            end_index = start_index + end_netags.index('E-Ni')
            name = ''.join(words[start_index: end_index + 1])
            position = (start_index, end_index)
            names.append((name, position))

        # if ner == 'S-Ns':
        #     name = words[start_index]
        #     position = (start_index, start_index)
        #     names.append((name, position))
        #
        # if ner == 'B-Ns':
        #     end_netags = netags[start_index:]
        #     end_index = start_index + end_netags.index('E-Ns')
        #     name = ''.join(words[start_index: end_index + 1])
        #     position = (start_index, end_index)
        #     names.append((name, position))

    return names


def main():
    # saying_words_path = 'saying_verbs_cleaned.txt'
    saying_words_path = 'saying_verbs.txt'
    saying_list = load_saying_words(saying_words_path)

    # text_path = 'test_chinese_news.txt'
    # sentences = load_text(text_path)
    #
    # sents_list = sentence_splitter(sentences)
    #
    # for sent in sents_list:
    #     print(sent)
    #     opinions = extract_single_sentence(saying_list, sent)
    #     if opinions:
    #         for name, op in opinions.items():
    #             print("人物：{}\n言论：{}".format(name, op))
    #     print('*' * 80)

    news = """在今天商务部举行的例行发布会上，有媒体表示：IMF近日发布的研究报告称，美国加征关税造成的成本几乎全部由美国企业承担了，但美国总统特朗普称，中国在为美国加征的关税买单。对此，新闻发言人高峰表示：美方的贸易霸凌主义最终损害的是美国自身，买单的是美国的消费者和企业。

    　　高峰表示，中美贸易不平衡，主要是由于美国出口管制等非经济因素以及储蓄率低等原因造成的，加征关税根本解决不了贸易不平衡问题。

    　　关于美国单方面加征关税的影响，高峰强调，美方的贸易霸凌做法最终损害的是美国自身，买单的是美国的消费者和企业，纽约联储经济学家最近的预测表明，美方加征关税措施，将使每个美国家庭每年平均损失831美元。

    　　高峰表示，美国一些智库的研究也显示，如果美方的措施持续下去，会导致美国的GDP增速下滑、就业和投资减少、国内物价上升，美国商品在海外的竞争力下降，已经有越来越多的美国企业、消费者感受到加征关税的影响。

    　　与此同时，高峰再次强调了中方关于中美经贸磋商的立场：中方绝不会接受任何有损国家主权和尊严的协议，在重大原则问题上，中方绝对不会让步，如果要达成协议，美方需要拿出诚意，妥善解决中方提出的核心关切，在平等相待、相互尊重的基础上继续磋商。
    """

    # news = """美国贸易代表莱特希泽星期五表示，他已收到总统特朗普的指示，对其余尚未加征关税的所有中国商品加征关税，星期一将公布细节。此后特朗普发推特呼吁中国现在就采取行动(向美方让步)。关于中美下一步何时磋商，美财政部长姆努钦对媒体回应说：“目前还没有这方面的安排。”
    #
    # 美国极限施压的大棒高高举起，中方的态度是：我们做好了应对各种情况的准备。“极限施压”与“应对各种情况”在博弈。
    #
    # 美方是挑起贸易战的一方，自恃实力强大，相信它的关税大棒足以压垮中国。中方的回应则是太极哲学的示范版，坚守原则，不主动打也不惧战，用更大的承受力瓦解对方的攻击力，增加其他情况出现的可能性。
    #
    # 美方攻势猛烈，但这种攻势在经济学上充满了非理性，对美国经济将导致常识性的自伤。美方显然寄希望于人类贸易史上从未有过的凶猛关税战可以一举摧毁中国的意志，以短时间内的损失换取中国接受不平等协议，铸就美国现政府的“辉煌大业”。美国的做法是赌博。美方不断发声，一个动作接一个动作，表现出的其实是他们急切希望这一切迅速生效的焦虑。
    # """

    sents_list = sentence_splitter(news)
    for sent in sents_list:
        print(sent)
        opinions = extract_single_sentence(saying_list, sent)
        if opinions:
            print('提取成功')
            for (name, op) in opinions:
                print("人物：{}\n言论：{}".format(name, op))
        else:
            print('提取失败')
        print('*' * 80)


if __name__ == '__main__':
    main()
