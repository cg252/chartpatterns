import yfinance as yf

arr = yf.download("SPY", interval="1h", start="2023-01-01")

openList = arr['Open']
closeList = arr['Close']
lowList = arr['Low']
highList = arr['High']


setupDates = []
Return2d = []
Return4d = []
Return7d = []


for i in range(len(arr)-1):

    #data for current day
    deltaTD = closeList.iloc[i] - openList.iloc[i]
    percentTD = (deltaTD/openList.iloc[i])*100
    highTD = highList.iloc[i]
    openTD = openList.iloc[i]
    closeTD = closeList.iloc[i]

    #data for tomorrow
    deltaTMR = closeList.iloc[i+1] - openList.iloc[i+1]
    percentTMR = (deltaTMR/openList.iloc[i+1])*100
    lowTMR = lowList.iloc[i+1]
    openTMR = openList.iloc[i+1]
    closeTMR = closeList.iloc[i+1]


    #criteria 

    if (deltaTD < 0) and (deltaTMR > 0) and (deltaTMR > 1.25*abs(deltaTD)) and (openTMR <= closeTD) and (closeTMR > openTD) and percentTMR > 0.3:

        setupDates.append(i)
        
        print(arr.iloc[i])

        #see how price behaves after trigger
        try:
            Return2d.append(((closeList.iloc[i+4]-openList.iloc[i+2])/openList.iloc[i+2])*100)
            Return4d.append(((closeList.iloc[i+6]-openList.iloc[i+2])/openList.iloc[i+2])*100)
            Return7d.append(((closeList.iloc[i+9]-openList.iloc[i+2])/openList.iloc[i+2])*100)
        except:
            print("No return data for " + str(i))



