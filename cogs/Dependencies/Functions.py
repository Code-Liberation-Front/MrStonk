import yfinance
import pandas as pd
import numpy as np

async def stonkspull(ticker, period, interval):
    data = yfinance.download(tickers=ticker, period=period, interval=interval)
    stock = data.loc['2022-07-28']['Open']
    print(data)
    print(stock)
