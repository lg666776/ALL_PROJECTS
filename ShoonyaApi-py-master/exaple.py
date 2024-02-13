import datetime
from NorenRestApiPy.NorenApi import NorenApi
import logging
import pyotp
import pandas as pd
from datetime import datetime, timedelta


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
        global api
        api = self


# genable dbug to see request and responses
logging.basicConfig(level=logging.DEBUG)

# start of our program
Qr_code = '4M4I4T6A63G22WRV64W2X546M44OK656'
api = ShoonyaApiPy()
otp = pyotp.TOTP(Qr_code).now()

# credentials
user = 'FA87766'
pwd = 'Lg666776@500'
factor2 = otp
vc = 'FA87766_U'
app_key = 'ed5b4b44cf139d74b2a5b4ff7480ad48'
imei = 'abc1234'

# make the api call
ret = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)


# Code A
def get_time_series(exchange, token, start_time, end_time, interval):
    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=start_time.timestamp(),
                                    endtime=end_time.timestamp(), interval=interval)
    if ret:
        candle_df = pd.DataFrame(ret, columns=['time', 'inth', 'intl', 'intc', 'intv', 'intvwap'])
        candle_df['time'] = pd.to_datetime(candle_df['time'], format='%d-%m-%Y %H:%M:%S')
        candle_df['date'] = candle_df['time'].dt.date
        candle_df.sort_values(['date', 'time'], inplace=True)
        candle_df.reset_index(drop=True, inplace=True)

        # Filter data after 9:25
        candle_df = candle_df[candle_df['time'].dt.time >= datetime.time(hour=9, minute=15)]

        # Update date after 15:25
        candle_df['date'] = candle_df['time'].apply(
            lambda x: x.date() + datetime.timedelta(days=1) if x.time() >= datetime.time(hour=15,
                                                                                         minute=25) else x.date())

        candle_df.drop(columns='date', inplace=True)

        print(candle_df)  # Print the DataFrame
        return candle_df


# Part 2: Creating new DataFrame and Printing Data
import pandas as pd


# Assuming candle_df is the DataFrame containing the data
def print_columns(df):
    # Convert columns to numeric data types
    df['inth'] = pd.to_numeric(df['inth'], errors='coerce')
    df['intl'] = pd.to_numeric(df['intl'], errors='coerce')
    df['intc'] = pd.to_numeric(df['intc'], errors='coerce')
    df['intv'] = pd.to_numeric(df['intv'], errors='coerce')

    inth_data = df['inth'].tolist()
    intl_data = df['intl'].tolist()
    intc_data = df['intc'].tolist()
    intv_data = df['intv'].tolist()
    time_data = df['time'].tolist()

    # ... (printing data or further processing)


# Part 3: Calculating VWAP and Printing vwap_df
if candle_df is not None:
    # Convert the 'time' column to datetime format
    candle_df['time'] = pd.to_datetime(candle_df['time'], format='%d-%m-%Y %H:%M:%S')

    # Set the 'time' column as the index
    candle_df.set_index('time', inplace=True)

    # Convert the relevant columns to numeric type
    candle_df['inth'] = pd.to_numeric(candle_df['inth'])
    candle_df['intl'] = pd.to_numeric(candle_df['intl'])
    candle_df['intc'] = pd.to_numeric(candle_df['intc'])
    candle_df['intv'] = pd.to_numeric(candle_df['intv'])

    # Calculate VWAP
    candle_df['TP'] = (candle_df['inth'] + candle_df['intl'] + candle_df['intc']) / 3  # Typical Price
    candle_df['PV'] = candle_df['TP'] * candle_df['intv']  # Price * Volume

    # Reset cumulative calculations for each trading day
    candle_df['CumulativePV'] = candle_df.groupby(candle_df.index.date)['PV'].cumsum()
    candle_df['CumulativeVolume'] = candle_df.groupby(candle_df.index.date)['intv'].cumsum()

    # Calculate VWAP
    candle_df['VWAP'] = candle_df['CumulativePV'] / candle_df['CumulativeVolume']

    # Create a new DataFrame with column name 'VWAP' above VWAP values
    vwap_df = pd.DataFrame({'VWAP': candle_df['VWAP']})

    print(vwap_df)
