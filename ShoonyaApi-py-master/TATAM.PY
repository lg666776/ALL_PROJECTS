from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import requests

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

last_update_time = None
tata_motors_lp_value = None
tata_motors_quantity = []
store_low = None
store_high = None
buy_order_placed = None
lowest_price = None
vwap_df = []
buy_order_details = {}
lowest_point = None
store_low_sell = None
buy_exit_point = None
sell_exit_point = None
last_order_book = None
order_status_counts = {}
total_count = 0
sell_order_placed = None
store_high_sell = None
sell_order_details = {}
highest_point = None
executed_low_values = {}
executed_high_values = {}
exit1_buy_order_details = {}
exit2_buy_order_details = {}
exit3_buy_order_details = {}
exit1_sell_order_details = {}
exit2_sell_order_details = {}
exit3_sell_order_details = {}

# Define file paths for storing order details and executed values
BUY_ORDER_DETAILS_FILE = 'tatamotors_buy_order_details.pkl'
SELL_ORDER_DETAILS_FILE = 'tatamotors100_sell_order_details.pkl'
EXECUTED_HIGH_VALUES_FILE = 'tatamotors500_executed_high_values.pkl'
EXECUTED_LOW_VALUES_FILE = 'tatamotors500_executed_low_values.pkl'
EXIT1_BUY_ORDER_DETAILS_FILE = 'tatam_exit1_buy_order_details.pkl'
EXIT2_BUY_ORDER_DETAILS_FILE = 'tatam_exit2_buy_order_details.pkl'
EXIT3_BUY_ORDER_DETAILS_FILE = 'tatam_exit3_buy_order_details.pkl'
EXIT1_SELL_ORDER_DETAILS_FILE = 'tatam_exit1_sell_order_details.pkl'
EXIT2_SELL_ORDER_DETAILS_FILE = 'tatam_exit2_sell_order_details.pkl'
EXIT3_SELL_ORDER_DETAILS_FILE = 'tatam_exit3_sell_order_details.pkl'

# Load existing buy_order_details if the file exists
try:
    if os.path.exists(BUY_ORDER_DETAILS_FILE):
        with open(BUY_ORDER_DETAILS_FILE, 'rb') as file:
            buy_order_details = pickle.load(file)
    else:
        buy_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading buy_order_details:", e)
    buy_order_details = {}

# Load existing buy_order_details if the file exists
try:
    if os.path.exists(EXIT1_BUY_ORDER_DETAILS_FILE):
        with open(EXIT1_BUY_ORDER_DETAILS_FILE, 'rb') as file:
            exit1_buy_order_details = pickle.load(file)
    else:
        exit1_buy_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading exit_buy_order_details:", e)
    exit1_buy_order_details = {}

# Load existing exit2_buy_order_details if the file exists
try:
    if os.path.exists(EXIT2_BUY_ORDER_DETAILS_FILE):
        with open(EXIT2_BUY_ORDER_DETAILS_FILE, 'rb') as file:
            exit2_buy_order_details = pickle.load(file)
    else:
        exit2_buy_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading exit2_buy_order_details:", e)
    exit2_buy_order_details = {}

# Load existing exit2_buy_order_details if the file exists
try:
    if os.path.exists(EXIT3_BUY_ORDER_DETAILS_FILE):
        with open(EXIT3_BUY_ORDER_DETAILS_FILE, 'rb') as file:
            exit3_buy_order_details = pickle.load(file)
    else:
        exit3_buy_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading exit3_buy_order_details:", e)
    exit3_buy_order_details = {}

# Load existing sell_order_details if the file exists
try:
    if os.path.exists(SELL_ORDER_DETAILS_FILE):
        with open(SELL_ORDER_DETAILS_FILE, 'rb') as file:
            sell_order_details = pickle.load(file)
    else:
        sell_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading sell_order_details:", e)
    sell_order_details = {}

# Load existing buy_order_details if the file exists
try:
    if os.path.exists(EXIT1_SELL_ORDER_DETAILS_FILE):
        with open(EXIT1_SELL_ORDER_DETAILS_FILE, 'rb') as file:
            exit1_sell_order_details = pickle.load(file)
    else:
        exit1_sell_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading exit1_sell_order_details:", e)
    exit1_sell_order_details = {}

# Load existing exit2_buy_order_details if the file exists
try:
    if os.path.exists(EXIT2_SELL_ORDER_DETAILS_FILE):
        with open(EXIT2_SELL_ORDER_DETAILS_FILE, 'rb') as file:
            exit2_sell_order_details = pickle.load(file)
    else:
        exit2_sell_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading exit2_sell_order_details:", e)
    exit2_sell_order_details = {}

