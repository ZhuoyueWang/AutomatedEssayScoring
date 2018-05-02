# perfect essays : 37, 118, 147,
import csv
import sys
from nltk.corpus import stopwords
import numpy
from nltk import word_tokenize
from nltk import pos_tag
import numpy as np
import sys, getopt
from string import punctuation
import math

class LSA(object):
    def __init__(self, stopwords, ignorechars):
        self.stopwords = stopwords
        self.ignorechars = ignorechars
        self.wdict = {}
        self.dcount = 0

class Essay:
    'Common base class for all essays'

    def __init__(self, ess_id, ess_set, ess_text, ess_score_r1, ess_score_r2):
        self.ess_id = ess_id
        self.ess_set = ess_set
        self.ess_text = ess_text
        self.ess_score_r1 = ess_score_r1
        self.ess_score_r2 = ess_score_r2

    def displayProfile(self):
        print "ID : ", self.ess_id, ", Set: ", self.ess_set, ", SR1: ", self.ess_score_r1, ", SR2: ", self.ess_score_r2

    def getProfile(self):
        return [self.ess_id, self.ess_set, self.ess_score_r1, self.ess_score_r2, self.wcount, self.lwcount, self.scount, self.pcncount, self.avslength]


def getPOSCounts(essay_txt):
    ncount = 0.
    vcount = 0.
    adjcount = 0.
    pron_count = 0.
    prep_count = 0. #preposition count
    modaux_count = 0. #modal auxiliary
    punc_count = 0.
    adv_count = 0.
    dt_count = 0.
    conj_count = 0.
    token_count = 0.
    word_tokens = word_tokenize(essay_txt)
    tagged_tokens = pos_tag(word_tokens)
    # print tagged_tokens
    for tagged_token in tagged_tokens:
        if("NN" == tagged_token[1][0:2]):
            ncount += 1
        elif("VB" == tagged_token[1][0:2]):
            vcount += 1
        elif("JJ" == tagged_token[1][0:2]):
            adjcount += 1
        elif("PR" == tagged_token[1][0:2] or "WH" == tagged_token[1][0:2]):
            pron_count +=1
        elif("MD" == tagged_token[1][0:2]):
            modaux_count +=1
        elif("IN" == tagged_token[1][0:2]):
            prep_count += 1
        elif("RB" == tagged_token[1][0:2]):
            adv_count += 1
        elif ("DT" == tagged_token[1][0:2]):
            dt_count += 1
        elif ("CC" == tagged_token[1][0:2]):
            conj_count += 1
        elif tagged_token[0] in punctuation:
            punc_count += 1
        token_count+=1
    return np.array([ncount/token_count, vcount/token_count, adjcount/token_count, pron_count/token_count, prep_count/token_count, modaux_count/token_count, punc_count/token_count, adv_count/token_count, dt_count/token_count, conj_count/token_count])



def scoreSYN(essay_fn, data_fn, ifesstxt=False):
    esstxts = []
    svParams = []
    '''Get perfect essays'''
    with open('dataset/'+data_fn, 'rb') as f:
        perfect_essays = f.readlines()
    esstxts.append(" ".join(perfect_essays))

    if ifesstxt:
        test_essay = essay_fn
    else:
        '''Get the essay to be graded'''
        with open(essay_fn, 'rb') as f:
            test_essay = f.read()
    esstxts.append(test_essay)
    ignorechars = ''',:'!@'''

    test_counts = getPOSCounts(test_essay)
    avg_score = 0
    num_essays = len(perfect_essays)
    # print test_counts
    for essay in perfect_essays:
        pos_score = 0
        perf_count = getPOSCounts(essay)
        diff_counts = perf_count - test_counts
        # print "perf_count", perf_count

        for i in range(0,len(diff_counts)):
            diff_counts[i] = 12*math.fabs(diff_counts[i])

        # print "diff_counts", diff_counts

        for diff_score in diff_counts:
            pos_score += diff_score

        pos_score = 12 - (pos_score/10)
        avg_score = avg_score + pos_score
    avg_score = avg_score/num_essays

    return avg_score




def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=", "dfile="])
    except getopt.GetoptError:
        print 'stage2.py -i <inputfile> -d <datafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'stage2.py -i <inputfile> -d <datafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            EssayFileName = arg
        elif opt in ("-d", "--dfile"):
            DataFileName = arg
    scoreSYN(EssayFileName, DataFileName)



if __name__ == "__main__":
    main(sys.argv[1:])
