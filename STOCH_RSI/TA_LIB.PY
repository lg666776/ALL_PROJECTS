import pandas as pd
import talib
import yfinance as yf



def rsi_talib():
    data = yf.download(tickers='TATAMOTORS.NS', period='2d', interval='5m')

    # Set Pandas display option to show all rows
    pd.set_option('display.max_rows', None)

    candle_df = data[['Open', 'High', 'Low', 'Close']].copy()
    # Round the numbers to one decimal place

    print(candle_df)

    # Use the 'Close' column from the candle_df DataFrame as price data
    close_prices = candle_df['Close']

    # Calculate RSI
    rsi_period = 14  # Adjust the period as needed
    rsi_values = talib.RSI(close_prices, timeperiod=rsi_period)

    df = pd.DataFrame(rsi_values)
    print(df)

    k = 5
    period = 14

    stoch = 100 * (df - df.rolling(period).min()) / (df.rolling(period).max() - df.rolling(period).min())
    k = stoch.rolling(k).mean()
    print(k)





rsi()

