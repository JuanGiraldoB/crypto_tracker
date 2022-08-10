import pandas as pd
from binance import Client
from tracker.models import Symbol, PriceData
import csv

client = Client()

def get_min_data(symbol, start):
    frame = pd.DataFrame(client.get_historical_klines(symbol, "1m", start))

    frame = frame[[0,1,2,3,4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame.Date = pd.to_datetime(frame.Date, unit="ms")
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    i = 0
    for row in frame.itertuples():
        print(row[0], row[1], row[2], row[3], row[4])
        if i == 5:
            break
        i += 1
    return frame

def run():

    Symbol.objects.all().delete()

    with open('tracker/crypto_symbols.csv') as file:
        datareader = csv.reader(file)
        next(datareader, None) 

        for row in datareader:
            print(row)

            s, created = Symbol.objects.get_or_create(symbol=row[1])
            print(created)
            print(row[1])
                
            df = get_min_data(row[1], '1 days ago UTC-5')

            for row in df.itertuples():
                p_d = PriceData(symbol=s, date=row[0], open=row[1], high=row[2], low=row[3], close=row[4])
                p_d.save()
