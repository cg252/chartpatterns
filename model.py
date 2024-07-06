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
train = data.iloc[:-1000]
test = data.iloc[-1000:]

predictors = ["TSI_Position", "TSI_Crossover", "YBR_Position"]
model.fit(train[predictors], train["Profit"])

preds = model.predict(test[predictors])
preds = pd.Series(preds, index=test.index)

print(precision_score(test["Profit"], preds))

combined = pd.concat([test["Profit"], preds], axis=1)
combined.plot()
#plt.show()