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
import schedule

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


def process_candle_df(candle_df):

    print(candle_df)

    # Extract highest value of 'inth'
    highest_inth = candle_df['inth'].max()
    highest_inth = float(highest_inth)
    print(f'Highest inth value: {highest_inth}')
    with open('nifty_high.txt', 'w') as file:
        file.write(str(highest_inth))


    # Extract lowest value of 'intl'
    lowest_intl = candle_df['intl'].min()
    lowest_intl = float(lowest_intl)
    print(f'Lowest intl value: {lowest_intl}')
    with open('nifty_low.txt', 'w') as file:
        file.write(str(lowest_intl))


    points_diff = highest_inth - lowest_intl
    print(f'Point Diff: {points_diff}')

    prc = points_diff / 20000 * 100
    print(prc)

    if prc < 15 or prc == 15:
        prem = 50
        with open('premimum.txt', 'w') as file:
            file.write(str(prem))
    elif prc > 15 and prc <= 30:
        prem = 40
        with open('premimum.txt', 'w') as file:
            file.write(str(prem))
    elif prc > 30 and prc <= 40:
        prem = 30
        with open('premimum.txt', 'w') as file:
            file.write(str(prem))
    elif prc > 40:
        prem = 20
        with open('premimum.txt', 'w') as file:
            file.write(str(prem))


def high_low_fetch():
   
    # Calculate the date 5 days ago from the current date
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')

    print(current_date)
    
    # Define the start and end times for the 5-minute candles
    start_time = datetime.datetime.strptime(f'{current_date} 09:26:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 09:35:00', '%d-%m-%Y %H:%M:%S')
    
    # Fetch candle data (replace this with your implementation)
    candle_df = get_time_series('NSE', '26000', start_time, end_time, interval=1)
    
    if candle_df is not None:
        process_candle_df(candle_df)


high_low_fetch()
