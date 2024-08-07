import pandas as pd
import matplotlib.pyplot as plt 


data = pd.read_csv("data.csv", index_col=0)
entries = len(data[data.Return != 0])
print(entries)
print(sum(data["Return"])/len(data[data.Return != 0]))

