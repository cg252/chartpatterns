import yfinance as yf

arr = yf.download("NG=F", period="max", interval="1d", start="1950-01-01", actions="False")

openList = arr['Open']
closeList = arr['Close']
lowList = arr['Low']
highList = arr['High']

setupDates = []
Return3d = []
Return5d = []
Return7d = []
Return10d = []

for i in range(len(arr)-2):

    #data for current day
    deltaTD = closeList.iloc[i] - openList.iloc[i]
    percentTD = (deltaTD/openList.iloc[i])*100
    highTD = highList.iloc[i]

    #data for tomorrow
    deltaTMR = closeList.iloc[i+1] - openList.iloc[i+1]
    percentTMR = (deltaTMR/openList.iloc[i+1])*100
    lowTMR = lowList.iloc[i+1]
    openTMR = openList.iloc[i+1]
    closeTMR = closeList.iloc[i+1]

    #data for ovm or overmorrow
    deltaOVM = closeList.iloc[i+2] - openList.iloc[i+2]
    percentOVM = (deltaOVM/openList.iloc[i+2])*100
    lowOVM = lowList.iloc[i+2]
    openOVM = openList.iloc[i+2]

    #criteria for 3 white soldiers: 3 green days, second day better than first and its close is near previous day high

    if (deltaTD > 0) and (deltaTMR > 0) and (abs((closeTMR-highTD)/closeTMR) < 0.0035) and (lowOVM > lowTMR) and (deltaOVM > (1.8*deltaTMR)) and (percentOVM > 0.4):
        setupDates.append(i)
        
        #print(arr.iloc[i])

        #see how price behaves after trigger
        try:
            Return3d.append(((closeList.iloc[i+3]-openList.iloc[i])/openList.iloc[i])*100)
            Return5d.append(((closeList.iloc[i+5]-openList.iloc[i])/openList.iloc[i])*100)
            Return7d.append(((closeList.iloc[i+7]-openList.iloc[i])/openList.iloc[i])*100)
            Return10d.append(((closeList.iloc[i+10]-openList.iloc[i])/openList.iloc[i])*100)
        except:
            print("No return data for " + str(i))

#print(Return3d)

avg3d = round(sum(Return3d)/len(Return3d), 2)
avg5d = round(sum(Return5d)/len(Return5d), 2)
avg7d = round(sum(Return7d)/len(Return7d), 2)
avg10d = round(sum(Return10d)/len(Return10d), 2)

print(str(len(Return3d)) + ' Cases found')
print('Average 3 day return: ' + str(avg3d) + ' %')
print('Average 5 day return: ' + str(avg5d) + ' %')
print('Average 7 day return: ' + str(avg7d) + ' %')
print('Average 10 day return: ' + str(avg10d) + ' %')


