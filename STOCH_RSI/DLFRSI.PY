from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import requests

rsi_values = None
formatted_rsi = None
smoothed_stoch_rsi_k = None
store_high = None
store_low = None
formatted_buy_sl = 0
formatted_buy_tgt = 0
formatted_sell_sl = 0
formatted_sell_tgt = 0
sell_avgprc = 0
buy_avgprc = 0
buy_sl = 0
buy_tgt = 0
sell_sl = 0
sell_tgt = 0
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
    print('DLF LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()

dlf_lp_value = 0
dlf_quantity = []
order_status_counts = {}
buy_order_quantity = None
sell_order_quantity = None
sell_order_placed = None
buy_order_placed = None
last_update_time = None
store_high_sell = None
sell_exit_point = None
last_order_book = None
buy_exit_point = None
store_low_sell = None
total_count = 0
exit1_orderno = None
exit2_orderno = None
exit3_orderno = None
exit1_sell_orderno = None
exit2_sell_orderno = None
exit3_sell_orderno = None

TRADE_DETAILS_FILE = 'dlfrsi_trade_details.pkl'
SELL_TRADE_DETAILS_FILE = 'dlfrsi_sell_trade_details.pkl'
BUY_ORDER_DETAILS_FILE = 'dlfrsi_buy_order_details.pickle'
SELL_ORDER_DETAILS_FILE = 'dlfrsi_sell_order_details.pickle'
EXIT1_BUY_ORDER_DETAILS_FILE = 'dlfrsi_exit1_buy_order_details.pickle'
EXIT2_BUY_ORDER_DETAILS_FILE = 'dlfrsi_exit2_buy_order_details.pickle'
EXIT3_BUY_ORDER_DETAILS_FILE = 'dlfrsi_exit3_buy_order_details.pickle'
EXIT1_SELL_ORDER_DETAILS_FILE = 'dlfrsi_exit1_sell_order_details.pickle'
EXIT2_SELL_ORDER_DETAILS_FILE = 'dlfrsi_exit2_sell_order_details.pickle'
EXIT3_SELL_ORDER_DETAILS_FILE = 'dlfrsi_exit3_sell_order_details.pickle'


def load_data(file_path, initialize_empty_dict=False, initialize_empty_set=False, max_retries=100, retry_delay=3):
    for retry in range(max_retries):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    return pickle.load(file)
        except (FileNotFoundError, pickle.UnpicklingError) as e:
            if retry < max_retries - 1:
                time.sleep(retry_delay)
    if initialize_empty_dict:
        return {}
    elif initialize_empty_set:
        return set()


def save_data(file_path, data):
    with open(file_path, 'wb') as file:
        try:
            # Attempt to pickle the data
            pickle.dump(data, file)
        except Exception as e:
            # Print an error message and simulate a pickling error
            raise


# Load data with initializing empty dictionaries for all variables
trade_details_file: dict = load_data(TRADE_DETAILS_FILE, initialize_empty_dict=True)
sell_trade_details_file: dict = load_data(SELL_TRADE_DETAILS_FILE, initialize_empty_dict=True)
sell_order_details: dict = load_data(SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
buy_order_details: dict = load_data(BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit1_buy_order_details: dict = load_data(EXIT1_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit2_buy_order_details: dict = load_data(EXIT2_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit3_buy_order_details: dict = load_data(EXIT3_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit1_sell_order_details: dict = load_data(EXIT1_SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit2_sell_order_details: dict = load_data(EXIT2_SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit3_sell_order_details: dict = load_data(EXIT3_SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)


def get_order_book_loop():
    global last_order_book, total_count

    time.sleep(3)  # Initial sleep before starting to print counts

    retry_delay = 3  # Retry delay in seconds
    unique_norenordnos = set()  # Initialize set to keep track of unique norenordnos

    while True:
        try:
            ret = api.get_order_book()

            if ret is not None and ret != last_order_book:  # Check if 'ret' is not None and data has changed
                for item in ret:
                    status = item.get('status', 'Status not found')
                    tsym = item.get('tsym', 'Symbol not found')
                    norenordno = item.get('norenordno', 'norenordno not found')

                    if status == 'COMPLETE' and tsym == 'DLF-EQ' and norenordno not in unique_norenordnos:
                        # Increment the count for the norenordno if it exists in the dictionary
                        order_status_counts[norenordno] = order_status_counts.get(norenordno, 0) + 1
                        unique_norenordnos.add(norenordno)

                total_count = sum(order_status_counts.values())  # Calculate the total count again

            last_order_book = ret  # Update the last order book data

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
            # Handle connection or read timeouts

            time.sleep(retry_delay)

        except Exception as e:
            # Handle other unexpected exceptions

            time.sleep(retry_delay)

        time.sleep(60)  # Sleep for 5 seconds at the end of the loop


def ltp_quantity_loop():
    global dlf_lp_value, dlf_quantity
    while True:
        try:
            # Read data from data_titan.pickle
            with open('data_dlf.pickle', 'rb') as file:
                try:
                    data_dlf = pickle.load(file)
                    if isinstance(data_dlf, dict):
                        dlf_lp_value = data_dlf.get('dlf_lp_value')
                        dlf_quantity = data_dlf.get('dlf_quantity')


                except EOFError:
                    # Reset the titan_lp_value and titan_quantity to None if EOFError
                    dlf_lp_value = 0

        except FileNotFoundError:
            dlf_lp_value = 0

        except Exception as e:
            dlf_lp_value = 0

        time.sleep(0.2)  # Adjust the interval as needed


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

    # Set the 'time' column as the index again
    candle_df_reset.set_index('time', inplace=True)

    # Convert the 'intc' column to numeric if it contains string values
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')


def calculate_rsi(candle_df, n=14):
    global rsi_values
    candle_df.reset_index(drop=True)

    candle_df = candle_df[['inth', 'intl', 'intc']].copy()

    # Reset the index to ensure consistent indexing
    candle_df.reset_index(drop=True, inplace=True)

    # Convert the 'intc' column to numeric if it contains string values
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')

    # Replace this with your actual price data from candle_df
    close_prices = candle_df['intc']

    period = 14  # You can change this to your desired period

    # Calculate price changes
    candle_df['price_change'] = candle_df['intc'].diff()

    # Calculate gains (positive price changes) and losses (negative price changes)
    candle_df['gain'] = candle_df['price_change'].apply(lambda x: x if x > 0 else 0)
    candle_df['loss'] = candle_df['price_change'].apply(lambda x: -x if x < 0 else 0)

    # Calculate average gains and average losses over the specified period
    avg_gain = candle_df['gain'][:period].mean()
    avg_loss = candle_df['loss'][:period].mean()

    # Calculate RS (Relative Strength) for the first RSI value
    rs = avg_gain / avg_loss

    # Calculate RSI for the first period
    rsi = 100 - (100 / (1 + rs))

    # Create lists to store RSI values
    rsi_values = [rsi]

    # Create a list to store RSI values with NaN for the first 14 periods
    rsi_values = [None] * period

    # Calculate RSI for the remaining periods
    for i in range(period, len(candle_df)):
        price_change = candle_df['price_change'][i]
        gain = price_change if price_change > 0 else 0
        loss = -price_change if price_change < 0 else 0

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)

        # Create a DataFrame with 'time' and 'smoothk' columns to store the RSI values
    result_df = pd.DataFrame({'smoothk': rsi_values})

    # Set Pandas display option to show all rows
    pd.set_option('display.max_rows', None)


def calculate_stoch_rsi(stoch_period=14, smoothing_period=5):
    global rsi_values, formatted_rsi, smoothed_stoch_rsi_k

    # Calculate the RSI's highest high and lowest low over the StochRSI period
    rsi_high = pd.Series(rsi_values).rolling(window=stoch_period).max()
    rsi_low = pd.Series(rsi_values).rolling(window=stoch_period).min()

    # Calculate the StochRSI %K value
    stoch_rsi_k = (pd.Series(rsi_values) - rsi_low) / (rsi_high - rsi_low)

    # Apply smoothing using a simple moving average (SMA)
    smoothed_stoch_rsi_k = stoch_rsi_k.rolling(window=smoothing_period).mean()

    # Create a DataFrame to store time and smoothed StochRSI %K values
    result_df = pd.DataFrame(
        {'time': pd.date_range(start='2023-09-26 09:15:00', periods=len(smoothed_stoch_rsi_k), freq='5T'),
         'smoothk': smoothed_stoch_rsi_k})

    # Assuming you already have the `smoothed_stoch_rsi_k` series from your function

    latest_smoothed_stoch_rsi_k = smoothed_stoch_rsi_k.iloc[-1]  # Get the latest smoothed StochRSI %K value

    # Convert to a formatted percentage string
    formatted_rsi = "{:.2f}".format(latest_smoothed_stoch_rsi_k * 100)

    return formatted_rsi, smoothed_stoch_rsi_k


def calculate_atr(candle_df, period=14):
    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['inth'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['intl'], errors='coerce')

    atr_values = []  # List to store ATR values

    for i in range(len(candle_df)):
        if i == 0:
            atr_values.append(candle_df['inth'].iloc[i] - candle_df['intl'].iloc[i])
        else:
            tr = max(candle_df['inth'].iloc[i] - candle_df['intl'].iloc[i],
                     abs(candle_df['inth'].iloc[i] - candle_df['intc'].iloc[i - 1]),
                     abs(candle_df['intl'].iloc[i] - candle_df['intc'].iloc[i - 1]))
            atr_values.append((atr_values[-1] * (period - 1) + tr) / period)

    # Create a DataFrame with 'time' and 'smoothk' columns to store the RSI values
    atr_df = pd.DataFrame({'atr': atr_values})

    return atr_df


def check_buy_entry_conditions(candle_df, atr_df):
    global formatted_rsi, smoothed_stoch_rsi_k, store_high, trade_details_file, formatted_buy_sl, formatted_buy_tgt

    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['inth'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['intl'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Find the index of the data point corresponding to 9:15 AM
    start_time_index = candle_df_reset.index[candle_df_reset['time'] == '09:15'].tolist()
    if not start_time_index:
        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    # Initialize a variable to keep track of the previous value of formatted_rsi_float
    prev_formatted_rsi_float = None

    # Initialize the store_low variable
    store_high = None
    atr = 0

    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check if the index 'i' is within the valid range of smoothed_stoch_rsi_k
        if 0 <= i < len(smoothed_stoch_rsi_k):
            # Access a specific element in the Series and convert it to a float
            formatted_rsi_float = float(smoothed_stoch_rsi_k.iloc[i])

            if prev_formatted_rsi_float is not None:
                if prev_formatted_rsi_float <= 0.30 and formatted_rsi_float > 0.30:
                    # Buy condition: RSI crosses above 30 from below 30
                    # Define your buy entry logic here
                    buy_entry_condition = True  # Modify this as needed

                    if buy_entry_condition:
                        # This is where you execute your buy action
                        store_high = candle_df_reset['inth'].iloc[i]
                        atr = atr_df['atr'].iloc[i]
                        # Format to display only two decimal places
                        formatted_atr = "{:.2f}".format(atr)

                        # Convert formatted_atr to a float if it's not already
                        formatted_atr = float(formatted_atr)
                        sl = formatted_atr
                        tgt = formatted_atr * 3

                        # Convert sl and tgt to strings with two decimal places
                        formatted_buy_sl = "{:.2f}".format(sl)
                        formatted_buy_tgt = "{:.2f}".format(tgt)

                elif prev_formatted_rsi_float >= 0.70 and formatted_rsi_float < 0.70:
                    store_high = None
                    atr = 0

                elif prev_formatted_rsi_float >= 0.30 and formatted_rsi_float < 0.30:
                    store_high = None
                    atr = 0

            # Update the previous value with the current value
            prev_formatted_rsi_float = formatted_rsi_float


def buy_sl_tgt_loop():
    global formatted_buy_sl, formatted_buy_tgt, buy_order_details, trade_details_file, buy_order_details, buy_avgprc, buy_sl, buy_tgt
    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_avgprc_str = order_info.get('buy_avgprc', '0')  # Default to '0' if missing or not a number
            buy_avgprc = float(buy_avgprc_str)  # Convert to float

            # Convert bsl and btgt to floats
            formatted_buy_sl = float(formatted_buy_sl)
            formatted_buy_tgt = float(formatted_buy_tgt)

            buy_stop_loss = buy_avgprc - formatted_buy_sl
            buy_target = buy_avgprc + formatted_buy_tgt

            # Convert sl and tgt to strings with two decimal places
            formatted_buy_stoploss = "{:.2f}".format(buy_stop_loss)
            formatted_buy_target = "{:.2f}".format(buy_target)

            # Create a dictionary to store these values
            trade_details = {
                'Buy_SL': formatted_buy_stoploss,
                'Buy_Target': formatted_buy_target
            }
            # Assign values to the keys in trade_details_file
            trade_details_file.update(trade_details)
            save_data(TRADE_DETAILS_FILE, trade_details_file)

            buy_sl = trade_details_file.get('Buy_SL', 0)
            buy_tgt = trade_details_file.get('Buy_Target', 0)


def execute_buy_trade():
    global dlf_quantity, buy_order_details

    # If the current time is later than or equal to the desired execution time, execute the buy order
    ret = api.place_order(buy_or_sell='B', product_type='I',
                          exchange='NSE', tradingsymbol='DLF-EQ',
                          quantity=dlf_quantity, discloseqty=0, price_type='MKT',
                          retention='DAY', remarks='my_order_001')

    # Extract the orderno from the ret value
    orderno = ret['norenordno']

    order_history = api.single_order_history(orderno=orderno)

    if order_history:
        # Check the order status
        status = order_history[0].get('status')

        if status == 'COMPLETE':
            # Fetch the order timestamp
            order_timestamp = order_history[0].get('norentm')
            order_quantity = order_history[0].get('qty')
            avgprc = order_history[0].get('avgprc')

            # Check if the order has not been processed before
            if orderno not in buy_order_details:
                # Store the details in the global dictionary
                buy_order_details[orderno] = {
                    'Status': 'COMPLETE',
                    'Timestamp': order_timestamp,
                    'Quantity': order_quantity,
                    'buy_avgprc': avgprc,
                    'trantype': 'B',  # Add custom field trantype with value "B" (Buy)
                    'remarks': 'my_order_001',  # Add custom field remarks to identify the buy order
                }
                # Save the updated buy_order_details dictionary to a file after removing the item
                save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)

    # Return the order details dictionary
    return buy_order_details


def execute_exit_trade_1():
    global buy_order_details, exit1_buy_order_details, exit1_orderno
    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NSE', tradingsymbol='DLF-EQ',
                                  quantity=buy_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_001')

            # Extract the orderno from the ret value
            exit1_orderno = ret['norenordno']

            order_history = api.single_order_history(orderno=exit1_orderno)

            if order_history:
                # Check the order status
                status = order_history[0].get('status')

                if status == 'COMPLETE':

                    # Check if the order has not been processed before
                    if exit1_orderno not in exit1_buy_order_details:
                        # Store the details in the global dictionary
                        exit1_buy_order_details[exit1_orderno] = {
                            'Status': 'COMPLETE',
                            'trantype': 'B',  # Add custom field trantype with value "B" (Buy)
                            'remarks': 'my_order_001',  # Add custom field remarks to identify the buy order
                        }
                        # Save the updated exit buy_order_details dictionary to a file after removing the item
                        save_data(EXIT1_BUY_ORDER_DETAILS_FILE, exit1_buy_order_details)

    # Return the order details dictionary
    return exit1_buy_order_details


def execute_exit_trade_2():
    global buy_order_details, exit2_buy_order_details, exit2_orderno, buy_order_quantity
    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NSE', tradingsymbol='DLF-EQ',
                                  quantity=buy_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_001')

            # Extract the orderno from the ret value
            exit2_orderno = ret['norenordno']

            order_history = api.single_order_history(orderno=exit2_orderno)

            if order_history:
                # Check the order status
                status = order_history[0].get('status')

                if status == 'COMPLETE':

                    # Check if the order has not been processed before
                    if exit2_orderno not in exit2_buy_order_details:
                        # Store the details in the global dictionary
                        exit2_buy_order_details[exit2_orderno] = {
                            'Status': 'COMPLETE',
                        }
                        # Save the updated exit buy_order_details dictionary to a file after removing the item
                        save_data(EXIT2_BUY_ORDER_DETAILS_FILE, exit2_buy_order_details)

    # Return the updated exit2_buy_order_details dictionary
    return exit2_buy_order_details


def exit_trade_1515():
    global buy_order_details, exit3_buy_order_details, exit3_orderno

    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to 14:55, execute the sell order
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NSE', tradingsymbol='DLF-EQ',
                                  quantity=buy_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_001')

            # Extract the orderno from the ret value
            exit3_orderno = ret['norenordno']

            # Verify order history here (similar to other exit_trade functions)
            order_history = api.single_order_history(orderno=exit3_orderno)
            if order_history:
                status = order_history[0].get('status')
                if status == 'COMPLETE':
                    # Check if the order has not been processed before
                    if exit3_orderno not in exit3_buy_order_details:
                        # Store the details in the global dictionary
                        exit3_buy_order_details[exit3_orderno] = {
                            'Status': 'COMPLETE',
                        }
                        # Save the updated exit3 buy_order_details dictionary to a file after removing the item
                        save_data(EXIT3_BUY_ORDER_DETAILS_FILE, exit3_buy_order_details)

    return exit3_buy_order_details


def buy_condition_check():
    global dlf_lp_value, store_high, sell_order_details, order_status_counts, total_count, buy_order_details

    max_retries = 5
    retries = 0

    while retries < max_retries:
        if dlf_lp_value != 0 and store_high is not None:
            if isinstance(dlf_lp_value, (int, float)) and isinstance(store_high, (int, float)):
                entry_price = store_high
                if dlf_lp_value >= entry_price and dlf_lp_value < (entry_price + 0.4):
                    if not buy_order_details:  # Check if buy_order_details is empty
                        if not sell_order_details:  # Check if sell_order_details is empty
                            # Check if the current time is before 14:20
                            current_time = datetime.datetime.now().time()
                            if current_time < datetime.time(14, 30):
                                if total_count <= 3:
                                    buy_order_details = execute_buy_trade()
                                    time.sleep(0.1)
                                    buy_sl_tgt_loop()
                                    time.sleep(0.1)
                                    buy_sl_tgt_loop()
                                    time.sleep(0.1)
                                    buy_sl_tgt_loop()
                                    save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                    if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                                           for orderno, order_info in buy_order_details.items()):
                                        save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)

                                    else:

                                        retries += 1
                                        break
        # Adjust the interval as needed
        time.sleep(0.5)


def exit_trade_1_loop():
    global buy_order_details, dlf_lp_value, exit1_buy_order_details, exit1_orderno, trade_details_file, buy_sl

    # Initialize the exit1_order_executed flag outside the loop
    exit1_order_details = False

    while True:
        if not buy_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    # Check if the current time is less than 15:15
                    if current_time < datetime.time(15, 15):
                        dlf_lp_value = float(dlf_lp_value)
                        buy_stoploss = float(buy_sl)
                        # Check if both values are not equal to 0 before comparison
                        if dlf_lp_value != 0 and buy_stoploss != 0:
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if dlf_lp_value <= buy_stoploss:
                                # Call the exit trade function here
                                execute_exit_trade_1()
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       exit1_orderno, order_info in exit1_buy_order_details.items()):
                                    exit1_order_details = True
                                    buy_order_details.pop(orderno)
                                    exit1_buy_order_details.pop(exit1_orderno)
                                    trade_details_file.clear()
                                    buy_order_details.clear()
                                    save_data(TRADE_DETAILS_FILE, trade_details_file)
                                    save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                    save_data(EXIT1_BUY_ORDER_DETAILS_FILE, exit1_buy_order_details)
                                    break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.3)


def exit_trade_2_loop():
    global buy_order_details, dlf_lp_value, exit2_buy_order_details, exit2_orderno, trade_details_file, buy_tgt

    # Variable to track whether the exit2 order has been executed
    exit2_order_details = False

    while True:
        if not buy_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    # Check if the current time is less than 15:15
                    if current_time < datetime.time(15, 15):
                        dlf_lp_value = float(dlf_lp_value)
                        buy_tgt = float(buy_tgt)
                        # Check if both values are not equal to 0 before comparison
                        if dlf_lp_value != 0 and buy_tgt != 0:
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if dlf_lp_value >= buy_tgt:
                                # Call the exit trade function here
                                execute_exit_trade_2()
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       exit2_orderno, order_info in exit2_buy_order_details.items()):
                                    exit2_order_details = True
                                    buy_order_details.pop(orderno)
                                    exit2_buy_order_details.pop(exit2_orderno)
                                    trade_details_file.clear()
                                    buy_order_details.clear()
                                    save_data(TRADE_DETAILS_FILE, trade_details_file)
                                    save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                    save_data(EXIT2_BUY_ORDER_DETAILS_FILE, exit2_buy_order_details)
                                    break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.3)


def exit_trade_1515_loop():
    global exit3_buy_order_details, buy_order_details, exit3_orderno, trade_details_file
    exit3_order_details = False

    while True:
        if not buy_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    # Check if the current time is greater than 15:15
                    if current_time > datetime.time(15, 15):
                        exit_trade_1515()
                        if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                               exit3_orderno, order_info in exit3_buy_order_details.items()):
                            exit3_order_details = True
                            buy_order_details.pop(orderno)
                            exit3_buy_order_details.pop(exit3_orderno)
                            trade_details_file.clear()
                            buy_order_details.clear()  # Clear the sell_order_details dictionary
                            save_data(TRADE_DETAILS_FILE, trade_details_file)
                            save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                            save_data(EXIT3_BUY_ORDER_DETAILS_FILE, exit3_buy_order_details)
                            break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.3)


