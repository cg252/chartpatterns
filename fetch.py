import json
import yfinance as yf
import time

while True:
    historical_prices = yf.Ticker('EURUSD=X').history(period='1d', interval='1m')
    # Get the latest price and time
    latest_price = historical_prices['Close'].iloc[-1]
    latest_time = historical_prices.index[-1].strftime('%H:%M')

    newdata = {
        latest_time: {
            "Price": latest_price,
            "TSI": '5',
            "TSI_Signal": '5'
        }
        }

    with open('data.json') as file:
        olddata = json.load(file)
    

    olddata.update(newdata)

    with open("data.json", 'w') as file:
        json.dump(olddata, file)

    time.sleep(5)


