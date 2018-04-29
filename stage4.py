import nltk
from nltk import CFG
from nltk import word_tokenize, pos_tag
import csv
import re
import nltk.data


'''
nltk.download('large_grammars')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
'''
grammar = nltk.data.load('grammars/large_grammars/atis.cfg')



with open('result/stage1_result.csv', 'r', newline='', encoding='utf-8', errors='ignore') as fd:
	fd = csv.reader(fd, delimiter=',')
	for row in fd:
		esstxt = row[2]
		sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
		sents = sent_detector.tokenize(esstxt.strip())
		print(sents)
		for sent in sents:
			words = word_tokenize(sent)
			tagged_words = pos_tag(words)
			cp = nltk.RegexpParser(grammar)
			result = cp.parse(tagged_words)
			for tree in result:
				print(tree)