# Load existing exit2_buy_order_details if the file exists
try:
    if os.path.exists(EXIT3_SELL_ORDER_DETAILS_FILE):
        with open(EXIT3_SELL_ORDER_DETAILS_FILE, 'rb') as file:
            exit3_sell_order_details = pickle.load(file)
    else:
        exit3_sell_order_details = {}
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading exit3_sell_order_details:", e)
    exit3_sell_order_details = {}

# Load existing executed_high_values if the file exists
try:
    if os.path.exists(EXECUTED_HIGH_VALUES_FILE):
        with open(EXECUTED_HIGH_VALUES_FILE, 'rb') as file:
            executed_high_values = pickle.load(file)
    else:
        executed_high_values = set()
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading executed_high_values:", e)
    executed_high_values = set()

# Load existing executed_low_values if the file exists
try:
    if os.path.exists(EXECUTED_LOW_VALUES_FILE):
        with open(EXECUTED_LOW_VALUES_FILE, 'rb') as file:
            executed_low_values = pickle.load(file)
    else:
        executed_low_values = set()
except (EOFError, FileNotFoundError) as e:
    print("An error occurred while loading executed_low_values:", e)
    # Handle the error, for example by re-creating the file or initializing executed_low_values to an empty set
    executed_low_values = set()


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

                    if status == 'COMPLETE' and tsym == 'TATAMOTORS-EQ' and norenordno not in unique_norenordnos:
                        # Increment the count for the norenordno if it exists in the dictionary
                        order_status_counts[norenordno] = order_status_counts.get(norenordno, 0) + 1
                        unique_norenordnos.add(norenordno)

                # Print the counts for each norenordno
                for norenordno, count in order_status_counts.items():
                    print(f"Count for norenordno {norenordno}: {count}")

                total_count = sum(order_status_counts.values())  # Calculate the total count again

            last_order_book = ret  # Update the last order book data

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
            # Handle connection or read timeouts
            print(f"Error: {e}. Retrying after {retry_delay} seconds...")
            time.sleep(retry_delay)

        except Exception as e:
            # Handle other unexpected exceptions
            print(f"Unexpected error: {e}. Retrying after {retry_delay} seconds...")
            time.sleep(retry_delay)

        time.sleep(60)  # Sleep for 5 seconds at the end of the loop


