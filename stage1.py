import csv
import math
import sys
from nltk import word_tokenize, pos_tag
from string import punctuation
import nltk.data
import sys, getopt
import io

class Essay:
    'Common base class for all essays'

    def __init__(self, ess_id, ess_set, ess_score_r1, ess_score_r2, wcount, lwcount, scount, avslength):
        self.ess_id = ess_id
        self.ess_set = ess_set
        self.ess_score_r1 = ess_score_r1
        self.ess_score_r2 = ess_score_r2
        self.wcount = wcount
        self.lwcount = lwcount
        self.scount = scount
        self.avslength = avslength
    def displayProfile(self):
        print "ID : ", self.ess_id, ", Set: ", self.ess_set, ", SR1: ", self.ess_score_r1, ", SR2: ", self.ess_score_r2

    def getProfile(self):
        return [self.ess_id, self.ess_set, self.ess_score_r1, self.ess_score_r2, self.wcount, self.lwcount, self.scount, self.avslength]


def getStats(contents, raw_text):
    wcount = 0
    for line in contents:
        if (line != "\n"):
            if line.rstrip() not in punctuation:
                wcount = wcount + 1
    lwcount = 0
    for line in contents:
        if (line != "\n"):
            if (len(line.rstrip()) >= 8):
                lwcount = lwcount + 1
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_detector.tokenize(raw_text.strip())
    i = 0
    avslength = 0
    for line in sents:
        i += 1
        sen_words = word_tokenize(line)
        swcount = 0 #number of words in sentence
        for wline in sen_words:
            if (wline != "\n"):
                if wline.rstrip() not in punctuation:
                    swcount = swcount + 1
        avslength = (avslength * (i - 1) + swcount) / i
    scount = len(sents)
    return [wcount, lwcount, avslength, scount]



def getPerfectStat(perfect_essays):
    perfect_stats = []
    for perfect_essay in perfect_essays:
        perfect_stats.append(getStats(perfect_essay, perfect_essay))
    num_essays = len(perfect_stats)
    avg_wcount = 0.
    avg_lwcount = 0.
    avg_avslength = 0.
    avg_scount = 0.
    for perfect_stat in perfect_stats:
        avg_wcount = avg_wcount + perfect_stat[0]
        avg_lwcount = avg_lwcount + perfect_stat[1]
        avg_avslength = avg_avslength + perfect_stat[2]
        avg_scount = avg_scount + perfect_stat[3]
    avg_wcount = avg_wcount / num_essays
    avg_lwcount = avg_lwcount / num_essays
    avg_avslength = avg_avslength / num_essays
    avg_scount = avg_scount / num_essays
    perfect_stat = [avg_wcount, avg_lwcount, avg_avslength, avg_scount]
    return perfect_stat



def performSA(essay_fn, data_fn, ifesstxt=False):
    svParams = []
    '''Get perfect essays'''
    with io.open(data_fn, encoding="ISO-8859-1") as f:
        perfect_essays = f.readlines()
    # esstxts.append(" ".join(perfect_essays))

    if ifesstxt:
        test_essay = essay_fn
    else:
        '''Get the essay to be graded'''
        with io.open(essay_fn, encoding="ISO-8859-1") as f:
            test_essay = f.read()
    ignorechars = ''',:'!@'''

    perfect_stat = getPerfectStat(perfect_essays)
    test_stat = getStats(test_essay, test_essay)

    # print "perfect_stat", perfect_stat
    # print "test_stat", test_stat

    stat_scores = []
    for i in range(0,len(perfect_stat)):
        pstat = perfect_stat[i]
        tstat = test_stat[i]
        diff = math.fabs(pstat - tstat)
        # print "i : ", i, "pstat : ", pstat, " | tstat : ", tstat, " ---> diff", diff
        try:
            stat_scores.append(12 - (diff*12/pstat))
        except ZeroDivisionError:
            stat_scores.append(12)

    fscore = 0.
    for stat_score in stat_scores:
        # print "stat_score", stat_score
        fscore = fscore + stat_score
    fscore = fscore/4
    return fscore




def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=", "dfile="])
    except getopt.GetoptError:
        print 'stage1.py -i <inputfile> -d <datafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'stage1.py -i <inputfile> -d <datafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            EssayFileName = arg
        elif opt in ("-d", "--dfile"):
            DataFileName = arg
    return performSA(EssayFileName, DataFileName)



if __name__ == "__main__":
    main(sys.argv[1:])
