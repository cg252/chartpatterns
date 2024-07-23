import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
#import matplotlib.pyplot as plt


data = pd.read_csv("data.csv", index_col=0)
data.index = pd.to_datetime(data.index, utc=True)
#data = data[data.YBR_Crossover != 0]
 
model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1) 

trainlen = int(0.75*len(data))
testlen = len(data) - trainlen

train = data.iloc[:-trainlen]
test = data.iloc[-testlen:]
 
predictors = ["Signal", "Hammer", "TSI_Crossover", "YBR_Crossover"]
model.fit(train[predictors], train["Return"])
preds = model.predict(test[predictors])
preds = pd.Series(preds, index=test.index, name="Predictions")

print(precision_score(test["Return"], preds, average='macro'))


combined = pd.concat([test["Return"], preds], axis=1)

print(combined["Predictions"].value_counts())
print(combined["Return"].value_counts())



combined.to_csv("model.csv")