def check_sell_entry_conditions(candle_df, atr_df):
    global formatted_rsi, smoothed_stoch_rsi_k, store_low, sell_trade_details_file, formatted_sell_sl, formatted_sell_tgt, buy_order_details, sell_order_details

    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['inth'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['intl'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Find the index of the data point corresponding to 9:15 AM
    start_time_index = candle_df_reset.index[candle_df_reset['time'] == '09:15'].tolist()
    if not start_time_index:
        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    # Initialize a variable to keep track of the previous value of formatted_rsi_float
    prev_formatted_rsi_float = None

    # Initialize the store_low variable
    store_low = None
    atr = 0

    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check if the index 'i' is within the valid range of smoothed_stoch_rsi_k
        if 0 <= i < len(smoothed_stoch_rsi_k):
            # Access a specific element in the Series and convert it to a float
            formatted_rsi_float = float(smoothed_stoch_rsi_k.iloc[i])

            if prev_formatted_rsi_float is not None:
                if prev_formatted_rsi_float >= 0.70 and formatted_rsi_float < 0.70:
                    # sell condition: RSI crosses bwlow 70 from above 70
                    # Define your buy entry logic here
                    sell_entry_condition = True  # Modify this as needed

                    if sell_entry_condition:
                        # This is where you execute your buy action
                        store_low = candle_df_reset['intl'].iloc[i]

                        atr = atr_df['atr'].iloc[i]
                        # Format to display only two decimal places
                        formatted_atr = "{:.2f}".format(atr)

                        # Convert formatted_atr to a float if it's not already
                        formatted_atr = float(formatted_atr)
                        sl = formatted_atr
                        tgt = formatted_atr * 3

                        # Convert sl and tgt to strings with two decimal places
                        formatted_sell_sl = "{:.2f}".format(sl)
                        formatted_sell_tgt = "{:.2f}".format(tgt)

                elif prev_formatted_rsi_float <= 0.30 and formatted_rsi_float > 0.30:
                    store_low = None
                    atr = 0

                elif prev_formatted_rsi_float <= 0.70 and formatted_rsi_float > 0.70:
                    store_low = None
                    atr = 0

            # Update the previous value with the current value
            prev_formatted_rsi_float = formatted_rsi_float


def sell_sl_tgt_loop():
    global formatted_sell_sl, formatted_sell_tgt, sell_order_details, sell_trade_details_file, buy_order_details, sell_avgprc, sell_sl, sell_tgt

    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing sell order
            sell_avgprc_str = order_info.get('sell_avgprc', '0')  # Default to '0' if missing or not a number
            sell_avgprc = float(sell_avgprc_str)  # Convert to float

            # Convert bsl and btgt to floats
            formatted_sell_sl = float(formatted_sell_sl)
            formatted_sell_tgt = float(formatted_sell_tgt)

            sell_stop_loss = sell_avgprc + formatted_sell_sl
            sell_target = sell_avgprc - formatted_sell_tgt

            # Convert sl and tgt to strings with two decimal places
            formatted_sell_stoploss = "{:.2f}".format(sell_stop_loss)
            formatted_sell_target = "{:.2f}".format(sell_target)

            # Create a dictionary to store these values
            trade_details = {
                'Sell_SL': formatted_sell_stoploss,
                'Sell_Target': formatted_sell_target
            }
            # Assign values to the keys in trade_details_file
            sell_trade_details_file.update(trade_details)
            save_data(SELL_TRADE_DETAILS_FILE, sell_trade_details_file)

            sell_sl = sell_trade_details_file.get('Sell_SL', 0)
            sell_tgt = sell_trade_details_file.get('Sell_Target', 0)


def execute_sell_trade():
    global dlf_quantity, sell_order_details
    # If the current time is later than or equal to the desired execution time, execute the buy order
    ret = api.place_order(buy_or_sell='S', product_type='I',
                          exchange='NSE', tradingsymbol='DLF-EQ',
                          quantity=dlf_quantity, discloseqty=0, price_type='MKT',
                          retention='DAY', remarks='my_order_002')

    # Extract the orderno from the ret value
    orderno = ret['norenordno']

    order_history = api.single_order_history(orderno=orderno)

    if order_history:
        # Check the order status
        status = order_history[0].get('status')

        if status == 'COMPLETE':
            # Fetch the order timestamp
            order_timestamp = order_history[0].get('norentm')
            order_quantity = order_history[0].get('qty')
            avgprc = order_history[0].get('avgprc')

            # Check if the order has not been processed before
            if orderno not in sell_order_details:
                # Store the details in the global dictionary
                sell_order_details[orderno] = {
                    'Status': 'COMPLETE',
                    'Timestamp': order_timestamp,
                    'Quantity': order_quantity,
                    'sell_avgprc': avgprc,
                    'trantype': 'S',  # Add custom field trantype with value "B" (Buy)
                    'remarks': 'my_order_002',  # Add custom field remarks to identify the buy order
                }

                # Save the updated sell_order_details dictionary to a file
                save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)

    # Return the order details dictionary
    return sell_order_details


def execute_exit_trade_1_sell():
    global sell_order_details, exit1_sell_order_details, exit1_sell_orderno
    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            sell_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NSE', tradingsymbol='DLF-EQ',
                                  quantity=sell_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_002')

            # Extract the orderno from the ret value
            exit1_sell_orderno = ret['norenordno']

            order_history = api.single_order_history(orderno=exit1_sell_orderno)

            if order_history:
                # Check the order status
                status = order_history[0].get('status')

                if status == 'COMPLETE':

                    # Check if the order has not been processed before
                    if exit1_sell_orderno not in exit1_sell_order_details:
                        # Store the details in the global dictionary
                        exit1_sell_order_details[exit1_sell_orderno] = {
                            'Status': 'COMPLETE',
                        }
                        # Save the updated exit buy_order_details dictionary to a file after removing the item
                        save_data(EXIT1_SELL_ORDER_DETAILS_FILE, exit1_sell_order_details)

    # Return the order details dictionary
    return exit1_sell_order_details


def execute_exit_trade_2_sell():
    global sell_order_details, exit2_sell_order_details, exit2_sell_orderno
    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            sell_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NSE', tradingsymbol='DLF-EQ',
                                  quantity=sell_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_002')

            # Extract the orderno from the ret value
            exit2_sell_orderno = ret['norenordno']

            order_history = api.single_order_history(orderno=exit2_sell_orderno)

            if order_history:
                # Check the order status
                status = order_history[0].get('status')

                if status == 'COMPLETE':

                    # Check if the order has not been processed before
                    if exit2_sell_orderno not in exit2_sell_order_details:
                        # Store the details in the global dictionary
                        exit2_sell_order_details[exit2_sell_orderno] = {
                            'Status': 'COMPLETE',
                        }
                        save_data(EXIT2_SELL_ORDER_DETAILS_FILE, exit2_sell_order_details)

    # Return the updated exit2_buy_order_details dictionary
    return exit2_sell_order_details


def exit_trade_15_15_sell():
    global sell_order_details, exit3_sell_order_details, exit3_sell_orderno
    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            sell_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NSE', tradingsymbol='DLF-EQ',
                                  quantity=sell_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_002')

            # Extract the orderno from the ret value
            exit3_sell_orderno = ret['norenordno']

            # Verify order history here (similar to other exit_trade functions)
            order_history = api.single_order_history(orderno=exit3_sell_orderno)
            if order_history:
                status = order_history[0].get('status')
                if status == 'COMPLETE':
                    # Check if the order has not been processed before
                    if exit3_sell_orderno not in exit3_sell_order_details:
                        # Store the details in the global dictionary
                        exit3_sell_order_details[exit3_sell_orderno] = {
                            'Status': 'COMPLETE',
                        }
                        # Save the updated exit3 buy_order_details dictionary to a file after removing the item
                        save_data(EXIT3_SELL_ORDER_DETAILS_FILE, exit3_sell_order_details)

    return exit3_sell_order_details


def sell_condition_check():
    global dlf_lp_value, store_low, sell_order_details, order_status_counts, total_count, sell_trade_details_file

    max_retries = 5
    retries = 0

    while retries < max_retries:
        if dlf_lp_value != 0 and store_low is not None:
            if isinstance(dlf_lp_value, (int, float)) and isinstance(store_low, (int, float)):
                entry_price = store_low
                if dlf_lp_value <= entry_price and dlf_lp_value > (entry_price - 0.4):
                    if not buy_order_details:  # Check if buy_order_details is empty
                        if not sell_order_details:  # Check if sell_order_details is empty
                            # Check if the current time is before 14:20
                            current_time = datetime.datetime.now().time()
                            if current_time < datetime.time(14, 30):
                                if total_count <= 3:
                                    sell_order_details = execute_sell_trade()
                                    time.sleep(0.1)
                                    sell_sl_tgt_loop()
                                    time.sleep(0.1)
                                    sell_sl_tgt_loop()
                                    time.sleep(0.1)
                                    sell_sl_tgt_loop()
                                    save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                    if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                                           for orderno, order_info in sell_order_details.items()):
                                        save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)

                                    else:

                                        retries += 1
                                        break

        time.sleep(0.5)  # Adjust the


