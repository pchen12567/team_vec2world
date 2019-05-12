This folder contains the following:

- python codes for training a `word2vec` model;
- a sample snippet of chinese news taken from [ifeng.com](https://news.ifeng.com/c/7mcljJF7cYK);
- the output of annotating the news snippet by running the stanford CoreNLP server:

```shell
cd path/to/stanford-corenlp-full-2018-10-05
java -Xmx8192m -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props StanfordCoreNLP-chinese.properties -annotators tokenize,ssplit,pos,lemma,ner,parse,depparse,coref,quote -file /path/to/input/file.txt  -outputFormat text (or json, xml) -outputDirectory /path/to/output/directory
```
