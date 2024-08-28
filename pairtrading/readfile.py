import pickle
import pandas as pd
import numpy as np
from sklearn import cluster, covariance

model = pickle.load(open("edgemodel.pkl", "rb"))
varianceData = pd.read_pickle('data.pkl')

_, labels = cluster.affinity_propagation(random_state=0).fit(model.covariance)
n_labels = labels.max()

names=[]
for stock in varianceData.columns.tolist():
    names.append(stock)
names = np.array(names)


for i in range(n_labels + 1):
    print('Cluster {0}: {1}'.format((i + 1), ', '.join(names[labels == i])))