def exit_trade_1_loop_sell():
    global sell_order_details, dlf_lp_value, sell_trade_details_file, exit1_sell_order_details, exit1_sell_orderno, sell_sl
    exit1_order_details = False

    while True:
        if not sell_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in sell_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'my_order_002':
                    # Check if the current time is less than 15:15
                    if current_time < datetime.time(15, 15):
                        dlf_lp_value = float(dlf_lp_value)
                        sell_stoploss = float(sell_sl)
                        # Check if both values are not equal to 0 before comparison
                        if dlf_lp_value != 0 and sell_stoploss != 0:
                            if dlf_lp_value >= sell_stoploss:
                                # Call the exit trade function here
                                execute_exit_trade_1_sell()
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       exit1_sell_orderno, order_info in exit1_sell_order_details.items()):
                                    exit1_order_details = True
                                    sell_order_details.pop(orderno)
                                    sell_order_details.clear()
                                    exit1_sell_order_details.pop(exit1_sell_orderno)
                                    sell_trade_details_file.clear()
                                    save_data(SELL_TRADE_DETAILS_FILE, sell_trade_details_file)
                                    save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                    save_data(EXIT1_SELL_ORDER_DETAILS_FILE, exit1_sell_order_details)
                                    break  # Corrected the indentation

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)


