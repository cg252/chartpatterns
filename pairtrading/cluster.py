from sklearn.preprocessing import MinMaxScaler
from sklearn import cluster, covariance, manifold
import numpy as np
import pandas as pd
import pickle

varianceData = pd.read_pickle('data.pkl')

edge_model = covariance.GraphicalLassoCV(verbose=True)
X = varianceData.copy()
X = X / X.std(axis=0)
edge_model.fit(X)

pickle.dump(edge_model, open("edgemodel.pkl", "wb"))

# using Affinity Propagation bc it does not enforce equal-size clusters 
# & it can choose automatically the number of clusters from the data.
_, labels = cluster.affinity_propagation(edge_model.covariance_, random_state=0)
n_labels = labels.max()


names=[]
for stock in varianceData.columns.tolist():
    names.append(stock)
names = np.array(names)

for i in range(n_labels + 1):
    print('Cluster {0}: {1}'.format((i + 1), ', '.join(names[labels == i])))
