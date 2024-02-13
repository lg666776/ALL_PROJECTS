import yfinance as yf
import pandas as pd
import time
import threading
from datetime import datetime
import datetime


def fetch_candle_data_loop():

    interval = 5

    while True:
        data = yf.download(tickers='^BSESN', period='1d', interval='5m')

        # Set Pandas display option to show all rows
        pd.set_option('display.max_rows', None)
        
        candle_df = data[['Open', 'High', 'Low', 'Close']].copy()
        
        candle_df = candle_df.round(1)
        
        intc_column = candle_df['Close']
        
        if not intc_column.empty:
            latest_intc_value = intc_column.iloc[-1]
            
            print("Latest 'into' value:", latest_intc_value)
        else:
            print("DataFrame is empty.")



        # Wait for the next 5-minute mark
        next_update_time = get_next_interval_mark(interval)
        time_to_sleep = (next_update_time - datetime.datetime.now()).total_seconds()
        time.sleep(time_to_sleep)


def get_next_interval_mark(interval):
    now = datetime.datetime.now()
    current_minute = now.minute
    remainder = current_minute % interval
    if remainder == 0:
        next_interval_mark = now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=interval)
    else:
        next_interval_mark = now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=interval - remainder)


    return next_interval_mark


if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    
    fetch_candle_data_thread = threading.Thread(target=fetch_candle_data_loop)
   
    fetch_candle_data_thread.start()
   