def print_tata_motors_data_loop():
    global tata_motors_lp_value, tata_motors_quantity

    while True:
        try:
            # Read data from data.pickle
            with open('data.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        tata_motors_lp_value = data.get('tata_motors_lp_value')
                        tata_motors_quantity = data.get('tata_motors_quantity')

                except EOFError:
                    # Reset the tata_motors_lp_value and tata_motors_quantity to None if EOFError
                    tata_motors_lp_value = None

        except FileNotFoundError:
            print("data.pickle not found. Skipping iteration.")
            # Reset the tata_motors_lp_value and tata_motors_quantity to None if data not found
            tata_motors_lp_value = None

        except Exception as e:
            print(f"An error occurred while reading data.pickle: {e}.")
            # Reset the tata_motors_lp_value and tata_motors_quantity to None in case of any other exception
            tata_motors_lp_value = None

        time.sleep(0.5)  # Adjust the interval as needed


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
    global store_high, buy_exit_point, buy_order_details, executed_high_values
    print(buy_order_details)
    print(executed_high_values)

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
        print("No data point corresponding to 9:15 AM found in the DataFrame calculate buy conditions.")
        return None

    # Get the index to start from 9:15 AM
    start_index = start_time_index[0]

    store_high = None
    sell_exit = None
    # Loop through each candle data starting from 9:15 AM

    for i in range(start_index, len(candle_df_reset)):
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
        print("Exit 1 : No buy order found ")
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
            print(filtered_candle_df)

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
                        print(f"For Order {orderno}:")
                        print(
                            f"Exit 1: satisfied. Candle High: {filtered_candle_df['inth'].iloc[i]}, Stored Low Price: {store_low}")

                elif store_low is not None and filtered_candle_df['intl'].iloc[i] > vwap_df_filtered.iloc[i]:
                    # If a subsequent candle with low above VWAP is found after the condition was satisfied, remove the
                    # stored high price
                    store_low = None
                    print("Stored Low Price removed. No exit 1 condition satisfied.")


def exit_2_calculation(candle_df):
    global lowest_point, buy_order_details
    # Reset the index to make the 'time' column a regular column again

    candle_df_reset = candle_df.reset_index()

    # Merge the two DataFrames based on the 'time' column
    merged_df = pd.merge(candle_df_reset, vwap_df, on='time')

    # Check if order details are available
    if not buy_order_details:
        print("Exit 2 : No buy order found ")

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
                print("No data available within the specified range.")
                return None

            # Find the lowest point in the 'intl' column (assuming this represents the low price)
            lowest_point = filtered_candle_df_2['intl'].min()
            print(f"Lowest point from 9:15 to Buy order Time: {lowest_point}")

    return lowest_point


def execute_buy_trade():
    global tata_motors_quantity, buy_order_details

    # If the current time is later than or equal to the desired execution time, execute the buy order
    ret = api.place_order(buy_or_sell='B', product_type='I',
                          exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                          quantity=tata_motors_quantity, discloseqty=0, price_type='MKT',
                          retention='DAY', remarks='my_order_001')

    # Extract the orderno from the ret value
    orderno = ret['norenordno']
    print("Order placed successfully.")
    print("Order Number:", orderno)

    order_history = api.single_order_history(orderno=orderno)

    if order_history:
        # Check the order status
        status = order_history[0].get('status')

        if status == 'COMPLETE':
            # Fetch the order timestamp
            order_timestamp = order_history[0].get('norentm')
            order_quantity = order_history[0].get('qty')

            # Check if the order has not been processed before
            if orderno not in buy_order_details:
                # Store the details in the global dictionary
                buy_order_details[orderno] = {
                    'Status': 'COMPLETE',
                    'Timestamp': order_timestamp,
                    'Quantity': order_quantity,
                    'trantype': 'B',  # Add custom field trantype with value "B" (Buy)
                    'remarks': 'my_order_001',  # Add custom field remarks to identify the buy order
                }
                # Save the updated buy_order_details dictionary to a file after removing the item
                with open(BUY_ORDER_DETAILS_FILE, 'wb') as file:
                    pickle.dump(buy_order_details, file)

    # Return the order details dictionary
    return buy_order_details


def execute_exit_trade_1():
    global buy_order_details, exit1_buy_order_details
    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                                  quantity=buy_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_001')

            # Extract the orderno from the ret value
            exit1_orderno = ret['norenordno']
            print("Exit order 1: Placed successfully.")
            print("Order Number:", exit1_orderno)

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
                        with open(EXIT1_BUY_ORDER_DETAILS_FILE, 'wb') as file:
                            pickle.dump(exit1_buy_order_details, file)

    # Return the order details dictionary
    return exit1_buy_order_details


def execute_exit_trade_2():
    global buy_order_details, exit2_buy_order_details
    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                                  quantity=buy_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_001')

            # Extract the orderno from the ret value
            exit2_orderno = ret['norenordno']
            print("Exit order 2: Placed successfully.")
            print("Order Number:", exit2_orderno)

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
                        with open(EXIT2_BUY_ORDER_DETAILS_FILE, 'wb') as file:
                            pickle.dump(exit2_buy_order_details, file)

    # Return the updated exit2_buy_order_details dictionary
    return exit2_buy_order_details


def exit_trade_14_55():
    global buy_order_details, exit3_buy_order_details

    for orderno, order_info in buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            buy_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to 14:55, execute the sell order
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                                  quantity=buy_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_001')

            # Extract the orderno from the ret value
            exit3_orderno = ret['norenordno']
            print("Exit order at 14:55 Placed successfully.")
            print("Order Number:", exit3_orderno)

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
                        with open(EXIT3_BUY_ORDER_DETAILS_FILE, 'wb') as file:
                            pickle.dump(exit3_buy_order_details, file)

    return exit3_buy_order_details


def buy_condition_check():
    global tata_motors_lp_value, store_high, sell_order_details, order_status_counts, total_count, executed_high_values, buy_order_details

    buy_order_executed = False
    max_retries = 2
    retries = 0

    while not buy_order_executed and retries < max_retries:
        # Check if the current time is after 15:00
        current_time = datetime.datetime.now().time()
        if current_time >= datetime.time(15, 0):
            executed_high_values.clear()  # Clear the executed_low_values set
            buy_order_details.clear()  # Clear the sell_order_details dictionary
            # Save the cleared sell_order_details dictionary to a pickle file
            with open(BUY_ORDER_DETAILS_FILE, 'wb') as file:
                pickle.dump(buy_order_details, file)
            # Save the updated executed_low_values set to a file after removing the item
            with open(EXECUTED_HIGH_VALUES_FILE, 'wb') as file:
                pickle.dump(executed_high_values, file)

        for orderno, order_info in sell_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'my_order_002':
                    pass
                else:
                    if any(isinstance(order_info, dict) and order_info.get('trantype') == 'B' for
                           orderno, order_info in buy_order_details.items()):
                        pass  # Do nothing if the sell order is already present
                    else:
                        # Check if the current time is before 14:20
                        current_time = datetime.datetime.now().time()
                        if current_time < datetime.time(14, 20):
                            # Check your sell conditions and place sell orders here
                            if tata_motors_lp_value is not None and store_high is not None:
                                if isinstance(tata_motors_lp_value, (int, float)) and isinstance(store_high,
                                                                                                 (int, float)):
                                    entry_price = store_high
                                    if tata_motors_lp_value > entry_price and tata_motors_lp_value < (entry_price + 2):
                                        if store_high not in executed_high_values:
                                            # Check if the current time is before 14:20
                                            current_time = datetime.datetime.now().time()
                                            if current_time < datetime.time(14, 20):
                                                time.sleep(3)  # Add a 5-second delay
                                                print("Buy for TATAMOTORS is placed...")
                                                buy_order_details = execute_buy_trade()
                                                print("Order Details:", buy_order_details)
                                                if any(isinstance(order_info, dict) and order_info.get(
                                                        'Status') == 'COMPLETE' for orderno, order_info in
                                                       buy_order_details.items()):
                                                    buy_order_executed = True
                                                    executed_high_values.add(store_high)
                                                    # Save the updated executed_low_values set to a file after removing
                                                    # the item
                                                    with open(EXECUTED_HIGH_VALUES_FILE, 'wb') as file:
                                                        pickle.dump(executed_high_values, file)

                                                    print("Buy order executed successfully.")
                                                else:
                                                    print('Buy Order not Executed')
                                                    retries += 1

                                                # Check if either of the conditions is reached and stop taking trades if
                                                # true
                                                if len(executed_high_values) >= 2 or total_count >= 6:
                                                    print("Either condition reached. Stopping further buy trades.")
                                                    break

        # Sleep statement outside the for loop
        time.sleep(1)  # Adjust the interval as needed


def exit_trade_1_loop():
    global buy_order_details, tata_motors_lp_value, store_low, exit1_buy_order_details

    # Initialize the exit1_order_executed flag outside the loop
    exit1_buy_order_executed = False

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
                    # Check if the current time is less than 14:55
                    if current_time < datetime.time(14, 55):
                        # Use the stored value of low_of_subsequent_candle_inner
                        if tata_motors_lp_value is not None and store_low is not None:
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if tata_motors_lp_value < store_low:
                                # Call the exit trade function here
                                execute_exit_trade_1()
                                # Store orderno before the inner loop
                                buy_orderno = orderno
                                for exit1_orderno, order_info_exit1 in exit1_buy_order_details.items():
                                    if isinstance(order_info_exit1, dict) and order_info_exit1.get(
                                            'Status') == 'COMPLETE':
                                        exit1_buy_order_executed = True
                                        # Remove the buy order details and exit1 order details from the dictionaries after exiting the trade
                                        buy_order_details.pop(buy_orderno)
                                        exit1_buy_order_details.pop(exit1_orderno)
                                        # Save the updated buy_order_details dictionary to a file after removing the item
                                        with open(BUY_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(buy_order_details, file)
                                        # Save the updated exit1_buy_order_details dictionary to a file after removing the item
                                        with open(EXIT1_BUY_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(exit1_buy_order_details, file)

                                        # Break the inner for loop as the trade exit is done
                                        break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)

        # Return the value of exit1_order_executed
        return exit1_buy_order_executed


def exit_trade_2_loop():
    global buy_order_details, tata_motors_lp_value, lowest_point, exit2_buy_order_details

    # Variable to track whether the exit2 order has been executed
    exit2_buy_order_executed = False

    while True:
        if not buy_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_002':
                    # Check if the current time is less than 14:55
                    if current_time < datetime.time(14, 55):
                        # Use the stored value of low_of_subsequent_candle_inner
                        if tata_motors_lp_value is not None and lowest_point is not None:
                            tata_motors_lp_value = float(tata_motors_lp_value)
                            lowest_point = float(lowest_point)
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if tata_motors_lp_value < lowest_point:
                                # Call the exit trade function here
                                execute_exit_trade_2()
                                # Store orderno before the inner loop
                                buy_orderno = orderno
                                for exit2_orderno, order_info_exit2 in exit2_buy_order_details.items():
                                    if isinstance(order_info_exit2, dict) and order_info_exit2.get(
                                            'Status') == 'COMPLETE':
                                        exit2_buy_order_executed = True
                                        # Remove the buy order details and exit1 order details from the dictionaries after exiting the trade
                                        buy_order_details.pop(buy_orderno)
                                        exit2_buy_order_details.pop(exit2_orderno)
                                        # Save the updated buy_order_details dictionary to a file after removing the item
                                        with open(BUY_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(buy_order_details, file)
                                        # Save the updated exit1_buy_order_details dictionary to a file after removing the item
                                        with open(EXIT1_BUY_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(exit2_buy_order_details, file)
                                        # Break the inner for loop as the trade exit is done
                                        break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)

        # Return the value of exit1_order_executed
        return exit2_buy_order_executed


def exit_trade_14_55_loop():
    global exit3_buy_order_details
    exit3_buy_order_executed = False
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
                    # Check if the current time is greater than 14:55
                    if current_time > datetime.time(14, 55):
                        exit_trade_14_55()
                        # Store orderno before the inner loop
                        buy_orderno = orderno
                        for exit3_orderno, order_info_exit3 in exit3_buy_order_details.items():
                            if isinstance(order_info_exit3, dict) and order_info_exit3.get(
                                    'Status') == 'COMPLETE':
                                exit3_buy_order_executed = True
                                # Remove the buy order details and exit1 order details from the dictionaries after exiting the trade
                                buy_order_details.pop(buy_orderno)
                                exit3_buy_order_details.pop(exit3_orderno)
                                # Save the updated buy_order_details dictionary to a file after removing the item
                                with open(BUY_ORDER_DETAILS_FILE, 'wb') as file:
                                    pickle.dump(buy_order_details, file)
                                # Save the updated exit1_buy_order_details dictionary to a file after removing the item
                                with open(EXIT1_BUY_ORDER_DETAILS_FILE, 'wb') as file:
                                    pickle.dump(exit3_buy_order_details, file)
                                # Break the inner for loop as the trade exit is done
                                break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)
        # Return the value of exit1_order_executed
        return exit3_buy_order_executed


def check_sell_entry_conditions(candle_df, vwap_df):
    global store_low_sell, sell_exit_point, sell_order_details, executed_low_values
    print(sell_order_details)
    print(executed_low_values)

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
        print("No data point corresponding to 9:15 AM found in the DataFrame to calculate sell conditions.")
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
                print('.....................................................................................')
                print(
                    f"Sell condition satisfied at {candle_df_reset['time'].iloc[i]}. Candle high: {candle_df_reset['inth'].iloc[i]}, Stored Low sell Price: {store_low_sell}")

        elif store_low_sell is not None and candle_df_reset['intl'].iloc[i] > vwap_df['VWAP'].iloc[i]:
            # If a subsequent candle with low above VWAP is found after the condition was satisfied, reset the
            # stored high price
            store_low_sell = None
            print(f"Stored low sell Price removed at {candle_df_reset['time'].iloc[i]}. No sell condition satisfied.")
            print('.....................................................................................')


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
        print("Exit 1 : No sell order found ")
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
            print(filtered_candle_df)

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
                        print(f"For Order {orderno}:")
                        print(
                            f"Exit 1: satisfied. Candle low: {filtered_candle_df['intl'].iloc[i]}, store_high_sell Price: {store_high_sell}")

                elif store_high_sell is not None and filtered_candle_df['inth'].iloc[i] < vwap_df_filtered.iloc[i]:
                    # If a subsequent candle with high below VWAP is found after the condition was satisfied, remove the
                    # stored high price
                    store_high_sell = None
                    print("store_high_sell Price removed. No exit 1 condition satisfied.")
                    print('.....................................................................................')


def exit_2_calculation_sell(candle_df):
    global highest_point, sell_order_details
    # Reset the index to make the 'time' column a regular column again

    candle_df_reset = candle_df.reset_index()

    # Merge the two DataFrames based on the 'time' column
    merged_df = pd.merge(candle_df_reset, vwap_df, on='time')

    # Check if order details are available
    if not sell_order_details:
        print("Exit 2 : No sell order found ")
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
                print("No data available within the specified range.")
                return None

            # Find the lowest point in the 'intl' column (assuming this represents the low price)
            highest_point = filtered_candle_df_2['inth'].max()
            print(f"highest point from 9:15 to sell order Time: {highest_point}")

    return highest_point


def execute_sell_trade():
    global tata_motors_quantity, sell_order_details
    # If the current time is later than or equal to the desired execution time, execute the buy order
    ret = api.place_order(buy_or_sell='S', product_type='I',
                          exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                          quantity=tata_motors_quantity, discloseqty=0, price_type='MKT',
                          retention='DAY', remarks='my_order_002')

    # Extract the orderno from the ret value
    orderno = ret['norenordno']
    print("Order placed successfully.")
    print("Order Number:", orderno)

    order_history = api.single_order_history(orderno=orderno)

    if order_history:
        # Check the order status
        status = order_history[0].get('status')

        if status == 'COMPLETE':
            # Fetch the order timestamp
            order_timestamp = order_history[0].get('norentm')
            order_quantity = order_history[0].get('qty')

            # Check if the order has not been processed before
            if orderno not in sell_order_details:
                # Store the details in the global dictionary
                sell_order_details[orderno] = {
                    'Status': 'COMPLETE',
                    'Timestamp': order_timestamp,
                    'Quantity': order_quantity,
                    'trantype': 'S',  # Add custom field trantype with value "B" (Buy)
                    'remarks': 'my_order_002',  # Add custom field remarks to identify the buy order
                }

                # Save the updated sell_order_details dictionary to a file
                with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                    pickle.dump(sell_order_details, file)

    # Return the order details dictionary
    return sell_order_details


def execute_exit_trade_1_sell():
    global sell_order_details, exit1_sell_order_details
    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            sell_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                                  quantity=sell_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_002')

            # Extract the orderno from the ret value
            exit1_sell_orderno = ret['norenordno']
            print("Sell Exit order 1: Placed successfully.")
            print("Order Number:", exit1_sell_orderno)

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
                        with open(EXIT1_SELL_ORDER_DETAILS_FILE, 'wb') as file:
                            pickle.dump(exit1_sell_order_details, file)

    # Return the order details dictionary
    return exit1_sell_order_details


def execute_exit_trade_2_sell():
    global sell_order_details, exit2_sell_order_details
    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            sell_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                                  quantity=sell_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_002')

            # Extract the orderno from the ret value
            exit2_sell_orderno = ret['norenordno']
            print("Sell Exit order 2: Placed successfully.")
            print("Order Number:", exit2_sell_orderno)

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
                        # Save the updated exit buy_order_details dictionary to a file after removing the item
                        with open(EXIT2_SELL_ORDER_DETAILS_FILE, 'wb') as file:
                            pickle.dump(exit2_sell_order_details, file)

    # Return the updated exit2_buy_order_details dictionary
    return exit2_sell_order_details


def exit_trade_14_55_sell():
    global sell_order_details, exit3_sell_order_details
    for orderno, order_info in sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            sell_order_quantity = order_info.get('Quantity')

            # If the current time is later than or equal to the desired execution time, execute the sell order
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NSE', tradingsymbol='TATAMOTORS-EQ',
                                  quantity=sell_order_quantity, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='exit_order_002')

            # Extract the orderno from the ret value
            exit3_sell_orderno = ret['norenordno']
            print("Sell Exit order at 14:55 Placed successfully.")
            print("Order Number:", exit3_sell_orderno)

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
                        with open(EXIT3_SELL_ORDER_DETAILS_FILE, 'wb') as file:
                            pickle.dump(exit3_sell_order_details, file)

    return exit3_sell_order_details


def sell_condition_check():
    global tata_motors_lp_value, store_low_sell, sell_order_details, order_status_counts, total_count, executed_low_values

    sell_order_executed = False
    max_retries = 2
    retries = 0

    while not sell_order_executed and retries < max_retries:
        # Check if the current time is after 15:00
        current_time = datetime.datetime.now().time()
        if current_time >= datetime.time(15, 0):
            executed_low_values.clear()  # Clear the executed_low_values set
            sell_order_details.clear()  # Clear the sell_order_details dictionary
            # Save the cleared sell_order_details dictionary to a pickle file
            with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                pickle.dump(sell_order_details, file)
            # Save the updated executed_low_values set to a file after removing the item
            with open(EXECUTED_LOW_VALUES_FILE, 'wb') as file:
                pickle.dump(executed_low_values, file)

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    pass
                else:
                    if any(isinstance(order_info, dict) and order_info.get('trantype') == 'S' for
                           orderno, order_info in sell_order_details.items()):
                        pass  # Do nothing if the sell order is already present
                    else:
                        # Check if the current time is before 14:20
                        current_time = datetime.datetime.now().time()
                        if current_time < datetime.time(14, 20):
                            # Check your sell conditions and place sell orders here
                            if tata_motors_lp_value is not None and store_low_sell is not None:
                                if isinstance(tata_motors_lp_value, (int, float)) and isinstance(store_low_sell,
                                                                                                 (int, float)):
                                    entry_price = store_low_sell
                                    if tata_motors_lp_value < entry_price and tata_motors_lp_value > (entry_price - 2):
                                        if store_low_sell not in executed_low_values:
                                            # Check if the current time is before 14:20
                                            current_time = datetime.datetime.now().time()
                                            if current_time < datetime.time(14, 20):
                                                time.sleep(2)  # Add a 5-second delay
                                                print("Sell condition for TATAMOTORS is TRUE! Order placed...")
                                                sell_order_details = execute_sell_trade()
                                                print("Order Details:", sell_order_details)
                                                if any(isinstance(order_info, dict) and order_info.get(
                                                        'Status') == 'COMPLETE' for orderno, order_info in
                                                       sell_order_details.items()):
                                                    sell_order_executed = True
                                                    executed_low_values.add(store_low_sell)
                                                    # Save the updated executed_low_values set to a file after removing
                                                    # the item
                                                    with open(EXECUTED_LOW_VALUES_FILE, 'wb') as file:
                                                        pickle.dump(executed_low_values, file)

                                                    print("Sell order executed successfully.")
                                                else:
                                                    print('Sell Order not Executed')
                                                    retries += 1

                                                # Check if either of the conditions is reached and stop taking trades if
                                                # true
                                                if len(executed_low_values) >= 2 or total_count >= 6:
                                                    print("Either condition reached. Stopping further sell trades.")
                                                    break

        # Sleep statement outside the for loop
        time.sleep(1)  # Adjust the interval as needed


def exit_trade_1_loop_sell():
    global sell_order_details, tata_motors_lp_value, store_high_sell, exit1_sell_order_details

    # Variable to track whether the exit2 order has been executed
    exit1_sell_order_executed = False

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
                    # Check if the current time is less than 14:55
                    if current_time < datetime.time(14, 55):
                        # Use the stored value of low_of_subsequent_candle_inner
                        if tata_motors_lp_value is not None and store_high_sell is not None:
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if tata_motors_lp_value < store_high_sell:
                                # Call the exit trade function here
                                execute_exit_trade_1_sell()
                                sell_orderno = orderno
                                for exit1_sell_orderno, order_info_exit1_sell in exit1_sell_order_details.items():
                                    if isinstance(order_info_exit1_sell, dict) and order_info_exit1_sell.get(
                                            'Status') == 'COMPLETE':
                                        exit1_sell_order_executed = True
                                        # Remove the buy order details and exit1 order details from the dictionaries after exiting the trade
                                        buy_order_details.pop(sell_orderno)
                                        exit1_sell_order_details.pop(exit1_sell_orderno)
                                        # Save the updated buy_order_details dictionary to a file after removing the item
                                        with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(sell_order_details, file)
                                        # Save the updated exit1_buy_order_details dictionary to a file after removing the item
                                        with open(EXIT1_SELL_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(exit1_sell_order_details, file)
                                        # Break the inner for loop as the trade exit is done
                                        break
        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)

        return exit1_sell_order_executed


def exit_trade_2_loop_sell():
    global sell_order_details, tata_motors_lp_value, highest_point, exit2_sell_order_details

    # Variable to track whether the message has been printed
    exit_trade_message_printed = False

    # Variable to track whether the exit2 order has been executed
    exit2_sell_order_executed = False

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
                    # Check if the current time is less than 14:55
                    if current_time < datetime.time(14, 55):
                        # Use the stored value of low_of_subsequent_candle_inner
                        if tata_motors_lp_value is not None and highest_point is not None:
                            tata_motors_lp_value = float(tata_motors_lp_value)
                            highest_point = float(highest_point)
                            # Check if the current market price (LTP) crosses the low value of the subsequent candle
                            if tata_motors_lp_value < highest_point:
                                # Call the exit trade function here
                                execute_exit_trade_2_sell()
                                sell_orderno = orderno
                                for exit2_sell_orderno, order_info_exit2_sell in exit2_sell_order_details.items():
                                    if isinstance(order_info_exit2_sell, dict) and order_info_exit2_sell.get(
                                            'Status') == 'COMPLETE':
                                        exit2_sell_order_executed = True
                                        # Remove the buy order details and exit1 order details from the dictionaries after exiting the trade
                                        buy_order_details.pop(sell_orderno)
                                        exit2_sell_order_details.pop(exit2_sell_orderno)
                                        # Save the updated buy_order_details dictionary to a file after removing the item
                                        with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(sell_order_details, file)
                                        # Save the updated exit1_buy_order_details dictionary to a file after removing the item
                                        with open(EXIT2_SELL_ORDER_DETAILS_FILE, 'wb') as file:
                                            pickle.dump(exit2_sell_order_details, file)
                                        # Break the inner for loop as the trade exit is done
                                        break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)

        return exit2_sell_order_executed


