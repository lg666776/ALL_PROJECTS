from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import math
import time
import pandas as pd  


ce_token_read = 0

global api

# Credentials
user = open('user.txt', 'r').read()
pwd = open('pass.txt', 'r').read()


def login():
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                              websocket='wss://api.shoonya.com/NorenWSTP/')

    api = ShoonyaApiPy()
    # Make the API call
    # res = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)
    session_token = open('session_token.txt', 'r').read()
    api.set_session(user, pwd, session_token)
    # Get the current time
    current_time = datetime.datetime.now().time()
    print('CE OHLC LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()
    

def atm_loop():
    global ce_token_read
 
    while True:
        try:
            with open('ce_token.txt', 'r') as file:
                ce_token_read = file.read()
                
        except FileNotFoundError:
            ce_token_read = None
            print('NO CE TOKEN')
           
        time.sleep(0.01)



def get_time_series(exchange, token, start_time, end_time, interval):
    global candle_df
    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=start_time.timestamp(),
                                    endtime=end_time.timestamp(), interval=interval)
    if ret:
        candle_df = pd.DataFrame(ret, columns=['time', 'inth', 'intl', 'intc', 'into', 'intvwap'])
        candle_df['time'] = pd.to_datetime(candle_df['time'], format='%d-%m-%Y %H:%M:%S')
        candle_df['date'] = candle_df['time'].dt.date
        candle_df.sort_values(['date', 'time'], inplace=True)
        candle_df.reset_index(drop=True, inplace=True)
        # Filter data after 9:25
        candle_df = candle_df[candle_df['time'].dt.time >= datetime.time(hour=9, minute=15)]


        # Update date after 15:25
        candle_df['date'] = candle_df['time'].apply(
            lambda x: x.date() + datetime.timedelta(days=1) if x.time() >= datetime.time(hour=15,
                                                                                         minute=30) else x.date())

        candle_df.drop(columns='date', inplace=True)
        candle_df.set_index('time', inplace=True)
        candle_df.reset_index()

        return candle_df


def print_candle_df(candle_df):


    # Extract the 'into' column
    intc_column = candle_df['intc']

    print(intc_column)

    # Check if there are any rows in the DataFrame
    if not intc_column.empty:
        # Extract the latest 'into' value
        latest_intc_value = intc_column.iloc[-1]

        with open('ce_closing_prc.txt', 'w') as file:
            file.write(latest_intc_value)
        
        with open('ce_closing_prc.txt', 'r') as file:
            ce_closing_price = file.read()
            
        # Print the latest 'into' value
        print("Latest 'intc' value:", latest_intc_value)
    else:
        print("DataFrame is empty.")


def fetch_candle_data_loop():
    global ce_token_read

    # Calculate the date 5 days ago from the current date
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    five_days = five_days_ago.strftime('%d-%m-%Y')

    # Define the start and end times for the 5-minute candles
    start_time = datetime.datetime.strptime(f'{five_days} 09:15:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 15:30:00', '%d-%m-%Y %H:%M:%S')

    while True:
        # Calculate the date and time for the next minute
        current_time = datetime.datetime.now()
        next_minute = (current_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)

        # Calculate the seconds remaining until the next minute
        seconds_remaining = (next_minute - current_time).total_seconds()

        # Sleep until the next minute
        time.sleep(seconds_remaining + 2)  # Sleep until the next minute + 5 seconds

        # Fetch candle data (replace this with your implementation)
        candle_df = get_time_series('NFO', ce_token_read, start_time, end_time, interval=1)

        if candle_df is not None:
            print_candle_df(candle_df)


if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    
    fetch_candle_data_thread = threading.Thread(target=fetch_candle_data_loop)
    amt_loop_thread = threading.Thread(target=atm_loop)
    fetch_candle_data_thread.start()
    amt_loop_thread.start()
