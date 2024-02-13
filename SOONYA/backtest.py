from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import pandas as pd
import time
import threading
import datetime

# TCS = 11536, TATAM = 3456, WIPRO = 3787, SBIN = 3045, INFY = 1594, INDUSINDBK = 5258, BAJFINANCE = 317, ITC = 1660,
# NBCC = 31415
global api

# Credentials
user = 'FA87766'
pwd = 'Lg666776@500'


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
    print('TATA MOTORS LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()


def get_time_series(exchange, token, start_time, end_time, interval):
    global candle_df
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
                                                                                         minute=30) else x.date())

        candle_df.drop(columns='date', inplace=True)
        candle_df.set_index('time', inplace=True)
        candle_df.reset_index()

        return candle_df


def print_candle_df(candle_df):
    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Print the 'time' and other columns of the candle_df DataFrame
    print(candle_df_reset[['time', 'inth', 'intl', 'intc', ]])

    # Set the 'time' column as the index again
    candle_df_reset.set_index('time', inplace=True)


def calculate_vwap(candle_df):
    global vwap_df
    candle_df.reset_index()

    candle_df = candle_df[['inth', 'intl', 'intc', 'intv']].copy()

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

    candle_df['VWAP'] = candle_df['CumulativePV'] / candle_df['CumulativeVolume']

    # Create a new DataFrame with column name 'VWAP' above VWAP values
    vwap_df = pd.DataFrame({'VWAP': candle_df['VWAP']})

    print(vwap_df)

    return vwap_df


def check_buy_entry_conditions(candle_df, vwap_df):

    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['inth'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['intl'], errors='coerce')

    # Convert 'VWAP' column in vwap_df to numeric
    vwap_df['VWAP'] = pd.to_numeric(vwap_df['VWAP'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    store_high = None
    sell_exit = None
    # Loop through each candle data starting from 9:15 AM

    for i in range(len(candle_df_reset)):
        # Check for the condition of low (intl) above VWAP
        if candle_df_reset['intl'].iloc[i] > vwap_df['VWAP'].iloc[i]:
            if store_high is None:
                store_high = candle_df_reset['inth'].iloc[i]

                print(
                    f"Buy condition satisfied at {candle_df_reset['time'].iloc[i]}. Candle Low: {candle_df_reset['intl'].iloc[i]}, Stored High Price: {store_high}")

        elif store_high is not None and candle_df_reset['inth'].iloc[i] < vwap_df['VWAP'].iloc[i]:
            # If a candle with high below VWAP is found, set the sell_exit point and reset the stored high price
            store_high = None
            print(f"Stored High Price removed at {candle_df_reset['time'].iloc[i]}.")

            print('.....................................................................................')


def tatam_fetch_candle_data_loop():
    current_date = '24-08-2023'

    # Define the time interval for the 5-minute candles on the current date
    start_time = datetime.datetime.strptime(f'{current_date} 09:15:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 15:30:00', '%d-%m-%Y %H:%M:%S')

    interval = 10

    while True:
        # Fetch candle data (replace this with your implementation)
        candle_df = get_time_series('NSE', '3456', start_time, end_time, interval=10)

        if candle_df is not None:
            # Process the data (replace this with your implementation)
            print_candle_df(candle_df)
            calculate_vwap(candle_df)
            check_buy_entry_conditions(candle_df, vwap_df)

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

    # Add 5 minutes to the next interval mark
    next_interval_mark += datetime.timedelta(minutes=5)

    return next_interval_mark


if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    fetch_candle_data_thread = threading.Thread(target=tatam_fetch_candle_data_loop)

    # Start the threads

    fetch_candle_data_thread.start()

    # Wait for all threads to complete
    fetch_candle_data_thread.join()