def exit_trade_14_55_loop_sell():
    global exit3_sell_order_details
    exit3_sell_order_executed = False
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
                    if current_time > datetime.time(14, 55):
                        exit_trade_14_55_sell()
                        sell_orderno = orderno
                        for exit3_sell_orderno, order_info_exit3_sell in exit3_sell_order_details.items():
                            if isinstance(order_info_exit3_sell, dict) and order_info_exit3_sell.get(
                                    'Status') == 'COMPLETE':
                                exit3_sell_order_executed = True
                                # Remove the buy order details and exit1 order details from the dictionaries after exiting the trade
                                buy_order_details.pop(sell_orderno)
                                exit3_sell_order_details.pop(exit3_sell_orderno)
                                # Save the updated buy_order_details dictionary to a file after removing the item
                                with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                                    pickle.dump(sell_order_details, file)
                                # Save the updated exit1_buy_order_details dictionary to a file after removing the item
                                with open(EXIT3_SELL_ORDER_DETAILS_FILE, 'wb') as file:
                                    pickle.dump(exit3_sell_order_details, file)
                                # Break the inner for loop as the trade exit is done
                                break

        # Add a sleep time of 1 second before the next iteration
        time.sleep(0.5)

        return exit3_sell_order_executed


def tatam_fetch_candle_data_loop():
    # Get the current date
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')

    # Define the time interval for the 5-minute candles on the current date
    start_time = datetime.datetime.strptime(f'{current_date} 09:15:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 15:30:00', '%d-%m-%Y %H:%M:%S')

    interval = 10

    # Wait for the next 5-minute mark before fetching and processing candle data
    next_update_time = get_next_interval_mark(interval)
    time_to_sleep = (next_update_time - datetime.datetime.now()).total_seconds()
    time.sleep(time_to_sleep)

    while True:
        # Fetch candle data (replace this with your implementation)
        candle_df = get_time_series('NSE', '3456', start_time, end_time, interval=10)

        if candle_df is not None:
            # Process the data (replace this with your implementation)
            print_candle_df(candle_df)
            calculate_vwap(candle_df)
            check_buy_entry_conditions(candle_df, vwap_df)
            exit_1_calculation(candle_df, vwap_df)
            exit_2_calculation(candle_df)
            check_sell_entry_conditions(candle_df, vwap_df)
            exit_1_calculation_sell(candle_df, vwap_df)
            exit_2_calculation_sell(candle_df)

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

    TATAM_data_thread = threading.Thread(target=print_tata_motors_data_loop)
    fetch_candle_data_thread = threading.Thread(target=tatam_fetch_candle_data_loop)
    buy_condition_thread = threading.Thread(target=buy_condition_check)
    exit_trade1_thread = threading.Thread(target=exit_trade_1_loop)
    exit_trade2_thread = threading.Thread(target=exit_trade_2_loop)
    exit_trade_14_55_thread = threading.Thread(target=exit_trade_14_55_loop)
    order_book_thread = threading.Thread(target=get_order_book_loop)
    sell_condition_thread = threading.Thread(target=sell_condition_check)
    sell_exit_trade1_thread = threading.Thread(target=exit_trade_1_loop_sell)
    sell_exit_trade2_thread = threading.Thread(target=exit_trade_2_loop_sell)
    sell_exit_trade_14_55_thread = threading.Thread(target=exit_trade_14_55_loop_sell)

    # Start the threads

    TATAM_data_thread.start()
    fetch_candle_data_thread.start()
    buy_condition_thread.start()
    exit_trade1_thread.start()
    exit_trade2_thread.start()
    exit_trade_14_55_thread.start()
    order_book_thread.start()
    sell_condition_thread.start()
    sell_exit_trade1_thread.start()
    sell_exit_trade2_thread.start()
    sell_exit_trade_14_55_thread.start()

    # Wait for all threads to complete
    fetch_candle_data_thread.join()
    buy_condition_thread.join()
    exit_trade1_thread.join()
    exit_trade2_thread.join()
    exit_trade_14_55_thread.join()
    order_book_thread.join()
    sell_condition_thread.join()
    sell_exit_trade1_thread.join()
    sell_exit_trade2_thread.join()
    sell_exit_trade_14_55_thread.join()

