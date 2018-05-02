import csv

perfectEssays = []
f = open('dataset/Set1Complete.csv', 'rb')
count = 0
try:
    reader = csv.reader(f)
    for row in reader:
        if count > 0 and len(perfectEssays) <= 10:
            count+=1
            ess_id = int(row[0])
            ess_set = int(row[1])
            ess_text = unicode(row[2], errors='ignore')
            ess_score_r1 = float(row[3])
            ess_score_r2 = float(row[4])
            if (ess_score_r1+ess_score_r2)==12:
                perfectEssays.append(ess_text)
        else:
            count+=1
finally:
    f.close()

f = open('dataset/perfect.csv', 'w')
for essay in perfectEssays:
    f.write(essay)
    f.write("\n")
f.close()
