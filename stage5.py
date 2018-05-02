# perfect essays : 37, 118, 147,
import csv
import sys
import nltk
import numpy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
from sklearn.random_projection import sparse_random_matrix
from scipy import spatial
from nltk import word_tokenize, pos_tag
import re
import sys, getopt
import io

test_essay = "@ORGANIZATION1, Computers are great tools and a great piece of modern technology. Almost every family has them. About @PERCENT1 of my class has computers. So many people have them because their helpful and another current learning resource. Also it's a gr"



grammar = "NP: {<IN>?<IN>?<RB>?<DT>?<JJ>*<NN>}"
grammar = """
	NP:   {<IN>?<IN>?<RB>?<DT>?<PRP>?<JJ.*>*<NN.*>+<IN>?<JJ>?<NN>?<CC>?<NN>?}
	CP:   {<JJR|JJS>}
	VP: {<VB.*>}
	COMP: {<DT>?<NP><RB>?<VP><DT>?<CP><THAN><DT>?<NP>}
	"""
ncount = 0;
vcount = 0;

global ideas_np
global ideas_vp


def extract_ideas(t, inp, ivp):
    try:
        t.label
    except AttributeError:
        return
    else:
        if t._label == "NP":
            temp = []
            for child in t:
                npw_ = ''.join(child[0]).encode('utf-8')
                npt_ = ''.join(child[1]).encode('utf-8')
                #TODO : HERE, ADD ONLY Nouns and adjective
                if npt_ == "NP" or npt_ == "JJ" or npt_ == "NNS" or npt_ == "NN":
                    temp.append(npw_)
            inp.append(temp)
        if t._label == "VP":
            temp = []
            for child in t:
                vpw_ = ''.join(child[0]).encode('utf-8')
                # print vpw_
                temp.append(vpw_)
            ivp.append(temp)
        for child in t:
            extract_ideas(child, inp, ivp)
    return [inp, ivp]


#TODO : Detect variations in tense.
def get_ideas_unigram(esstxt):
    ideas_np = []
    ideas_vp = []

    esstxt = re.sub(r'(\@)([A-Za-z]*)([\W]*[\d]*[\W]*)(\s)', " ", esstxt)

    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_detector.tokenize(esstxt.strip())

    for sent in sents:
        words = word_tokenize(sent)
        tagged_words = pos_tag(words)
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged_words)
        inp = []
        ivp = []
        inp, ivp = extract_ideas(result, inp, ivp)
        ideas_np.append(inp)
        ideas_vp.append(ivp)

    # print "Author presents the following key ideas: \n"

    key_ideas = []

    for nps in ideas_np:
        for nptuples in nps:
            for nptuple in nptuples:
                # nptxt = "".join(str(r) for v in nptuples for r in v)
                nptxt = "".join(nptuple)
                if not nptxt in key_ideas and not len(nptuple)==0:
                    key_ideas.append(nptxt.lower())

    return " ".join(key_ideas)


def get_ideas_bigram(esstxt):
    ideas_np = []
    ideas_vp = []

    esstxt = re.sub(r'(\@)([A-Za-z]*)([\W]*[\d]*[\W]*)(\s)', " ", esstxt)

    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_detector.tokenize(esstxt.strip())

    for sent in sents:
        words = word_tokenize(sent)
        tagged_words = pos_tag(words)
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged_words)
        inp = []
        ivp = []
        inp, ivp = extract_ideas(result, inp, ivp)
        ideas_np.append(inp)
        ideas_vp.append(ivp)

    # print "Author presents the following key ideas: \n"

    key_ideas = []

    for nps in ideas_np:
        for nptuples in nps:
            nptxt = "".join(str(r) for v in nptuples for r in v)
            if not nptxt in key_ideas and len(nptuples)!=0:
                key_ideas.append(nptxt.lower())

    return " ".join(key_ideas)




def scoreDiscourse(essay_fn, data_fn, ifesstxt=False):
    esstxts = []
    svParams = []
    '''Get perfect essays'''
    with io.open(data_fn, encoding="ISO-8859-1") as f:
        perfect_essays = f.readlines()

    if ifesstxt:
        test_essay = essay_fn
    else:
        '''Get the essay to be graded'''
        with io.open(essay_fn, encoding="ISO-8859-1") as f:
            test_essay = f.read()
    ignorechars = ''',:'!@'''

    test_k_ideas_unigram = get_ideas_unigram(test_essay)
    test_k_ideas_bigram = get_ideas_bigram(test_essay)

    csim_unigram_list = []
    csim_bigram_list = []

    # UNIGRAM
    for ess_text in perfect_essays:
        esstxts = []
        esstxts.append(test_k_ideas_unigram)
        esstxts.append(get_ideas_unigram(ess_text))
        vectorizer = TfidfVectorizer(max_features=10000,
                                 min_df=0.5, stop_words='english',
                                 use_idf=True)
        X = vectorizer.fit_transform(esstxts)
        tfidf = X.toarray()
        csim_unigram_list.append(1 - spatial.distance.cosine(tfidf[1], tfidf[0]))

    # BIGRAM
    for ess_text in perfect_essays:
        esstxts = []
        esstxts.append(test_k_ideas_bigram)
        esstxts.append(get_ideas_bigram(ess_text))
        vectorizer = TfidfVectorizer(max_features=10000,
                                     min_df=0.5, stop_words='english',
                                     use_idf=True)
        X = vectorizer.fit_transform(esstxts)
        tfidf = X.toarray()
        csim_bigram_list.append(1 - spatial.distance.cosine(tfidf[1], tfidf[0]))

    csim = max(csim_unigram_list) + max(csim_bigram_list)
    # print csim_unigram_list
    # print csim_bigram_list
    # print csim
    return csim*12




def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=", "dfile="])
    except getopt.GetoptError:
        print 'stage5.py -i <inputfile> -d <datafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'stage5.py -i <inputfile> -d <datafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            EssayFileName = arg
        elif opt in ("-d", "--dfile"):
            DataFileName = arg
    scoreDiscourse(EssayFileName, DataFileName)



if __name__ == "__main__":
    main(sys.argv[1:])
