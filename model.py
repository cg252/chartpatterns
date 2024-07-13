import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
import matplotlib.pyplot as plt


data = pd.read_csv("data.csv", index_col=0)
data.index = pd.to_datetime(data.index, utc=True)

del data["Time"]
del data["Open"]
del data["High"]
del data["Low"]
 
model = RandomForestClassifier(n_estimators=300, min_samples_split=100, random_state=1) 

trainlen = int(0.7*len(data))
testlen = len(data) - trainlen

train = data.iloc[:-trainlen]
test = data.iloc[-testlen:]
 
predictors = ["TSI_Position", "TSI_Crossover", "YBR_Position"]
model.fit(train[predictors], train["Results"])
preds = model.predict(test[predictors])
preds = pd.Series(preds, index=test.index, name="Predictions")


print(precision_score(test["Results"], preds))


combined = pd.concat([test["Results"], preds], axis=1)

print(combined["Predictions"].value_counts())
print(combined["Results"].value_counts())





z = 0
r = 0
for i in range(len(test)):
    # if both reality and the prediction agree that it will be profitable, increase Z by one. 
    if test["Results"].iloc[i] == 1 and preds.iloc[i] == 1:
        z += 1
    # if in reality it is profitable but the model misses it, append r. 
    elif test["Results"].iloc[i]== 1 and preds.iloc[i] == 0:
        r += 1


profit_prediction = round((z/(z+r))*100, 2)
print(profit_prediction)

combined.to_csv("model.csv")