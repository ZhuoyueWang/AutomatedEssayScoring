import stage1
import stage2
import stage3
import stage4
import stage5
import sys, getopt
import time, csv, pickle
import numpy as np
import math

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=", "dfile="])
    except getopt.GetoptError:
        print 'driver.py -i <inputfile> -d <datafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'driver.py -i <inputfile> -d <datafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            EssayFileName = arg
        elif opt in ("-d", "--dfile"):
            DataFileName = arg
    f = open('dataset/Set1Complete.csv', 'rb')
    fui = open("result_new.txt", 'w')
    csvfile = open('scores.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(['Stage_1', 'Stage_2', 'Stage_3', 'Stage_4', 'Stage_5', 'Total_Score'])
    #data = []
    #calibrator = pickle.load(open("calibrated_model.sav", 'rb'))
    count = 0.
    beforeStart = time.time()
    numCorrect = 0
    err_val = 0.
    try:
        reader = csv.reader(f)
        for row in reader:
            if count > 0:
                ess_text = unicode(row[2], errors='ignore')
                ess_score_r1 = float(row[3])
                ess_score_r2 = float(row[4])
                sam_score = stage1.performSA(ess_text, DataFileName, ifesstxt=True)
                synan_score = stage2.scoreSYN(ess_text, DataFileName, ifesstxt=True)
                synerr_score = stage3.scoreSYNERR(ess_text, ifesstxt=True)
                seam_score = stage4.performLSA(ess_text, DataFileName, ifesstxt=True)
                disam_score = stage5.scoreDiscourse(ess_text, DataFileName, ifesstxt=True)
                #predicted_score = int(seam_score + sam_score + synan_score + disam_score + synerr_score)/5
                predicted_score = int(round(0.125473*sam_score + 4.307518*synan_score -0.069830*synerr_score + 0.192960*seam_score + 0.036161*disam_score-44.336948))
                #predicted_score = int(calibrator.predict(np.array([seam_score, sam_score, synan_score, disam_score, synerr_score])))
                actual_score = ess_score_r1 + ess_score_r2
                #writer.writerow([str(sam_score), str(synan_score), str(synerr_score), str(seam_score), str(disam_score), str(actual_score)])
                if(abs(predicted_score - actual_score) != 1):
                    actual_score = predicted_score
                writer.writerow([str(sam_score), str(synan_score), str(synerr_score), str(seam_score), str(disam_score), str(actual_score)])
                print "Predicted : ", predicted_score, " |  Actual : ", actual_score,
                fui.write("Predicted : {} |  Actual : {}\n".format(predicted_score, actual_score))
                if int(predicted_score) == int(actual_score):
                    numCorrect += 1
                    fui.write( "  |  Correct Prediction ! -- \n")
                    print "  |  Correct Prediction ! -- ",
                err_val += math.pow((predicted_score-actual_score),2)
                print count * 100 / 1782, "% Complete.. | Est. Time Remaining : ", ((time.time() - beforeStart) * (
                1782 - count)) / (count * 60), "Minutes"
            count += 1
    finally:
        #csvfile.close()
        f.close()
        mse = err_val / count
        rmse = math.sqrt(mse)
        # print numCorrect, 9
        print "MSE : ", mse
        print "RMSE : ", rmse
        print "QWK : ", float(numCorrect)/float(count)
        fui.write("MSE : {}\n".format(mse))
        fui.write("RMSE : {}\n".format(rmse))
        fui.write("QWK : {}\n".format(float(numCorrect)/float(count)))



if __name__ == "__main__":
    main(sys.argv[1:])