def exit_trade_2_loop_sell():
    global sell_order_details, dlf_lp_value, sell_trade_details_file, exit2_sell_order_details, exit2_sell_orderno, sell_tgt

    exit2_order_details = False

    while True:
        if not sell_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in sell_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'my_order_002':
                    # Check if the current time is less than 15:15
                    if current_time < datetime.time(15, 15):
                        dlf_lp_value = float(dlf_lp_value)
                        sell_target_ = float(sell_tgt)
                        # Check if both values are not equal to 0 before comparison
                        if dlf_lp_value != 0 and sell_target_ != 0:
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if dlf_lp_value <= sell_target_:
                                # Call the exit trade function here
                                execute_exit_trade_2_sell()
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       exit2_sell_orderno, order_info in exit2_sell_order_details.items()):
                                    exit2_order_details = True
                                    sell_order_details.pop(orderno)
                                    exit2_sell_order_details.pop(exit2_sell_orderno)
                                    sell_trade_details_file.clear()
                                    sell_order_details.clear()
                                    save_data(SELL_TRADE_DETAILS_FILE, sell_trade_details_file)
                                    save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                    save_data(EXIT2_SELL_ORDER_DETAILS_FILE, exit2_sell_order_details)
                                    break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)


def exit_trade_15_15_loop_sell():
    global exit3_sell_order_details, sell_order_details, exit3_sell_orderno, sell_trade_details_file

    exit3_order_details = False

    while True:
        if not sell_order_details:
            time.sleep(0.01)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in sell_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'my_order_002':
                    # Check if the current time is less than 14:55
                    if current_time > datetime.time(15, 15):
                        exit_trade_15_15_sell()
                        if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                               exit3_sell_orderno, order_info in exit3_sell_order_details.items()):
                            exit3_order_details = True
                            sell_order_details.pop(orderno)
                            exit3_sell_order_details.pop(exit3_sell_orderno)
                            sell_order_details.clear()
                            sell_trade_details_file.clear()
                            save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                            save_data(EXIT3_SELL_ORDER_DETAILS_FILE, exit3_sell_order_details)
                            save_data(SELL_TRADE_DETAILS_FILE, sell_trade_details_file)
                            break
        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)


