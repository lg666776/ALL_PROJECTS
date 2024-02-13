from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime

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
    print('HCLTECH LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()

output = api.get_limits()
cash_value = float(output['cash'])  # Convert to a float for calculation
total_loss = cash_value / 250

# Specify the file path where the data is stored
file_path = 'ohlc.txt'

# Create a dictionary to store the values
ohlc = {}

# Open the file in read mode
with open(file_path, 'r') as file:
    # Read each line in the file
    for line in file:
        # Split each line by ':' to separate the key and value
        key, value = line.strip().split(': ')
        # Remove double quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]  # Remove double quotes
        # Check if the value is numeric (float)
        if '.' in value:
            ohlc[key] = float(value)
        else:
            ohlc[key] = value  # Store as a string

# Access and print individual values
hcltech_high = ohlc['hcltech_high']
hcltech_low = ohlc['hcltech_low']
hcltech_close = ohlc['hcltech_close']

# Extract the string '2023-10-03 15:25:00' from the dictionary and add single quotes
remove_date_string = "'" + ohlc['remove_date'] + "'"
added_date_string = "'" + ohlc['adding_next'] + "'"

formatted_final_mtm = 0
hcltech_lp_value = 0
hcltech_quantity = 0
original_quantity = 0
store_low = None
store_high = None
vwap_df = []
lowest_point = None
store_low_sell = None
buy_exit_point = None
store_high_sell = None
highest_point = None
exit1_orderno = None
exit1_sell_orderno = None
total_buy_count = 0
total_sell_count = 0
total_count = 0
buy_price = 0
sell_price = 0

BUYING_DICT = 'htech_buying_prc.pickle'
SELLING_DICT = 'htech_selling_prc.pickle'
BUY_MTM_DICT = 'htech_buying_mtm.pickle'
SELL_MTM_DICT = 'htech_selling_mtm.pickle'
BUY_ORDER_DETAILS_FILE = 'htech_buy_order_details.pickle'
SELL_ORDER_DETAILS_FILE = 'htech_sell_order_details.pickle'
EXIT1_BUY_ORDER_DETAILS_FILE = 'htech_exit1_buy_order_details.pickle'
EXIT1_SELL_ORDER_DETAILS_FILE = 'htech_exit1_sell_order_details.pickle'


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


# Load data with initializing empty dictionaries for all variables
buying_price_file: dict = load_data(BUYING_DICT, initialize_empty_dict=True)
selling_price_file: dict = load_data(SELLING_DICT, initialize_empty_dict=True)
buy_mtm_dictionary_file: dict = load_data(BUY_MTM_DICT, initialize_empty_dict=True)
sell_mtm_dictionary_file: dict = load_data(SELL_MTM_DICT, initialize_empty_dict=True)
sell_order_details: dict = load_data(SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
buy_order_details: dict = load_data(BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit1_buy_order_details: dict = load_data(EXIT1_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
exit1_sell_order_details: dict = load_data(EXIT1_SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)


def save_data(file_path, data):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


def ltp_quantity_loop():
    global hcltech_lp_value, hcltech_quantity, original_quantity
    while True:
        try:
            # Read data from data_titan.pickle
            with open('data_hcltech.pickle', 'rb') as file:
                try:
                    data_hcl = pickle.load(file)
                    if isinstance(data_hcl, dict):
                        hcltech_lp_value = data_hcl.get('hcltech_lp_value')
                        print(hcltech_lp_value)
                        original_quantity = data_hcl.get('hcltech_quantity')

                except EOFError:
                    # Reset the titan_lp_value and titan_quantity to None if EOFError
                    hcltech_lp_value = 0

        except FileNotFoundError:
            hcltech_lp_value = 0

        except Exception as e:
            hcltech_lp_value = 0

        time.sleep(0.1)



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

    return vwap_df


def calculate_atr(candle_df, period=14):
    pd.set_option('display.max_rows', None)

    # Create a boolean mask to identify the rows to remove
    mask = candle_df.index == pd.to_datetime(remove_date_string)

    # Use the mask to filter and keep rows where the condition is False
    candle_df = candle_df[~mask]

    candle_df = candle_df[['inth', 'intl', 'intc']].copy()

    # Create a new DataFrame for the manual input
    manual_data = pd.DataFrame({
        'inth': [hcltech_high],
        'intl': [hcltech_low],
        'intc': [hcltech_close]
    }, index=pd.to_datetime([remove_date_string]))

    # Find the index location of '2023-10-03 15:25:00' in the original 'candle_df'
    insert_index = candle_df.index.get_loc(added_date_string)

    # Split the original 'candle_df' into two parts, before and after the insert_index
    candle_df_before = candle_df.iloc[:insert_index + 1]
    candle_df_after = candle_df.iloc[insert_index + 1:]

    # Concatenate the parts with 'manual_data' in between to insert the values at '15:30:00'
    candle_df = pd.concat([candle_df_before, manual_data, candle_df_after])

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


def cal_atr(atr_df):
    global hcltech_lp_value, hcltech_quantity, original_quantity

    for i, row in atr_df.iterrows():
        atr = row['atr']

        # Define the new variables
        atr_75_prc = hcltech_lp_value * 0.0075
        atr_100_prc = hcltech_lp_value * 0.0100
        atr_150_prc = hcltech_lp_value * 0.0125
        atr_200_prc = hcltech_lp_value * 0.0150

        if atr <= atr_75_prc:
            hcltech_quantity = original_quantity
        elif atr > atr_75_prc and atr <= atr_100_prc:
            # Keep 75% of the original quantity
            hcltech_quantity = int(original_quantity * 0.75)
        elif atr > atr_100_prc and atr <= atr_150_prc:
            # Keep 50% of the original quantity
            hcltech_quantity = int(original_quantity * 0.50)
        elif atr > atr_150_prc and atr <= atr_200_prc:
            # Keep 25% of the original quantity
            hcltech_quantity = int(original_quantity * 0.25)
        else:
            # Keep 15% of the original quantity
            hcltech_quantity = int(original_quantity * 0.15)


def buying_price():
    global buy_price, buy_order_details, buying_price_file
    buy_price = buying_price_file.get('BUY_PRICE', 0)

    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_avgprc_str = order_info.get('buy_avgprc', '0')  # Default to '0' if missing or not a number
            buy_avg_prc = float(buy_avgprc_str)  # Convert to float

            # Create a dictionary to store these values
            buy_avg = {
                'BUY_PRICE': buy_avg_prc,
            }
            # Assign values to the keys in trade_details_file
            buying_price_file.update(buy_avg)
            save_data(BUYING_DICT, buying_price_file)


def seling_price():
    global sell_price, sell_order_details, selling_price_file
    sell_price = selling_price_file.get('SELL_PRICE', 0)

    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing sell order
            sell_avgprc_str = order_info.get('sell_avgprc', '0')  # Default to '0' if missing or not a number
            sell_avg_prc = float(sell_avgprc_str)  # Convert to float

            # Create a dictionary to store these values
            sell_avg = {
                'SELL_PRICE': sell_avg_prc,
            }
            # Assign values to the keys in trade_details_file
            selling_price_file.update(sell_avg)
            save_data(SELLING_DICT, selling_price_file)


def mtm_loop():
    global buy_price, sell_price, hcltech_lp_value, hcltech_quantity, buy_order_details, total_count, buy_mtm_dictionary_file, sell_mtm_dictionary_file, total_buy_count, total_sell_count, formatted_final_mtm

    final_buy_mtm = 0
    final_sell_mtm = 0

    while True:
        # Scenario 1: Iterations with buy_price = 0
        if buy_price != 0:
            if hcltech_lp_value != 0:
                buy_mtm = hcltech_lp_value - buy_price
                final_buy_mtm = buy_mtm * hcltech_quantity

        if total_buy_count == 1:
            buy_mtm_dictionary = {
                'FINAL_Buy_MTM_1': final_buy_mtm
            }
            buy_mtm_dictionary_file.update(buy_mtm_dictionary)
            save_data(BUY_MTM_DICT, buy_mtm_dictionary_file)

        if total_buy_count == 2:
            buy_mtm_dictionary = {
                'FINAL_Buy_MTM_2': final_buy_mtm
            }
            buy_mtm_dictionary_file.update(buy_mtm_dictionary)
            save_data(BUY_MTM_DICT, buy_mtm_dictionary_file)

        # Scenario 1: Iterations with sell_price = 0
        if sell_price != 0:
            if hcltech_lp_value != 0:
                sell_mtm = sell_price - hcltech_lp_value
                final_sell_mtm = sell_mtm * hcltech_quantity

        if total_sell_count == 1:
            sell_mtm_dictionary = {
                'FINAL_Sell_MTM_1': final_sell_mtm
            }
            sell_mtm_dictionary_file.update(sell_mtm_dictionary)
            save_data(SELL_MTM_DICT, sell_mtm_dictionary_file)

        if total_sell_count == 2:
            sell_mtm_dictionary = {
                'FINAL_Sell_MTM_2': final_sell_mtm
            }
            sell_mtm_dictionary_file.update(sell_mtm_dictionary)
            save_data(SELL_MTM_DICT, sell_mtm_dictionary_file)

        buy_mtm_1 = buy_mtm_dictionary_file.get('FINAL_Buy_MTM_1', 0)
        buy_mtm_2 = buy_mtm_dictionary_file.get('FINAL_Buy_MTM_2', 0)
        max_buy_mtm = buy_mtm_1 + buy_mtm_2

        sell_mtm_1 = sell_mtm_dictionary_file.get('FINAL_Sell_MTM_1', 0)
        sell_mtm_2 = sell_mtm_dictionary_file.get('FINAL_Sell_MTM_2', 0)
        max_sell_mtm = sell_mtm_1 + sell_mtm_2

        max_mtm = max_buy_mtm + max_sell_mtm
        formatted_final_mtm = f'{max_mtm:.2f}'  # Format to display with 2 decimal places

        time.sleep(0.1)  # Add a sleep time to control the rate of calculation and printing


def check_buy_entry_conditions(candle_df, vwap_df):
    global store_high, buy_order_details

    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['inth'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['intl'], errors='coerce')

    # Convert 'VWAP' column in vwap_df to numeric
    vwap_df['VWAP'] = pd.to_numeric(vwap_df['VWAP'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Find the index of the data point corresponding to 9:15 AM
    start_time_index = candle_df_reset.index[candle_df_reset['time'] == '09:15'].tolist()
    if not start_time_index:

        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    store_high = None
    # Loop through each candle data starting from 9:15 AM

    for i in range(start_index, len(candle_df_reset)):
        # Check for the condition of low (intl) above VWAP
        if candle_df_reset['intl'].iloc[i] > vwap_df['VWAP'].iloc[i]:
            if store_high is None:
                store_high = candle_df_reset['inth'].iloc[i]

        elif store_high is not None and candle_df_reset['intl'].iloc[i] < vwap_df['VWAP'].iloc[i]:
            # If a candle with high below VWAP is found, set the sell_exit point and reset the stored high price
            store_high = None


def exit_1_calculation(candle_df, vwap_df):
    global store_low, buy_order_details

    # Get the current time in 'HH:MM' format
    current_time = datetime.datetime.now().strftime('%H:%M')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Merge the two DataFrames based on the 'time' column
    merged_df = pd.merge(candle_df_reset, vwap_df, on='time')

    # Check if order details are available
    if not buy_order_details:
        return

    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the Unix timestamp from the order_info dictionary
            buy_order_timestamp = order_info.get('Timestamp')

            buy_order_unix_timestamp = int(
                datetime.datetime.strptime(buy_order_timestamp, '%H:%M:%S %d-%m-%Y').timestamp())

            # Calculate the start timestamp for filtering
            start_time = datetime.datetime.fromtimestamp(buy_order_unix_timestamp).replace(second=0, microsecond=0)

            # Filter the merged DataFrame based on the start timestamp
            filtered_candle_df = merged_df[merged_df['time'] >= start_time]

            # Calculate VWAP for the filtered data
            vwap_df_filtered = filtered_candle_df['VWAP']

            # Initialize variables to store and reset the high price
            store_low = None

            for i in range(len(filtered_candle_df)):
                # Ensure that 'intl' and 'intc' columns contain numeric values
                filtered_candle_df.loc[:, 'intl'] = pd.to_numeric(filtered_candle_df['intl'], errors='coerce')
                filtered_candle_df.loc[:, 'intc'] = pd.to_numeric(filtered_candle_df['intc'], errors='coerce')
                filtered_candle_df.loc[:, 'inth'] = pd.to_numeric(filtered_candle_df['inth'], errors='coerce')

                # Check for the condition of high (inth) below VWAP
                if filtered_candle_df['inth'].iloc[i] < vwap_df_filtered.iloc[i]:
                    if store_low is None:
                        # If the condition is satisfied, update the store_low
                        store_low = filtered_candle_df['intl'].iloc[i]

                elif store_low is not None and filtered_candle_df['intl'].iloc[i] > vwap_df_filtered.iloc[i]:
                    # If a subsequent candle with low above VWAP is found after the condition was satisfied, remove the
                    # stored high price
                    store_low = None


def exit_2_calculation(candle_df):
    global lowest_point, buy_order_details
    # Reset the index to make the 'time' column a regular column again

    candle_df_reset = candle_df.reset_index()

    # Merge the two DataFrames based on the 'time' column
    merged_df = pd.merge(candle_df_reset, vwap_df, on='time')

    # Check if order details are available
    if not buy_order_details:
        return

    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the Unix timestamp from the order_info dictionary
            buy_order_timestamp = order_info.get('Timestamp')

            # Get the Unix timestamp for the buy_order_timestamp
            buy_order_unix_timestamp = int(
                datetime.datetime.strptime(buy_order_timestamp, '%H:%M:%S %d-%m-%Y').timestamp())

            # Set the start time to 9:15 AM
            start_time = datetime.datetime.combine(datetime.datetime.today(), datetime.time(hour=9, minute=15))

            # Create a mask to filter the DataFrame within the specified range
            filter_mask = (merged_df['time'] >= start_time) & (
                    merged_df['time'] <= datetime.datetime.fromtimestamp(buy_order_unix_timestamp))

            # Apply the filter to get the DataFrame within the specified range
            filtered_candle_df_2 = merged_df[filter_mask]

            if filtered_candle_df_2.empty:
                return None

            # Find the lowest point in the 'intl' column (assuming this represents the low price)
            lowest_point = filtered_candle_df_2['intl'].min()

    return lowest_point


def execute_buy_trade():
    global hcltech_quantity, buy_order_details

    # If the current time is later than or equal to the desired execution time, execute the buy order
    ret = api.place_order(buy_or_sell='B', product_type='I',
                          exchange='NSE', tradingsymbol='HCLTECH-EQ',
                          quantity=hcltech_quantity, discloseqty=0, price_type='MKT',
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
                                  exchange='NSE', tradingsymbol='HCLTECH-EQ',
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


def buy_condition_check():
    global hcltech_lp_value, store_high, buy_order_details, total_count, sell_order_details, total_count, total_buy_count, total_sell_count, formatted_final_mtm

    max_retries = 2  # Maximum number of retries for placing the buy order
    retries = 0  # Counter for retries


    while retries < max_retries:
        if hcltech_lp_value != 0 and store_high is not None:
            if isinstance(hcltech_lp_value, (int, float)) and isinstance(store_high, (int, float)):
                entry_price = store_high
                if hcltech_lp_value > entry_price and hcltech_lp_value < (entry_price + 2):
                    if not buy_order_details:
                        if not sell_order_details:
                            current_time = datetime.datetime.now().time()
                            if current_time < datetime.time(10, 20):
                                if total_count <= 3 and float(formatted_final_mtm) < total_loss:
                                    buy_order_details = execute_buy_trade()
                                    if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                                           for
                                           orderno, order_info in buy_order_details.items()):
                                        total_buy_count += 1  # Increment the total buy count
                                        total_count = total_buy_count + total_sell_count
                                        print(total_count)
                                        time.sleep(0.1)
                                        buying_price()
                                        time.sleep(0.1)
                                        buying_price()
                                        time.sleep(2)
                                    else:
                                        retries += 1
                                        break

        time.sleep(0.1)  # Adjust the interval as needed


def exit_trade_1_loop():
    global buy_order_details, hcltech_lp_value, store_low, exit1_buy_order_details, exit1_orderno, lowest_point

    # Initialize the exit1_order_executed flag outside the loop
    exit1_order_details = False

    while True:
        if not buy_order_details:
            time.sleep(0.1)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    if hcltech_lp_value != 0 and store_low is not None:
                        hcltech_lp_value = float(hcltech_lp_value)
                        store_low = float(store_low)
                        if hcltech_lp_value < store_low:
                            execute_exit_trade_1()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_orderno, order_info in exit1_buy_order_details.items()):
                                exit1_order_details = True
                                buy_order_details.pop(orderno)
                                exit1_buy_order_details.pop(exit1_orderno)
                                buy_order_details.clear()
                                save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                save_data(EXIT1_BUY_ORDER_DETAILS_FILE, exit1_buy_order_details)
                                save_data(BUYING_DICT, buying_price_file)
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                break
                    if hcltech_lp_value != 0 and lowest_point is not None:
                        hcltech_lp_value = float(hcltech_lp_value)
                        lowest_point = float(lowest_point)
                        if hcltech_lp_value < lowest_point:
                            execute_exit_trade_1()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_orderno, order_info in exit1_buy_order_details.items()):
                                exit1_order_details = True
                                buy_order_details.pop(orderno)
                                exit1_buy_order_details.pop(exit1_orderno)
                                buy_order_details.clear()
                                save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                save_data(EXIT1_BUY_ORDER_DETAILS_FILE, exit1_buy_order_details)
                                save_data(BUYING_DICT, buying_price_file)
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                break
                    if hcltech_lp_value != 0 and formatted_final_mtm != 0:
                        hcltech_lp_value = float(hcltech_lp_value)
                        if float(formatted_final_mtm) > total_loss:
                            execute_exit_trade_1()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_orderno, order_info in exit1_buy_order_details.items()):
                                exit1_order_details = True
                                buy_order_details.pop(orderno)
                                exit1_buy_order_details.pop(exit1_orderno)
                                buy_order_details.clear()
                                save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                save_data(EXIT1_BUY_ORDER_DETAILS_FILE, exit1_buy_order_details)
                                save_data(BUYING_DICT, buying_price_file)
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                break
                    if hcltech_lp_value != 0:
                        if current_time > datetime.time(14, 55):
                            execute_exit_trade_1()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_orderno, order_info in exit1_buy_order_details.items()):
                                exit1_order_details = True
                                buy_order_details.pop(orderno)
                                exit1_buy_order_details.pop(exit1_orderno)
                                buy_order_details.clear()
                                save_data(BUY_ORDER_DETAILS_FILE, buy_order_details)
                                save_data(EXIT1_BUY_ORDER_DETAILS_FILE, exit1_buy_order_details)
                                save_data(BUYING_DICT, buying_price_file)
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                time.sleep(0.1)
                                buying_price()
                                break
        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.1)


def check_sell_entry_conditions(candle_df, vwap_df):
    global store_low_sell, sell_order_details

    # Convert 'inth' (low) and 'intc' (close) columns in candle_df to numeric
    candle_df['inth'] = pd.to_numeric(candle_df['inth'], errors='coerce')
    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')
    candle_df['intl'] = pd.to_numeric(candle_df['intl'], errors='coerce')

    # Convert 'VWAP' column in vwap_df to numeric
    vwap_df['VWAP'] = pd.to_numeric(vwap_df['VWAP'], errors='coerce')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Find the index of the data point corresponding to 9:15 AM
    start_time_index = candle_df_reset.index[candle_df_reset['time'] == '09:15'].tolist()
    if not start_time_index:

        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    store_low_sell = None

    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check for the condition of high (inth) below VWAP
        if candle_df_reset['inth'].iloc[i] < vwap_df['VWAP'].iloc[i]:
            if store_low_sell is None:
                store_low_sell = candle_df_reset['intl'].iloc[i]

        elif store_low_sell is not None and candle_df_reset['intl'].iloc[i] > vwap_df['VWAP'].iloc[i]:
            # If a subsequent candle with low above VWAP is found after the condition was satisfied, reset the
            # stored high price
            store_low_sell = None


def exit_1_calculation_sell(candle_df, vwap_df):
    global store_high_sell, sell_order_details

    # Get the current time in 'HH:MM' format
    current_time = datetime.datetime.now().strftime('%H:%M')

    # Reset the index to make the 'time' column a regular column again
    candle_df_reset = candle_df.reset_index()

    # Merge the two DataFrames based on the 'time' column
    merged_df = pd.merge(candle_df_reset, vwap_df, on='time')

    # Check if order details are available
    if not sell_order_details:
        return

    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the Unix timestamp from the order_info dictionary
            sell_order_timestamp = order_info.get('Timestamp')
            sell_order_unix_timestamp = int(
                datetime.datetime.strptime(sell_order_timestamp, '%H:%M:%S %d-%m-%Y').timestamp())

            # Calculate the start timestamp for filtering
            start_time = datetime.datetime.fromtimestamp(sell_order_unix_timestamp).replace(second=0, microsecond=0)

            # Filter the merged DataFrame based on the start timestamp
            filtered_candle_df = merged_df[merged_df['time'] >= start_time]

            # Calculate VWAP for the filtered data
            vwap_df_filtered = filtered_candle_df['VWAP']

            # Initialize variables to store and reset the high price
            store_high_sell = None

            for i in range(len(filtered_candle_df)):
                # Ensure that 'intl' and 'intc' columns contain numeric values
                filtered_candle_df.loc[:, 'intl'] = pd.to_numeric(filtered_candle_df['intl'], errors='coerce')
                filtered_candle_df.loc[:, 'intc'] = pd.to_numeric(filtered_candle_df['intc'], errors='coerce')
                filtered_candle_df.loc[:, 'inth'] = pd.to_numeric(filtered_candle_df['inth'], errors='coerce')

                # Check for the condition of low (intl) above VWAP
                if filtered_candle_df['intl'].iloc[i] > vwap_df_filtered.iloc[i]:
                    if store_high_sell is None:
                        # If the condition is satisfied, update the store_low
                        store_high_sell = filtered_candle_df['inth'].iloc[i]

                elif store_high_sell is not None and filtered_candle_df['inth'].iloc[i] < vwap_df_filtered.iloc[i]:
                    # If a subsequent candle with high below VWAP is found after the condition was satisfied, remove the
                    # stored high price
                    store_high_sell = None


def exit_2_calculation_sell(candle_df):
    global highest_point, sell_order_details
    # Reset the index to make the 'time' column a regular column again

    candle_df_reset = candle_df.reset_index()

    # Merge the two DataFrames based on the 'time' column
    merged_df = pd.merge(candle_df_reset, vwap_df, on='time')

    # Check if order details are available
    if not sell_order_details:
        return

    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the Unix timestamp from the order_info dictionary
            sell_order_timestamp = order_info.get('Timestamp')

            # Get the Unix timestamp for the buy_order_timestamp
            sell_order_unix_timestamp = int(
                datetime.datetime.strptime(sell_order_timestamp, '%H:%M:%S %d-%m-%Y').timestamp())

            # Set the start time to 9:15 AM
            start_time = datetime.datetime.combine(datetime.datetime.today(), datetime.time(hour=9, minute=15))

            # Create a mask to filter the DataFrame within the specified range
            filter_mask = (merged_df['time'] >= start_time) & (
                    merged_df['time'] <= datetime.datetime.fromtimestamp(sell_order_unix_timestamp))

            # Apply the filter to get the DataFrame within the specified range
            filtered_candle_df_2 = merged_df[filter_mask]

            if filtered_candle_df_2.empty:
                return None

            # Find the lowest point in the 'intl' column (assuming this represents the low price)
            highest_point = filtered_candle_df_2['inth'].max()

    return highest_point


def execute_sell_trade():
    global hcltech_quantity, sell_order_details
    # If the current time is later than or equal to the desired execution time, execute the buy order
    ret = api.place_order(buy_or_sell='S', product_type='I',
                          exchange='NSE', tradingsymbol='HCLTECH-EQ',
                          quantity=hcltech_quantity, discloseqty=0, price_type='MKT',
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
                                  exchange='NSE', tradingsymbol='HCLTECH-EQ',
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


def sell_condition_check():
    global hcltech_lp_value, store_low_sell, sell_order_details, total_count, buy_order_details, total_count, total_buy_count, total_sell_count, formatted_final_mtm

    max_retries = 2  # Maximum number of retries for placing the sell order
    retries = 0  # Counter for retries

    while retries < max_retries:
        if hcltech_lp_value != 0 and store_low_sell is not None:
            if isinstance(hcltech_lp_value, (int, float)) and isinstance(store_low_sell, (int, float)):
                entry_price = store_low_sell
                if hcltech_lp_value < entry_price and hcltech_lp_value > (entry_price - 2):
                    if not buy_order_details:
                        if not sell_order_details:
                            current_time = datetime.datetime.now().time()
                            if current_time < datetime.time(14, 20):
                                if total_count <= 3 and float(formatted_final_mtm) < total_loss:
                                    sell_order_details = execute_sell_trade()
                                    if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                                           for orderno, order_info in sell_order_details.items()):
                                        total_sell_count += 1
                                        total_count = total_buy_count + total_sell_count
                                        print(total_count)
                                        time.sleep(0.1)
                                        seling_price()
                                        time.sleep(0.1)
                                        seling_price()
                                        time.sleep(2)
                                    else:
                                        retries += 1
                                        break

        time.sleep(0.1)  # Adjust the interval as needed


def exit_trade_1_loop_sell():
    global sell_order_details, hcltech_lp_value, store_high_sell, exit1_sell_order_details, exit1_sell_orderno, highest_point, formatted_final_mtm

    exit1_order_details = False

    while True:
        if not sell_order_details:
            time.sleep(0.1)  # Add a sleep time of 0.5 seconds before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()
        for orderno, order_info in sell_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'my_order_002':
                    if hcltech_lp_value != 0 and store_high_sell is not None:
                        hcltech_lp_value = float(hcltech_lp_value)
                        store_high_sell = float(store_high_sell)
                        if hcltech_lp_value > store_high_sell:
                            execute_exit_trade_1_sell()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_sell_orderno, order_info in exit1_sell_order_details.items()):
                                exit1_order_details = True
                                sell_order_details.pop(orderno)
                                exit1_sell_order_details.pop(exit1_sell_orderno)
                                sell_order_details.clear()
                                selling_price_file.clear()
                                save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                save_data(EXIT1_SELL_ORDER_DETAILS_FILE, exit1_sell_order_details)
                                save_data(SELLING_DICT, selling_price_file)
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                break
                    if hcltech_lp_value != 0 and highest_point is not None:
                        hcltech_lp_value = float(hcltech_lp_value)
                        highest_point = float(highest_point)
                        if hcltech_lp_value > highest_point:
                            execute_exit_trade_1_sell()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_sell_orderno, order_info in exit1_sell_order_details.items()):
                                exit1_order_details = True
                                sell_order_details.pop(orderno)
                                exit1_sell_order_details.pop(exit1_sell_orderno)
                                sell_order_details.clear()
                                selling_price_file.clear()
                                save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                save_data(EXIT1_SELL_ORDER_DETAILS_FILE, exit1_sell_order_details)
                                save_data(SELLING_DICT, selling_price_file)
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                break
                    if hcltech_lp_value != 0 and formatted_final_mtm != 0:
                        hcltech_lp_value = float(hcltech_lp_value)
                        if float(formatted_final_mtm) > total_loss:
                            execute_exit_trade_1_sell()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_sell_orderno, order_info in exit1_sell_order_details.items()):
                                exit1_order_details = True
                                sell_order_details.pop(orderno)
                                exit1_sell_order_details.pop(exit1_sell_orderno)
                                sell_order_details.clear()
                                selling_price_file.clear()
                                save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                save_data(EXIT1_SELL_ORDER_DETAILS_FILE, exit1_sell_order_details)
                                save_data(SELLING_DICT, selling_price_file)
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                break
                    if hcltech_lp_value != 0:
                        if current_time > datetime.time(14, 55):
                            execute_exit_trade_1_sell()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   exit1_sell_orderno, order_info in exit1_sell_order_details.items()):
                                exit1_order_details = True
                                sell_order_details.pop(orderno)
                                exit1_sell_order_details.pop(exit1_sell_orderno)
                                sell_order_details.clear()
                                selling_price_file.clear()
                                save_data(SELL_ORDER_DETAILS_FILE, sell_order_details)
                                save_data(EXIT1_SELL_ORDER_DETAILS_FILE, exit1_sell_order_details)
                                save_data(SELLING_DICT, selling_price_file)
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                time.sleep(0.1)
                                seling_price()
                                break
        # Add a sleep time of 0.5 seconds before the next iteration
        time.sleep(0.1)


