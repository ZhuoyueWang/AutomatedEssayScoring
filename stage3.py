# perfect essays : 37, 118, 147,
import csv
import sys
import nltk
import numpy
from enchant.checker import SpellChecker
import enchant
import sklearn
from sklearn.feature_extraction.text import TfidfTransformer
import sys, getopt
from nltk import word_tokenize, pos_tag
import re
import io

transformer = TfidfTransformer(smooth_idf=False)


global grammar

grammar = "NP: {<IN>?<IN>?<RB>?<DT>?<JJ>*<NN>}"
grammar = """
	NP:   {<WRB>?<MD>?<PRP>?<IN>?<IN>?<WRB>?<RB>?<DT>?<PRP>?<JJ.*>*<NN.*>+<IN>?<JJ>?<NN>?<CC>?<NN>?}
	CP:   {<JJR|JJS>}
	VP: {<VB.*>}
	NP: {<PRP><MD>}
	NP: {<DT>}
	NP: {<WP>}
	COMP: {<DT>?<NP><RB>?<VP><DT>?<CP><THAN><DT>?<NP>}
	"""

ncount = 0;
vcount = 0;

global nVPflag
global nNPflag

nNPflag = True
nVPflag = True


def get_type2_errors(esstxt):
    #TODO: Define type 2 errors here
    esstxt = re.sub(r'(\@)([A-Za-z]*)([\W]*[\d]*[\W]*)(\s)', " ", esstxt)
    sdict = enchant.Dict("en_US")
    chkr = SpellChecker("en_US")
    chkr.set_text(esstxt)
    err_cnt = 0
    for err in chkr:
        # print "ERROR: ", err.word,
        slist = sdict.suggest(err.word)
        # print "-----",
        # print "Perhaps you meant", slist[0],
        # print "?"
        err_cnt = err_cnt + 1
    return err_cnt


def check_flags(t, nNPflag, nVPflag):
    try:
        t.label
    except AttributeError:
        return [nNPflag, nVPflag]
    else:
        if t._label == "NP":
            nNPflag = False
        if t._label == "VP":
            nVPflag = False
        for child in t:
            flags = check_flags(child, nNPflag, nVPflag)
            nNPflag = flags[0]
            nVPflag = flags[1]
    return [nNPflag, nVPflag]



def get_type1_errors(esstxt):
    'Incomplete sentence'
    esstxt = re.sub(r'(\@)([A-Za-z]*)([\W]*[\d]*[\W]*)(\s)', " ", esstxt)

    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_detector.tokenize(esstxt.strip())

    n_err = 0
    for sent in sents:
        words = word_tokenize(sent)
        tagged_words = pos_tag(words)
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged_words)
        # result.draw()
        flags = check_flags(result, True, True)
        if flags[0]:
            # print "NO NP FOUND : ",
            # print sent
            n_err += 1
            # result.draw()
        if flags[1]:
            # print "NO VP FOUND : ",
            # print sent
            n_err += 1
            # result.draw()
    return n_err

def get_syntax_errors(esstxt):
    nt1 = get_type1_errors(esstxt)
    nt2 = get_type2_errors(esstxt)
    return nt1+nt2

def scoreSYNERR(essay_fn, ifesstxt=False):
    '''Get the essay to be graded'''
    if ifesstxt:
        test_essay = essay_fn
    else:
        with io.open(essay_fn, encoding="ISO-8859-1") as f:
            test_essay = f.read()
    nerrs = get_syntax_errors(test_essay)
    return (12-nerrs*0.4)


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=", "dfile="])
    except getopt.GetoptError:
        print 'stage3.py -i <inputfile> -d <datafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'stage3.py -i <inputfile> -d <datafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            EssayFileName = arg
        elif opt in ("-d", "--dfile"):
            DataFileName = arg
    scoreSYNERR(EssayFileName, DataFileName)



if __name__ == "__main__":
    main(sys.argv[1:])