def fetch_candle_data_loop():
    # Calculate the date 5 days ago from the current date
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
    five_days = five_days_ago.strftime('%d-%m-%Y')

    # Define the start and end times for the 5-minute candles
    start_time = datetime.datetime.strptime(f'{five_days} 09:15:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 15:30:00', '%d-%m-%Y %H:%M:%S')

    interval = 5

    while True:
        # Fetch candle data (replace this with your implementation)
        candle_df = get_time_series('NSE', '14732', start_time, end_time, interval=5)

        if candle_df is not None:
            # Process the data (replace this with your implementation)
            print_candle_df(candle_df)
            calculate_rsi(candle_df, n=14)
            calculate_stoch_rsi(stoch_period=14, smoothing_period=5)
            calculate_atr(candle_df)
            atr_df = calculate_atr(candle_df)
            check_buy_entry_conditions(candle_df, atr_df)
            check_sell_entry_conditions(candle_df, atr_df)

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
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    fetch_candle_data_thread = threading.Thread(target=fetch_candle_data_loop)
    order_book_thread = threading.Thread(target=get_order_book_loop)
    buy_condition_thread = threading.Thread(target=buy_condition_check)
    exit_trade1_thread = threading.Thread(target=exit_trade_1_loop)
    exit_trade2_thread = threading.Thread(target=exit_trade_2_loop)
    exit_trade_1515_thread = threading.Thread(target=exit_trade_1515_loop)
    sell_condition_thread = threading.Thread(target=sell_condition_check)
    sell_exit_trade1_thread = threading.Thread(target=exit_trade_1_loop_sell)
    sell_exit_trade2_thread = threading.Thread(target=exit_trade_2_loop_sell)
    sell_exit_trade_15_15_thread = threading.Thread(target=exit_trade_15_15_loop_sell)

    # Start the threads
    ltp_data_thread.start()
    fetch_candle_data_thread.start()
    order_book_thread.start()
    buy_condition_thread.start()
    exit_trade1_thread.start()
    exit_trade2_thread.start()
    exit_trade_1515_thread.start()
    sell_condition_thread.start()
    sell_exit_trade1_thread.start()
    sell_exit_trade2_thread.start()
    sell_exit_trade_15_15_thread.start()