def fetch_candle_data_loop():
    # Calculate the date 5 days ago from the current date
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
    five_days = five_days_ago.strftime('%d-%m-%Y')

    # Define the start and end times for the 5-minute candles
    start_time = datetime.datetime.strptime(f'{five_days} 09:15:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 15:30:00', '%d-%m-%Y %H:%M:%S')

    interval = 10

    while True:
        # Fetch candle data (replace this with your implementation)
        candle_df = get_time_series('NSE', '7229', start_time, end_time, interval=10)

        if candle_df is not None:
            print_candle_df(candle_df)
            calculate_vwap(candle_df)
            atr_df = calculate_atr(candle_df)
            check_buy_entry_conditions(candle_df, vwap_df)
            exit_1_calculation(candle_df, vwap_df)
            exit_2_calculation(candle_df)
            check_sell_entry_conditions(candle_df, vwap_df)
            exit_1_calculation_sell(candle_df, vwap_df)
            exit_2_calculation_sell(candle_df)
            cal_atr(atr_df)

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
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    fetch_candle_data_thread = threading.Thread(target=fetch_candle_data_loop)
    buy_condition_thread = threading.Thread(target=buy_condition_check)
    exit_trade1_thread = threading.Thread(target=exit_trade_1_loop)
    sell_condition_thread = threading.Thread(target=sell_condition_check)
    sell_exit_trade1_thread = threading.Thread(target=exit_trade_1_loop_sell)
    mtm_thread = threading.Thread(target=mtm_loop)

    # Start the threads
    ltp_data_thread.start()
    fetch_candle_data_thread.start()
    buy_condition_thread.start()
    exit_trade1_thread.start()
    sell_condition_thread.start()
    sell_exit_trade1_thread.start()
    mtm_thread.start()
