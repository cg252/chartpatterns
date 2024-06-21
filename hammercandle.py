import yfinance as yf

arr = yf.download("SPY", period="max", interval="1d", start="2022-01-01")

openList = arr['Open']
closeList = arr['Close']
lowList = arr['Low']
highList = arr['High']
highlowList = arr['High'] - arr['Low']


setupDates = []
Return2d = []
Return4d = []
Return7d = []


for i in range(len(arr)-1):

    #data for current day
    deltaTD = closeList.iloc[i] - openList.iloc[i]
    highlowTD = highlowList.iloc[i]
    percentTD = (deltaTD/openList.iloc[i])*100
    highTD = highList.iloc[i]
    lowTD = lowList.iloc[i]
    openTD = openList.iloc[i]
    closeTD = closeList.iloc[i]

    avgMovePast5d = (abs(highlowList.iloc[i-1])+abs(highlowList.iloc[i-2])+abs(highlowList.iloc[i-3])+abs(highlowList.iloc[i-4])+abs(highlowList.iloc[i-5]))/5

    correlationFactor = highlowTD/avgMovePast5d
    #over 1 is good ? 

    #criteria 
    if (deltaTD > 0) and ((openTD-lowTD) > 2*(deltaTD)) and (abs(highTD-closeTD) < 0.1*(highTD-lowTD)):


        setupDates.append(i)
        
        print(arr.iloc[i])
        print(highlowTD)
        print(avgMovePast5d)
        print((highlowTD/avgMovePast5d))



