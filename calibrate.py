import stage1
import stage2
import stage3
import stage4
import stage5
import sys, getopt
import csv
from sklearn import linear_model
import numpy as np
import matplotlib.pyplot as plt
import warnings
import time
import pickle

warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

def randPartition(alldata_X, alldata_Y, _FRACTION):
    np.random.seed(0)
    indices = np.arange(alldata_X.shape[0])
    np.random.shuffle(indices)

    dataX = alldata_X[indices]
    dataY = alldata_Y[indices]


    partition_index = int(dataX.shape[0] * _FRACTION)

    trainX = dataX[0:partition_index]
    testX = dataX[partition_index:dataX.shape[0]]

    trainY = dataY[0:partition_index]
    testY = dataY[partition_index:dataY.shape[0]]

    return [trainX, trainY, testX, testY]


def main(argv):
    data_X = []
    data_Y = []
    try:
        opts, args = getopt.getopt(argv,"hi:d:",["ifile=", "dfile="])
    except getopt.GetoptError:
        print 'CalibrateUES.py -i <inputfile> -d <datafile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'CalibrateUES.py -i <inputfile> -d <datafile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            EssayFileName = arg
        elif opt in ("-d", "--dfile"):
            DataFileName = arg
    f = open('dataset/Set1Complete.csv', 'rb')
    count = 0.
    beforeStart = time.time()
    try:
        reader = csv.reader(f)
        for row in reader:
            if count > 0:
                ess_text = unicode(row[2], errors='ignore')
                ess_score_r1 = float(row[3])
                ess_score_r2 = float(row[4])
                seam_score = stage4.performLSA(ess_text, DataFileName, ifesstxt=True)
                sam_score = stage1.performSA(ess_text, DataFileName, ifesstxt=True)
                synan_score = stage2.scoreSYN(ess_text, DataFileName, ifesstxt=True)
                disam_score = stage5.scoreDiscourse(ess_text, DataFileName, ifesstxt=True)
                synerr_score = stage3.scoreSYNERR(ess_text, ifesstxt=True)
                data_X.append([seam_score, sam_score, synan_score, disam_score, synerr_score])
                data_Y.append(ess_score_r1+ess_score_r2)
            count +=1
            print count*100/1782, "% Complete.. | Est. Time Remaining : ", ((time.time()-beforeStart)*(1782-count))/(count*60), "Minutes"
    finally:
        f.close()

    data_X = np.array(data_X)
    data_Y = np.array(data_Y)

    print data_X.shape, data_Y.shape
    trainX, trainY, testX, testY = randPartition(data_X, data_Y, 0.75)

    print trainX.shape, trainY.shape, testX.shape, testY.shape
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(trainX, trainY)

    # The coefficients
    print('Coefficients: \n', regr.coef_)
    # The mean squared error
    print("Mean squared error: %.2f"
          % np.mean((regr.predict(testX) - testY) ** 2))
    # Explained variance score: 1 is perfect prediction
    print('Variance score: %.2f' % regr.score(testX, testY))

    print "Calibrated Weights : "
    print regr.coef_
    filename = 'calibrated_model.sav'
    pickle.dump(regr, open(filename, 'wb'))


if __name__ == "__main__":
    main(sys.argv[1:])
