import jieba
import logging
from stanfordcorenlp import StanfordCoreNLP

# Local server
# Terminal command:
'''
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer 
-annotators tokenize,ssplit,pos,lemma,ner,parse,depparse,coref,quote -port 9000 -timeout 30000
'''
nlp = StanfordCoreNLP('http://localhost', port=9000, lang='zh', logging_level=logging.DEBUG)


text_path = 'test_chinese_news.txt'
sentence = ''

with open(text_path, 'r') as f:
    for line in f.readlines():
        if line.strip():
            sentence += line


def cut(string):
    return ' '.join(jieba.cut(string))


cut_sentence = cut(sentence)

# print(nlp.word_tokenize(sentence))
# print(nlp.pos_tag(sentence))
# print(nlp.parse(sentence))
# print(nlp.dependency_parse(sentence))

# print(sentence)
# print(cut_sentence)
# print(nlp.ner(cut_sentence))
print(nlp.ner(sentence))
nlp.close()
