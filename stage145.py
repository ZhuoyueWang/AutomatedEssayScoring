import csv
import re
from nltk import word_tokenize, pos_tag
from string import punctuation
import nltk
from nltk import CFG
import nltk.data

grammar = "NP: {<IN>?<IN>?<RB>?<DT>?<JJ>*<NN>}"
grammar = """
	NP:   {<IN>?<IN>?<RB>?<DT>?<PRP>?<JJ.*>*<NN.*>+<IN>?<JJ>?<NN>?<CC>?<NN>?}
	CP:   {<JJR|JJS>}
	VP: {<VB.*>}
	COMP: {<DT>?<NP><RB>?<VP><DT>?<CP><THAN><DT>?<NP>}
	"""


class Essay:
     def __init__(self, id, set, content, score, word_count = 0, long_word_count = 0, sentence_count= 0, avg_sentence_len = 0.0, key_ideas = []):
         self.essay_id = id
         self.essay_set = set
         self.essay_content = content
         self.predicted_score = score
         self.word_count = word_count
         self.long_word_count = long_word_count
         self.sentence_count = sentence_count
         self.avg_sentence_len = avg_sentence_len
         self.key_ideas = key_ideas

     def printProfile(self):
         print("Essay ID: {}\nEssay set: {}\nEssay predict score: {}\nEssay word count: {}\nEssay long word count: {}\n".format(self.essay_id, self.essay_set, self.word_count, self.long_word_count))

     def getProfile(self):
         return [self.essay_id, self.essay_set, self.essay_content, self.predicted_score, self.word_count, self.long_word_count, self.sentence_count, self.avg_sentence_len]



######Stage 1

essay_arr = []
count = 0
with open('dataset/training_set_rel3.tsv', 'r', newline='', encoding='utf-8', errors='ignore') as fd:
    rd = csv.reader(fd, delimiter='\t')
    for row in rd:
        if count != 0:
            curr_id = int(row[0])
            curr_set = int(row[1])
            curr_content = row[2]
            curr_score = 0.0
            if curr_set == 1:
                curr_score = (int(row[6])/12)*100
            elif curr_set == 2:
                curr_score = 0.5*((int(row[6])/6)*100+(int(row[9])/4)*100)
            elif curr_set == 3:
                curr_score = (int(row[6])/3)*100
            elif curr_set == 4:
                curr_score = (int(row[6])/3)*100
            elif curr_set == 5:
                curr_score = (int(row[6])/4)*100
            elif curr_set == 6:
                curr_score = (int(row[6])/4)*100
            elif curr_set == 7:
                curr_score = (int(row[6])/30)*100
            elif curr_set == 8:
                curr_score = (int(row[6])/60)*100
            curr_essay = Essay(curr_id, curr_set, curr_content, curr_score)
            essay_arr.append(curr_essay)
        count += 1

#rd.close()

for curr in essay_arr:
    content = curr.essay_content
    words = content.split()
    word_count = 0
    long_word_count = 0
    for w in words:
        num_letter = 0
        for c in w:
            if c == '@':
                continue
            if (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122):
                num_letter += 1
        if num_letter >= 8:
            long_word_count += 1
        word_count += 1
    curr.long_word_count = long_word_count
    curr.word_count = word_count
    sentence_count = len(re.split(r'[.!?]+', content))
    curr.sentence_count = sentence_count
    curr.avg_sentence_len = word_count/sentence_count


results = open('result/stage1_result.csv', 'w')
for essay in essay_arr:
    results.write(str(essay.getProfile())[1:-1])
    results.write("\n")
print("stage 1 done")
#results.close()





######Stage 2







#####Stage 4 and 5
#grammar = nltk.data.load('grammars/large_grammars/atis.cfg')
def extract_ideas(t, inp, ivp):
    try:
        t.label
    except AttributeError:
        return
    else:
        if t._label == "NP":
            temp = []
            for child in t:
                npw_ = str(child[0])
                npt_ = str(child[1])
                if npt_ == "NP" or npt_ == "JJ" or npt_ == "NNS" or npt_ == "NN":
                    temp.append(npw_)
                else:
                    '''print("Not appending " + npw_ + "because it is a " + npt_)'''
            inp.append(temp)
        if t._label == "VP":
            temp = []
            for child in t:
                vpw_ = str(child[0])
                temp.append(vpw_)
            ivp.append(temp)
        for child in t:
            extract_ideas(child, inp, ivp)
    return [inp, ivp]


for essay in essay_arr:
    ideas_np = []
    ideas_vp = []
    esstxt = essay.essay_content
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
    curr_key_ideas = []
    print("Key Ideas in essay {}:".format(essay.essay_id))
    for nps in ideas_np:
        for nptuples in nps:
            # print "-",
            # for wnps in nptuples:
            #     # print wnps
            for nptuple in nptuples:
                # nptxt = "".join(str(r) for v in nptuples for r in v)
                nptxt = "".join(nptuple)
                if not nptxt in curr_key_ideas and not len(nptuple) == 0:
                    curr_key_ideas.append(nptxt.lower())
    print(",".join(curr_key_ideas))
    essay.key_ideas = curr_key_ideas

#print(ideas_np)
#print(ideas_vp)
