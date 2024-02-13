from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import schedule


smoothed_stoch_rsi_k = None
rsi_values = None
formatted_rsi = None
formatted_store_high = 0
formatted_store_low = 0
store_low = None
ce_sl = 0
ce_tgt = 0
pe_sl = 0
pe_tgt = 0
midcap_lp = 0
total_count = 0
total_ce_count = 0
total_pe_count = 0
pe_tsym_values = 0
ce_tsym_values = 0
total_ce_count = 0
total_pe_count = 0

ce_buy_entry_trigger_price = 0
ce_buy_exit_trigger_price = 0
ce_sell_entry_trigger_price = 0
ce_sell_exit_trigger_price = 0
pe_buy_entry_trigger_price = 0
pe_buy_exit_trigger_price = 0
pe_sell_entry_trigger_price = 0
pe_sell_exit_trigger_price = 0


# Get the current date and time
current_date_time = datetime.datetime.now()
# Extract the month from the current date
current_month_abbrev = current_date_time.strftime("%b").upper()

print("Current Month:", current_month_abbrev)


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
    print('MIDCAP LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()

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
midcap_high = ohlc['midcap_high']
midcap_low = ohlc['midcap_low']
midcap_close = ohlc['midcap_close']

# Extract the string '2023-10-03 15:25:00' from the dictionary and add single quotes
midcap_remove_date = "'" + ohlc['midcap_remove_date'] + "'"
midcap_adding_next = "'" + ohlc['midcap_adding_next'] + "'"

PE_BUY_ORDER_DETAILS_FILE = 'mcn_pe_buy_order_details.pickle'
CE_BUY_ORDER_DETAILS_FILE = 'mcn_ce_buy_order_details.pickle'
PE_BUY_EXIT_ORDER_DETAILS_FILE = 'mcn_pe_buy_exit_order.pickle'
CE_BUY_EXIT_ORDER_DETAILS_FILE = 'mcn_ce_buy_exit_order.pickle'
CE_ORDER_DETAILS_FILE = 'mcn_ce_order_details.pickle'
PE_ORDER_DETAILS_FILE = 'mcn_pe_order_details.pickle'
CE_SL_ORDER_DETAILS_FILE = 'mcn_ce_sl_order.pickle'
CE_TGT_ORDER_DETAILS_FILE = 'mcn_ce_tgt_order.pickle'
CE_EXIT_ORDER_DETAILS_FILE = 'mcn_ce_exit_order.pickle'
PE_SL_ORDER_DETAILS_FILE = 'mcn_pe_sl_order.pickle'
PE_TGT_ORDER_DETAILS_FILE = 'mcn_pe_tgt_order.pickle'
PE_EXIT_ORDER_DETAILS_FILE = 'mcn_pe_exit_order.pickle'
EXECUTED_HIGH_VALUES_FILE = 'mcn_executed_high_values.pickle'
EXECUTED_LOW_VALUES_FILE = 'mcn_executed_low_values.pickle'


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
    

ce_buy_order_details: dict = load_data(CE_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_buy_exit_order_details: dict = load_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_buy_order_details: dict = load_data(PE_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_buy_exit_order_details: dict = load_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_order_details: dict = load_data(CE_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_order_details: dict = load_data(PE_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_sl_order_details: dict = load_data(CE_SL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_tgt_order_details: dict = load_data(CE_TGT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_exit_order_details: dict = load_data(CE_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_sl_order_details: dict = load_data(PE_SL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_tgt_order_details: dict = load_data(PE_TGT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_exit_order_details: dict = load_data(PE_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
executed_low_values: set = load_data(EXECUTED_LOW_VALUES_FILE, initialize_empty_set=True)
executed_high_values: set = load_data(EXECUTED_HIGH_VALUES_FILE, initialize_empty_set=True)



def save_data(file_path, data):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


def ltp_quantity_loop():
    global midcap_lp
    while True:
        try:
            ret = api.get_quotes(exchange='NSE', token='26074')

            # Check if ret is not None before accessing its attributes
            if ret is not None:
                ltp = ret.get("lp")
                if ltp is not None:
                    midcap_lp = float(ltp)
                    with open('midcap_ltp.txt', 'w') as file:
                        file.write(str(midcap_lp))
                else:
                    print("Error: 'lp' attribute is None")
                    midcap_lp = 0
            else:
                print("Error: 'ret' is None")
                midcap_lp = 0

        except Exception as e:
            print(f"An error occurred: {e}")
            midcap_lp = 0

        time.sleep(0.1)



def atm_loop():
    global midcap_lp, atmstrike, ce_tsym_values, pe_tsym_values, ce_order_details, pe_order_details

    while True:

        strike = int(round(midcap_lp/25,0)*25)

        month = 'FEB'
        atm = strike

        call_otm = strike + 100
        put_otm = strike - 100

        ce_txt = f'MIDCPNIFTY {month} {atm} CE'
        pe_txt = f'MIDCPNIFTY {month} {atm} PE'

        midcap_ls = 0
        ce_tsym_values = 0
        pe_tsym_values = 0
        ce_token_values = 0
        pe_token_values = 0
        ce_otm_token = 0
        pe_otm_token = 0
        
        try:
            ce_res = api.searchscrip('NFO', ce_txt)
            if ce_res:
                ce_df = pd.DataFrame(ce_res['values'])
                ce_tsym = ce_df.loc[0, 'tsym']
                ce_filtered_df = ce_df[ce_df['tsym'] == ce_tsym].sort_values(by='tsym')
                ce_tsym_values = ce_filtered_df['tsym'].tolist()
                ce_token_values = ce_filtered_df['token'].tolist()
                midcap_ls = ce_filtered_df['ls'].tolist()
            else:
                print("No 'values' key found in CE options result")
        
        except ValueError as ce_value_error:
            print(f"ValueError occurred while fetching CE options: {ce_value_error}")
            ce_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except TypeError as ce_type_error:
            print(f"TypeError occurred while fetching CE options: {ce_type_error}")
            ce_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except Exception as ce_general_error:
            print(f"Error occurred while fetching CE options: {ce_general_error}")
            ce_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        try:
            # Search for PE options
            pe_res = api.searchscrip('NFO', pe_txt)
            
            if pe_res:
                pe_df = pd.DataFrame(pe_res['values'])
                pe_tsym = pe_df.loc[0, 'tsym']
                pe_filtered_df = pe_df[pe_df['tsym'] == pe_tsym].sort_values(by='tsym')
                pe_tsym_values = pe_filtered_df['tsym'].tolist()
                pe_token_values = pe_filtered_df['token'].tolist()
            else:
                print("No 'values' key found in PE options result")
        
        except ValueError as pe_value_error:
            print(f"ValueError occurred while fetching PE options: {pe_value_error}")
            pe_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except TypeError as pe_type_error:
            print(f"TypeError occurred while fetching PE options: {pe_type_error}")
            pe_df = pd.DataFrame()  
        
        except Exception as pe_general_error:
            print(f"Error occurred while fetching PE options: {pe_general_error}")
            pe_df = pd.DataFrame()  

        if midcap_ls:
            lot_size = midcap_ls[0]
            qty = float(lot_size) * 1
            qty = int(qty)
            with open('mcn_qty.txt', 'w') as file:
                file.write(str(qty))

        ce_otm = midcap_lp + 100
        pe_otm = midcap_lp - 100
        
        ce_otm_strike = int(round(ce_otm/25,0)*25)
        pe_otm_strike = int(round(pe_otm/25,0)*25)
        
        ce_otm_txt = f'MIDCPNIFTY {month} {ce_otm_strike} CE'
        pe_otm_txt = f'MIDCPNIFTY {month} {pe_otm_strike} PE'

        ce_otm_tsym_values = 0
        pe_otm_tsym_values = 0

        try:
            ce_otm_res = api.searchscrip('NFO', ce_otm_txt)
            if ce_otm_res:
                ce_otm_df = pd.DataFrame(ce_otm_res['values'])
                ce_otm_tsym = ce_otm_df.loc[0, 'tsym']
                ce_otm_filtered_df = ce_otm_df[ce_otm_df['tsym'] == ce_otm_tsym].sort_values(by='tsym')
                ce_otm_tsym_values = ce_otm_filtered_df['tsym'].tolist()
                ce_otm_token = ce_otm_filtered_df['token'].tolist()
            else:
                print("No 'values' key found in CE otm options result")
        
        except ValueError as ce_value_error:
            print(f"ValueError occurred while fetching CE otm options: {ce_value_error}")
            ce_otm_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except TypeError as ce_type_error:
            print(f"TypeError occurred while fetching CE otm options: {ce_type_error}")
            ce_otm_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except Exception as ce_general_error:
            print(f"Error occurred while fetching CE otm options: {ce_general_error}")
            ce_otm_df = pd.DataFrame() 
        
        try:
            pe_otm_res = api.searchscrip('NFO', pe_otm_txt)
            if pe_otm_res:
                pe_otm_df = pd.DataFrame(pe_otm_res['values'])
                pe_otm_tsym = pe_otm_df.loc[0, 'tsym']
                pe_otm_filtered_df = pe_otm_df[pe_otm_df['tsym'] == pe_otm_tsym].sort_values(by='tsym')
                pe_otm_tsym_values = pe_otm_filtered_df['tsym'].tolist()
                pe_otm_token = pe_otm_filtered_df['token'].tolist()
            else:
                print("No 'values' key found in PE otm options result")
        
        except ValueError as pe_value_error:
            print(f"ValueError occurred while fetching PE otm options: {pe_value_error}")
            pe_otm_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except TypeError as ce_type_error:
            print(f"TypeError occurred while fetching PE otm options: {pe_type_error}")
            pe_otm_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except Exception as ce_general_error:
            print(f"Error occurred while fetching PE otm options: {pe_general_error}")
            pe_otm_df = pd.DataFrame() 

        # Assuming you want the first value in the list
        if ce_token_values:
            ce_token = ce_token_values[0]
            with open('mcn_ce_atm_token.txt', 'w') as file:
                file.write(ce_token)
        
        if pe_token_values:
            pe_token = pe_token_values[0]
            with open('mcn_pe_atm_token.txt', 'w') as file:
                file.write(pe_token)
        
        # Assuming you want the first value in the list
        if ce_otm_token:
            ce_otm_token = ce_otm_token[0]
            with open('mcn_ce_otm_token.txt', 'w') as file:
                file.write(ce_otm_token)
        
        if pe_otm_token:
            pe_otm_token = pe_otm_token[0]
            with open('mcn_pe_otm_token.txt', 'w') as file:
                file.write(pe_otm_token)

        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]
           
            with open('mcn_ce_atm.txt', 'w') as file:
                    file.write(ce_specific_tsym)
                
        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]
            
            with open('mcn_pe_atm.txt', 'w') as file:
                    file.write(pe_specific_tsym)
        
        if ce_otm_tsym_values:
            ce_otm_tsym_values = ce_otm_tsym_values[0]
           
            with open('mcn_ce_otm.txt', 'w') as file:
                file.write(str(ce_otm_tsym_values))
        
        if pe_otm_tsym_values:
            pe_otm_tsym_values = pe_otm_tsym_values[0]
           
            with open('mcn_pe_otm.txt', 'w') as file:
                file.write(str(pe_otm_tsym_values))  

        trigger_price_loop()         
        
        time.sleep(1)


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
    pd.set_option('display.max_rows', None)

    # Create a boolean mask to identify the rows to remove
    mask = candle_df.index == pd.to_datetime(midcap_remove_date)

    # Use the mask to filter and keep rows where the condition is False
    candle_df = candle_df[~mask]

    candle_df.reset_index(drop=True)

    candle_df = candle_df[['inth', 'intl', 'intc']].copy()
    # Set Pandas display option to show all rows
    pd.set_option('display.max_rows', None)

    # Create a new DataFrame for the manual input
    manual_data = pd.DataFrame({
        'inth': [midcap_high],
        'intl': [midcap_low],
        'intc': [midcap_close]
    }, index=pd.to_datetime([midcap_remove_date]))

    # Find the index location of '2023-10-03 15:25:00' in the original 'candle_df'
    insert_index = candle_df.index.get_loc(midcap_adding_next)

    # Split the original 'candle_df' into two parts, before and after the insert_index
    candle_df_before = candle_df.iloc[:insert_index + 1]
    candle_df_after = candle_df.iloc[insert_index + 1:]

    # Concatenate the parts with 'manual_data' in between to insert the values at '15:30:00'
    candle_df = pd.concat([candle_df_before, manual_data, candle_df_after])


    period = 14  # You can change this to your desired period

    candle_df['intc'] = pd.to_numeric(candle_df['intc'], errors='coerce')

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
        price_change = candle_df['price_change'].iloc[i]
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


def calculate_stoch_rsi(stoch_period=14, smoothing_period=7):
    global rsi_values, formatted_rsi, smoothed_stoch_rsi_k

    # Calculate the RSI's highest high and lowest low over the StochRSI period
    rsi_high = pd.Series(rsi_values).rolling(window=stoch_period).max()
    rsi_low = pd.Series(rsi_values).rolling(window=stoch_period).min()

    # Calculate the StochRSI %K value
    stoch_rsi_k = (pd.Series(rsi_values) - rsi_low) / (rsi_high - rsi_low)

    # Apply smoothing using a simple moving average (SMA)
    smoothed_stoch_rsi_k = stoch_rsi_k.rolling(window=smoothing_period).mean()


    return smoothed_stoch_rsi_k


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

def call_entry_conditions(candle_df, atr_df):
    global smoothed_stoch_rsi_k, store_low, ce_sl, ce_tgt, formatted_store_low, store_low
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

    atr = 0 
    store_low = None

    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check if the index 'i' is within the valid range of smoothed_stoch_rsi_k
        if 0 <= i < len(smoothed_stoch_rsi_k):
            # Access a specific element in the Series and convert it to a float
            formatted_rsi_float = float(smoothed_stoch_rsi_k.iloc[i])

            if prev_formatted_rsi_float is not None:
                if prev_formatted_rsi_float >= 0.70 and formatted_rsi_float < 0.70:
    
                    sell_entry_condition = True 

                    if sell_entry_condition:
                        # This is where you execute your buy action
                        store_low = candle_df_reset['intl'].iloc[i]
                        atr = atr_df['atr'].iloc[i]

                        # Format to display only two decimal places
                        formatted_atr = "{:.2f}".format(atr)
                        formatted_store_low = "{:.2f}".format(store_low)

                        # Convert formatted_atr to a float if it's not already
                        formatted_atr = float(formatted_atr)
                        formatted_store_low = float(formatted_store_low)
                        sl = formatted_atr
                        tgt = formatted_atr * 2

                        if formatted_store_low and formatted_atr:
                            ce_sl = formatted_store_low + sl
                            ce_tgt = formatted_store_low - tgt
                            
                            #print('SELL CONDITION MET AT',candle_df_reset['time'].iloc[i], 'RSI', formatted_rsi_float, 'STORE LOW', formatted_store_low, 
                                  #'ATR', formatted_atr, 'SL', ce_sl, 'TGT', ce_tgt)

                elif prev_formatted_rsi_float <= 0.70 and formatted_rsi_float > 0.70:
                    store_low = None
                    atr = 0
                    formatted_store_low = 0
                    

            # Update the previous value with the current value
            prev_formatted_rsi_float = formatted_rsi_float


def put_entry_conditions(candle_df, atr_df):
    global smoothed_stoch_rsi_k, formatted_store_high, pe_sl, pe_tgt, store_high

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

    atr = 0
    store_high = None


    # Loop through each candle data starting from 9:15 AM
    for i in range(start_index, len(candle_df_reset)):
        # Check if the index 'i' is within the valid range of smoothed_stoch_rsi_k
        if 0 <= i < len(smoothed_stoch_rsi_k):
            # Access a specific element in the Series and convert it to a float
            formatted_rsi_float = float(smoothed_stoch_rsi_k.iloc[i])

            if prev_formatted_rsi_float is not None:
                if prev_formatted_rsi_float <= 0.30 and formatted_rsi_float > 0.30:
                                        
                    buy_entry_condition = True  # Modify this as needed

                    if buy_entry_condition:
                        # This is where you execute your buy action
                        store_high = candle_df_reset['inth'].iloc[i]
                        atr = atr_df['atr'].iloc[i]

                        # Format to display only two decimal places
                        formatted_atr = "{:.2f}".format(atr)
                        formatted_store_high = "{:.2f}".format(store_high)

                        # Convert formatted_atr to a float if it's not already
                        formatted_atr = float(formatted_atr)
                        formatted_store_high = float(formatted_store_high)
                        sl = formatted_atr
                        tgt = formatted_atr * 2

                        if formatted_store_high and formatted_atr:
                            pe_sl = formatted_store_high - sl
                            pe_tgt = formatted_store_high + tgt

                            #print('BUY CONDITION MET AT',candle_df_reset['time'].iloc[i], 'RSI', formatted_rsi_float, 'STORE HIGH', formatted_store_high, 
                                  #'ATR', formatted_atr, 'SL', pe_sl, 'TGT', pe_tgt)

                elif prev_formatted_rsi_float >= 0.30 and formatted_rsi_float < 0.30:
                    store_high = None
                    atr = 0
                    formatted_store_high = 0

            # Update the previous value with the current value
            prev_formatted_rsi_float = formatted_rsi_float

def exits_token_loop():
    global ce_order_details, pe_order_details
    
    for orderno, order_info in ce_order_details.items():
        if isinstance(order_info, dict):  
            ce_token_str = order_info.get('ce_token', 0) 
            with open('mcn_ce_sell_token.txt', 'w') as file:
                file.write(ce_token_str)
            
    for orderno, order_info in pe_order_details.items():
        if isinstance(order_info, dict):
            pe_token_str = order_info.get('pe_token', 0)  
            with open('mcn_pe_sell_token.txt', 'w') as file:
                file.write(str(pe_token_str))
    
    for orderno, order_info in ce_buy_order_details.items():
        if isinstance(order_info, dict):  
            ce_buy_token_str = order_info.get('ce_buy_token', 0) 
            with open('mcn_ce_buy_token.txt', 'w') as file:
                file.write(ce_buy_token_str)
            
    for orderno, order_info in pe_buy_order_details.items():
        if isinstance(order_info, dict): 
            pe_token_str = order_info.get('pe_buy_token', 0)  
            with open('mcn_pe_buy_token.txt', 'w') as file:
                file.write(str(pe_token_str))


def trigger_price_loop():
    global ce_buy_entry_trigger_price, ce_buy_exit_trigger_price, ce_sell_entry_trigger_price, ce_sell_exit_trigger_price, pe_buy_entry_trigger_price, pe_buy_exit_trigger_price, pe_sell_entry_trigger_price, pe_sell_exit_trigger_price

    ce_otm_token = None
    ce_buy_token = None
    ce_atm_token = None
    ce_sell_token = None
    pe_otm_token = None
    pe_buy_token = None
    pe_atm_token = None
    pe_sell_token = None


    try:
        with open('mcn_ce_otm_token.txt', 'r') as file:
            ce_otm_token = file.read()
    except FileNotFoundError as e:
        ce_otm_token = 0
        #print(f"Error reading mcn_ce_otm_token.txt: {e}")
    try:
        with open('mcn_ce_buy_token.txt', 'r') as file:
            ce_buy_token = file.read()
    except FileNotFoundError as e:
        ce_buy_token = 0
        #print(f"Error reading mcn_ce_buy_token.txt: {e}")
    try:
        with open('mcn_ce_atm_token.txt', 'r') as file:
            ce_atm_token = file.read()
    except FileNotFoundError as e:
        ce_atm_token = 0
        #print(f"Error reading ce_atm_token.txt: {e}")

    try:
        with open('mcn_ce_sell_token.txt', 'r') as file:
            ce_sell_token = file.read()
    except FileNotFoundError as e:
        ce_sell_token = 0
        #print(f"Error reading ce_sell_token.txt: {e}")

    try:
        with open('mcn_pe_otm_token.txt', 'r') as file:
            pe_otm_token = file.read()
    except FileNotFoundError as e:
        pe_otm_token  = 0
       # print(f"Error reading mcn_pe_otm_token.txt: {e}")

    try:
        with open('mcn_pe_buy_token.txt', 'r') as file:
            pe_buy_token = file.read()
    except FileNotFoundError as e:
        pe_buy_token = 0
        #print(f"Error reading mcn_pe_buy_token.txt: {e}")
    try:
        with open('mcn_pe_atm_token.txt', 'r') as file:
            pe_atm_token = file.read()
    except FileNotFoundError as e:
        print(f"Error reading pe_atm_token.txt: {e}")
    try:
        with open('mcn_pe_sell_token.txt', 'r') as file:
            pe_sell_token = file.read()
    except FileNotFoundError as e:
        pe_sell_token = 0
        #print(f"Error reading mcn_pe_sell_token.txt: {e}")
    
    try:
        ce_buy_res = api.get_quotes(exchange='NFO', token=str(ce_otm_token))
        ce_buy_lp = ce_buy_res.get("lp")

        if ce_buy_lp is not None:
            ce_buy_lp = float(ce_buy_lp)
            ce_buy_trigger_prc = ce_buy_lp * 0.20
            ce_buy_trigger = ce_buy_lp + ce_buy_trigger_prc
            ce_buy_entry_trigger_price = f'{round(ce_buy_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for ce_otm_token:")
    except Exception as e:
        ce_buy_res = 0
        #print('An error occurred while fetching ce_lp for ce_otm_token')
    
    try:
        ce_buy_exit_res = api.get_quotes(exchange='NFO', token=str(ce_buy_token))
        ce_buy_exit_lp = ce_buy_exit_res.get("lp")
        
        if ce_buy_exit_lp is not None:
            ce_buy_exit_lp = float(ce_buy_exit_lp)
            ce_buy_exit_trigger_prc = ce_buy_exit_lp * 0.20
            ce_buy_exit_trigger = ce_buy_exit_lp - ce_buy_exit_trigger_prc
            ce_buy_exit_trigger_price = f'{round(ce_buy_exit_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for ce_buy_token:")
    except Exception as e:
        ce_buy_exit_res = 0
        #print('An error occurred while fetching ce_lp for ce_buy_token')
    
    try:
        ce_sell_res = api.get_quotes(exchange='NFO', token=str(ce_atm_token))
        ce_sell_lp = ce_sell_res.get("lp")

        if ce_sell_lp is not None:
            ce_sell_lp = float(ce_sell_lp)
            ce_sell_trigger_prc = ce_buy_lp * 0.20
            ce_sell_trigger = ce_sell_lp - ce_sell_trigger_prc
            ce_sell_entry_trigger_price = f'{round(ce_sell_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for ce_atm_token:")
    except Exception as e:
        ce_sell_res = 0
        #print('An error occurred while fetching ce_lp for ce_atm_token')
    
    try:
        ce_sell_exit_res = api.get_quotes(exchange='NFO', token=str(ce_sell_token))
        ce_sell_exit_lp = ce_sell_exit_res.get("lp")
        
        if ce_sell_exit_lp is not None:
            ce_sell_exit_lp = float(ce_sell_exit_lp)
            ce_sell_exit_trigger_prc = ce_sell_exit_lp * 0.20
            ce_sell_exit_trigger = ce_sell_exit_lp + ce_sell_exit_trigger_prc
            ce_sell_exit_trigger_price = f'{round(ce_sell_exit_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for ce_sell_token:")
    except Exception as e:
        ce_sell_exit_res = 0
        #print('An error occurred while fetching ce_lp for ce_sell_token')
    
    try:
        pe_buy_res = api.get_quotes(exchange='NFO', token=str(pe_otm_token))
        pe_buy_lp = pe_buy_res.get("lp")

        if pe_buy_lp is not None:
            pe_buy_lp = float(pe_buy_lp)
            pe_buy_trigger_prc = pe_buy_lp * 0.20
            pe_buy_trigger = pe_buy_lp + pe_buy_trigger_prc
            pe_buy_entry_trigger_price = f'{round(pe_buy_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for pe_otm_token:")
    except Exception as e:
        pe_buy_res = 0
        #print('An error occurred while fetching ce_lp for pe_otm_token')
    
    try:
        pe_buy_exit_res = api.get_quotes(exchange='NFO', token=str(pe_buy_token))
        pe_buy_exit_lp = pe_buy_exit_res.get("lp")
        
        if pe_buy_exit_lp is not None:
            pe_buy_exit_lp = float(pe_buy_exit_lp)
            pe_buy_exit_trigger_prc = pe_buy_exit_lp * 0.20
            pe_buy_exit_trigger = pe_buy_exit_lp - pe_buy_exit_trigger_prc
            pe_buy_exit_trigger_price = f'{round(pe_buy_exit_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for pe_buy_token:")
    except Exception as e:
        pe_buy_exit_res = 0
        #print('An error occurred while fetching ce_lp for pe_buy_token')
    
    try:
        pe_sell_res = api.get_quotes(exchange='NFO', token=str(pe_atm_token))
        pe_sell_lp = pe_sell_res.get("lp")

        if pe_sell_lp is not None:
            pe_sell_lp = float(pe_sell_lp)
            pe_sell_trigger_prc = pe_buy_lp * 0.20
            pe_sell_trigger = pe_sell_lp - pe_sell_trigger_prc
            pe_sell_entry_trigger_price = f'{round(pe_sell_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for pe_atm_token:")
    except Exception as e:
        pe_sell_res = 0
        #print('An error occurred while fetching ce_lp for pe_atm_token')
    
    try:
        pe_sell_exit_res = api.get_quotes(exchange='NFO', token=str(pe_sell_token))
        pe_sell_exit_lp = pe_sell_exit_res.get("lp")
        
        if pe_sell_exit_lp is not None:
            pe_sell_exit_lp = float(pe_sell_exit_lp)
            pe_sell_exit_trigger_prc = pe_sell_exit_lp * 0.20
            pe_sell_exit_trigger = pe_sell_exit_lp + pe_sell_exit_trigger_prc
            pe_sell_exit_trigger_price = f'{round(pe_sell_exit_trigger):.2f}'
        else:
            print("Warning: 'lp' attribute is None for pe_sell_token:")
    except Exception as e:
        pe_sell_exit_res = 0
        #print('An error occurred while fetching pe_lp for pe_sell_token')


def ce_buy_order():
        global ce_otm_symbol, ce_buy_order_details, ce_buy_entry_trigger_price

        ce_otm = 0
        try:
            with open('mcn_ce_otm.txt', 'r') as file:
                ce_otm = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")
        try:
            with open('mcn_qty.txt', 'r') as file:
                qty = file.read()
                qty = float(qty)
        except FileNotFoundError as e:
            print(f"Error reading bnf_qty.txt: {e}")
            qty = 75
        except ValueError as e:
            qty = 75  # or any default value
            print(f"Error converting to float: {e}")
        
        print('CE BUY ORDER PLACED')

        # Assuming you want the first value in the list
        if ce_otm:

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_otm,
                                  quantity=qty, discloseqty=0, price_type='LMT', 
                                  price=ce_buy_entry_trigger_price,
                                  retention='DAY', remarks='pe_buy_order')
            orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    status = order_history[0].get('status')

                    if status == 'COMPLETE':
                        tsym = order_history[0].get('tsym')
                        ce_buy_token = order_history[0].get('token')
                        
                        if orderno not in ce_buy_order_details:
                            ce_buy_order_details[orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'B',
                                'remarks': 'ce_buy_order',
                                'ce_buy_tsym': tsym,
                                'ce_buy_token': ce_buy_token,
                            }
                            save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)
                            # Exit the loop once ce_order_details is populated
                            break

        # Return the order details dictionary
        return ce_buy_order_details


def ce_buy_exit_order():
    global ce_buy_order_details, ce_buy_exit_order_details, ce_buy_exit_trigger_price

    qty = None

    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")

    
    print('CE BUY EXIT ORDER PLACED')

    for orderno, order_info in ce_buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_buy_exit_symbol = order_info.get('ce_buy_tsym')
            
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_buy_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=ce_buy_exit_trigger_price,
                                  retention='DAY', remarks='ce_buy_exit_order')
            ce_buy_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=ce_buy_exit_orderno)
                if order_history:
                    status = order_history[0].get('status')
                    if status == 'COMPLETE':
                        if ce_buy_exit_orderno not in ce_buy_exit_order_details:
                            ce_buy_exit_order_details[ce_buy_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',  
                                'remarks': 'ce_buy_exit_order',  
                                }
                            save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                            # Exit the loop once ce_order_details is populated
                            break
    
    # Return the order details dictionary
    return ce_buy_exit_order_details


def ce_order_execute():
    global ce_tsym_values, ce_order_details, ce_sell_entry_trigger_price

    ce_atm = None
    qty = None
    

    try:
        with open('mcn_ce_atm.txt', 'r') as file:
                ce_atm = file.read()
    except FileNotFoundError as e:
            print(f"Error reading ce_atm.txt: {e}")
    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading sensex_qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")
    
    print('CE SELL ORDER PLACED')

    if ce_atm:
        ret = api.place_order(buy_or_sell='S', product_type='I',
                              exchange='NFO', tradingsymbol=ce_atm,
                              quantity=qty, discloseqty=0, price_type='LMT', 
                              price=ce_sell_entry_trigger_price,
                              retention='DAY', remarks='ce_buy_order')
        orderno = ret['norenordno']

        while True:
            order_history = api.single_order_history(orderno=orderno)
            
            if order_history:
                status = order_history[0].get('status')
                
                if status == 'COMPLETE':
                    ce_token = order_history[0].get('token')
                    ce_avprc = order_history[0].get('avgprc')
                    ce_tsym = order_history[0].get('tsym')
                    
                    if orderno not in ce_order_details:
                        ce_order_details[orderno] = {
                            'Status': 'COMPLETE',
                            'trantype': 'S',
                            'remarks': 'ce_order',
                            'ce_avgprc': ce_avprc,
                            'ce_tsym': ce_tsym,
                            'ce_token': ce_token,
                            }
                        save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                        break
     
    # Return the order details dictionary
    return ce_order_details


def ce_exit_order():
    global ce_order_details, ce_exit_order_details, ce_sell_exit_trigger_price

    qty = None

    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")
    
    print('CE SELL EXIT ORDER PLACED')

    for orderno, order_info in ce_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_sell_exit_symbol = order_info.get('ce_tsym')
            
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_sell_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', 
                                  price=ce_sell_exit_trigger_price,
                                  retention='DAY', remarks='ce_exit_order')
            # Extract the orderno from the ret value
            ce_exit_orderno = ret['norenordno']
            
            while True:
                order_history = api.single_order_history(orderno=ce_exit_orderno)
                
                if order_history:
                    status = order_history[0].get('status')
                    
                    if status == 'COMPLETE':
                        if ce_exit_orderno not in ce_exit_order_details:
                            ce_exit_order_details[ce_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'B',  
                                'remarks': 'ce_exit_order',  
                                }
                            save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                            break
    
    # Return the order details dictionary
    return ce_exit_order_details



def ce_order_place():
    global ce_order_details, ce_sl, executed_low_values, ce_buy_order_details, pe_buy_order_details, ce_tgt, formatted_store_low, pe_order_details, total_count, total_ce_count, total_pe_count, midcap_lp

    max_retries = 2  # Maximum number of retries for placing the buy order
    trades = 5 #Total trades
    retries = 0  # Counter for retries
    previous_ltp = None
    
    while retries < max_retries:
        midcap_lp = float(midcap_lp)
        formatted_store_low = float(formatted_store_low)
        
        if midcap_lp and formatted_store_low and previous_ltp:
            if not ce_order_details and not ce_buy_order_details and not pe_order_details and not pe_buy_order_details:
                current_time = datetime.datetime.now().time()
                if current_time < datetime.time(15, 10):
                    if total_count < trades and formatted_store_low not in executed_low_values:
                            if midcap_lp < formatted_store_low:
                                if previous_ltp >= formatted_store_low:
                                    ce_buy_order_details = ce_buy_order()
                                    time.sleep(0.1)
                                    ce_order_details = ce_order_execute()
                                    time.sleep(5)
                                    if ce_buy_order_details and ce_order_details:
                                        total_ce_count += 1  # Increment the total buy count
                                        total_count = total_ce_count + total_pe_count
                                        print(total_count)
                                        call_sl = ce_sl
                                        call_tgt = ce_tgt  
                                        store_low = formatted_store_low
                                        with open('mcn_store_low.txt', 'w') as file:
                                            file.write(str(store_low))
                                        with open('mcn_call_sl.txt', 'w') as file:
                                            file.write(str(call_sl))
                                        with open('mcn_tgt.txt', 'w') as file:
                                            file.write(str(call_tgt))
                                        exits_token_loop() 
                                        time.sleep(0.1)
                                        exits_token_loop()
                                        time.sleep(0.1)
                                        exits_token_loop()
                                    else:
                                        retries += 1
                                        break                    

        previous_ltp = midcap_lp
        time.sleep(0.1)  

def ce_exit_loop():
    global ce_order_details, executed_low_values, ce_buy_exit_order_details, ce_buy_order_details, ce_sl, ce_tgt, midcap_lp, ce_exit_order_details, executed_low_values, formatted_store_low

    while True:

        current_time = datetime.datetime.now().time()

        if ce_order_details:
            if ce_buy_order_details:
                try:
                    with open('mcn_call_sl.txt', 'r') as file:
                        call_sl = file.read()
                        call_sl = float(call_sl)
                except FileNotFoundError as e:
                    call_sl = 0
                    print(f"Error reading call_sl.txt: {e}")
                except ValueError as e:
                    call_sl = 0  # or any default value
                    print(f"Error converting to float: {e}")
                    
                try:
                    with open('mcn_call_tgt.txt', 'r') as file:
                        call_tgt = file.read()
                        call_tgt = float(call_tgt)
                except FileNotFoundError as e:
                    call_tgt = 0
                    print(f"Error reading call_tgt.txt: {e}")
                except ValueError as e:
                    call_tgt = 0  # or any default value
                    print(f"Error converting to float: {e}")
                
                try:
                    with open('mcn_store_low.txt', 'r') as file:
                        store_low = file.read()
                        store_low = float(store_low)
                except FileNotFoundError as e:
                    store_low = 0
                    print(f"Error reading store_low.txt: {e}")
                except ValueError as e:
                    store_low = 0  # or any default value
                    print(f"Error converting to float: {e}")

                if midcap_lp and call_sl:
                    if midcap_lp >= call_sl:
                        ce_exit_order()
                        time.sleep(0.1)
                        ce_buy_exit_order()
                        time.sleep(2)
                        if ce_exit_order_details and ce_buy_exit_order_details:
                            ce_order_details.clear()
                            ce_exit_order_details.clear()
                            ce_buy_order_details.clear()
                            ce_buy_exit_order_details.clear()
                            save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                            save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                            save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)
                            save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                            with open('mcn_call_sl.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            with open('mcn_call_tgt.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                                time.sleep(2)
                                
                    if midcap_lp and call_tgt:
                        if midcap_lp <= call_tgt:
                            ce_exit_order()
                            time.sleep(0.1)
                            ce_buy_exit_order()
                            time.sleep(2)
                            if ce_exit_order_details and ce_buy_exit_order_details:
                                ce_order_details.clear()
                                ce_exit_order_details.clear()
                                ce_buy_order_details.clear()
                                ce_buy_exit_order_details.clear()
                                save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                                save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                                save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)
                                save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                                executed_low_values.add(store_low) 
                                save_data(EXECUTED_LOW_VALUES_FILE, executed_low_values)
                                with open('mcn_call_sl.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                with open('mcn_call_tgt.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                    time.sleep(2)
                                
                    if midcap_lp:
                        if current_time > datetime.time(15, 20):
                            ce_exit_order()
                            time.sleep(0.1)
                            ce_buy_exit_order()
                            time.sleep(2)
                            if ce_exit_order_details and ce_buy_exit_order_details:
                                ce_order_details.clear()
                                ce_exit_order_details.clear()
                                ce_buy_order_details.clear()
                                ce_buy_exit_order_details.clear()
                                save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                                save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                                save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)
                                save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                                with open('mcn_call_sl.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                with open('mcn_call_tgt.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                    time.sleep(2)
                                   
        time.sleep(0.1) 


def pe_buy_order():
    global pe_otm_symbol, pe_buy_order_details

    pe_otm = None
    qty = None
    

    try:
        with open('mcn_pe_otm.txt', 'r') as file:
                pe_otm = file.read()
    except FileNotFoundError as e:
            print(f"Error reading sensex_pe_otm.txt: {e}")
    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading sensex_qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")
    
    print('PE BUY ORDER PLACED')

    if pe_otm:
        ret = api.place_order(buy_or_sell='B', product_type='I', exchange='NFO', 
                              tradingsymbol=pe_otm, quantity=qty, 
                              discloseqty=0, price_type='LMT', 
                              price=pe_buy_entry_trigger_price, retention='DAY', 
                              remarks='pe_buy_order')
        orderno = ret['norenordno']
        
        while True:
            order_history = api.single_order_history(orderno=orderno)
            
            if order_history:
                status = order_history[0].get('status')
                
                if status == 'COMPLETE':
                    pe_buy_token = order_history[0].get('token')
                    tsym = order_history[0].get('tsym')
                    
                    if orderno not in pe_buy_order_details:
                        pe_buy_order_details[orderno] = {
                            'Status': 'COMPLETE',
                            'trantype': 'B',
                            'remarks': 'pe_buy_order',
                            'pe_buy_tsym': tsym,
                            'pe_buy_token': pe_buy_token,
                            }
                        save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)
                        break
    
    return pe_buy_order_details


def pe_buy_exit_order():
    global pe_buy_order_details, pe_buy_exit_order_details, pe_buy_exit_trigger_price

    qty = None

    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")
    
    
    print('PE BUY EXIT ORDER PLACED')

    for orderno, order_info in pe_buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_buy_exit_symbol = order_info.get('pe_buy_tsym')
            
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_buy_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=pe_buy_exit_trigger_price,
                                  retention='DAY', remarks='ce_buy_exit_order')
            pe_buy_exit_orderno = ret['norenordno']
            
            while True:
                order_history = api.single_order_history(orderno=pe_buy_exit_orderno)
                
                if order_history:
                    status = order_history[0].get('status')
                    
                    if status == 'COMPLETE':
                        if pe_buy_exit_orderno not in pe_buy_exit_order_details:
                            pe_buy_exit_order_details[pe_buy_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',  
                                'remarks': 'pe_buy_exit_order',  
                                }
                            save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                            break
    return pe_buy_exit_order_details


def pe_order_execute():
    global pe_tsym_values, pe_order_details, pe_sell_entry_trigger_price

    pe_atm = None
    qty = None

    try:
        with open('mcn_pe_atm.txt', 'r') as file:
                pe_atm = file.read()
    except FileNotFoundError as e:
            print(f"Error reading pe_atm.txt: {e}")
    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading sensex_qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")
    
    print('PE SELL ORDER PLACED')

    if pe_atm:
        
        ret = api.place_order(buy_or_sell='S', product_type='I',
                              exchange='NFO', tradingsymbol=pe_atm,
                              quantity=qty, discloseqty=0, price_type='LMT', price=pe_sell_entry_trigger_price,
                              retention='DAY', remarks='pe_sell_order')
        orderno = ret['norenordno']

        while True:
            order_history = api.single_order_history(orderno=orderno)
            
            if order_history:
                status = order_history[0].get('status')
                
                if status == 'COMPLETE':
                    pe_token = order_history[0].get('token')
                    pe_avprc = order_history[0].get('avgprc')
                    pe_tsym = order_history[0].get('tsym')
                    
                    if orderno not in pe_order_details:
                        pe_order_details[orderno] = {
                            'Status': 'COMPLETE',
                            'trantype': 'S',
                            'remarks': 'pe_order',
                            'pe_avgprc': pe_avprc,
                            'pe_tsym': pe_tsym,
                            'pe_token': pe_token,
                            }
                        save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                        break
    
    return pe_order_details

def pe_exit_order():
    global pe_order_details, pe_exit_order_details, pe_sell_exit_trigger_price

    qty = None

    try:
        with open('mcn_qty.txt', 'r') as file:
            qty = file.read()
            qty = float(qty)
    except FileNotFoundError as e:
        print(f"Error reading mcn_qty.txt: {e}")
        qty = 75
    except ValueError as e:
        qty = 75  # or any default value
        print(f"Error converting to float: {e}")

    print('PE SELL EXIT ORDER PLACED')
    
    for orderno, order_info in pe_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_sell_exit_symbol = order_info.get('pe_tsym')
            
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_sell_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', 
                                  price=pe_sell_exit_trigger_price,
                                  retention='DAY', remarks='ce_exit_order')
            pe_exit_orderno = ret['norenordno']
            
            while True:
                order_history = api.single_order_history(orderno=pe_exit_orderno)
                if order_history:
                    status = order_history[0].get('status')
                    if status == 'COMPLETE':
                        if pe_exit_orderno not in pe_exit_order_details:
                            pe_exit_order_details[pe_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'B',  
                                'remarks': 'pe_exit_order',  
                                }
                            save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                            break
        
    return pe_exit_order_details


def pe_order_place():
    global ce_order_details, executed_high_values, pe_sl, pe_tgt, formatted_store_high, pe_order_details, pe_buy_order_details, ce_buy_order_details, total_count, total_ce_count, total_pe_count, midcap_lp

    max_retries = 2  # Maximum number of retries for placing the buy order
    trades = 5
    retries = 0  # Counter for retries
    previous_ltp = None
    
    while retries < max_retries:
        midcap_lp = float(midcap_lp)
        formatted_store_high = float(formatted_store_high)
        if midcap_lp and formatted_store_high and previous_ltp:
            if not ce_order_details and not pe_order_details and not pe_buy_order_details and not ce_buy_order_details:
                current_time = datetime.datetime.now().time()
                if current_time < datetime.time(15, 10):
                    if total_count < trades and formatted_store_high not in executed_high_values:
                            if midcap_lp > formatted_store_high:
                                if previous_ltp <= formatted_store_high:
                                    pe_buy_order_details = pe_buy_order()
                                    time.sleep(0.1)
                                    pe_order_details = pe_order_execute()
                                    time.sleep(5)
                                    if pe_order_details and pe_buy_order_details:
                                        total_ce_count += 1  # Increment the total buy count
                                        total_count = total_ce_count + total_pe_count
                                        print(total_count)
                                        put_sl = pe_sl
                                        put_tgt = pe_tgt
                                        store_high = formatted_store_high
                                        with open('mcn_store_high.txt', 'w') as file:
                                            file.write(str(store_high))
                                        with open('mcn_put_sl.txt', 'w') as file:
                                            file.write(str(put_sl))
                                        with open('mcn_put_tgt.txt', 'w') as file:
                                            file.write(str(put_tgt))
                                        exits_token_loop() 
                                        time.sleep(0.1)
                                        exits_token_loop()
                                        time.sleep(0.1)
                                        exits_token_loop()
                                    else:
                                        retries += 1
                                        break
                        
        previous_ltp = midcap_lp
        time.sleep(0.1)  


def pe_exit_loop():
    global pe_order_details, pe_sl, executed_high_values, pe_tgt, midcap_lp, pe_exit_order_details, pe_buy_order_details, formatted_store_high, pe_buy_exit_order_details

    # Initialize the exit1_order_executed flag outside the loop
    pe_order_executed = False

    while True:
       
        current_time = datetime.datetime.now().time()

        if pe_order_details:
            if pe_buy_order_details:
                try:
                    with open('mcn_put_sl.txt', 'r') as file:
                        put_sl = file.read()
                        put_sl = float(put_sl)
                except FileNotFoundError as e:
                    put_sl = 0
                    print(f"Error reading mcn_put_sl.txt: {e}")
                except ValueError as e:
                    put_sl = 0  # or any default value
                    print(f"Error converting to float: {e}")
                    
                try:
                    with open('mcn_put_tgt.txt', 'r') as file:
                        put_tgt = file.read()
                        put_tgt = float(put_tgt)
                except FileNotFoundError as e:
                    put_tgt = 0
                    print(f"Error reading mcn_put_tgt.txt: {e}")
                except ValueError as e:
                    put_tgt = 0  # or any default value
                    print(f"Error converting to float: {e}")
                
                try:
                    with open('mcn_store_high.txt', 'r') as file:
                        store_high = file.read()
                        store_high = float(store_high)
                except FileNotFoundError as e:
                    store_high = 0
                    print(f"Error reading mcn_store_high.txt: {e}")
                except ValueError as e:
                    store_high = 0  # or any default value
                    print(f"Error converting to float: {e}")

                if midcap_lp and put_sl:
                    if midcap_lp <= put_sl:
                        pe_exit_order()
                        time.sleep(0.1)
                        pe_buy_exit_order()
                        time.sleep(2)
                        if pe_exit_order_details and pe_buy_exit_order_details:
                            pe_order_details.clear()
                            pe_exit_order_details.clear()
                            pe_buy_order_details.clear()
                            pe_buy_exit_order_details.clear()
                            save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                            save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                            save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)
                            save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                            with open('mcn_put_sl.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            with open('mcn_put_tgt.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            time.sleep(2)
                    
                    if midcap_lp and put_tgt:
                       if midcap_lp>= put_tgt:
                        pe_exit_order()
                        time.sleep(0.1)
                        pe_buy_exit_order()
                        time.sleep(2)
                        if pe_exit_order_details and pe_buy_exit_order_details:
                            pe_order_details.clear()
                            pe_exit_order_details.clear()
                            pe_buy_order_details.clear()
                            pe_buy_exit_order_details.clear()
                            save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                            save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                            save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)
                            save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                            executed_high_values.add(store_high) 
                            save_data(EXECUTED_HIGH_VALUES_FILE, executed_high_values)
                            with open('mcn_put_sl.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            with open('mcn_put_tgt.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            time.sleep(2)     

                if midcap_lp:
                    if current_time > datetime.time(15, 20):
                        pe_exit_order()
                        time.sleep(0.1)
                        pe_buy_exit_order()
                        time.sleep(2)
                        if pe_exit_order_details and pe_buy_exit_order_details:
                            pe_order_details.clear()
                            pe_exit_order_details.clear()
                            pe_buy_order_details.clear()
                            pe_buy_exit_order_details.clear()
                            save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                            save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                            save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)
                            save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                            with open('mcn_put_sl.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            with open('mcn_put_tgt.txt', 'w') as file:
                                file.truncate()
                                file.write('0')
                            time.sleep(2)
                          
        time.sleep(0.1)
                

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
        candle_df = get_time_series('NSE', '26074', start_time, end_time, interval=5)

        if candle_df is not None:
            # Process the data (replace this with your implementation)
            print_candle_df(candle_df)
            calculate_rsi(candle_df, n=14)
            calculate_stoch_rsi(stoch_period=14, smoothing_period=7)
            calculate_atr(candle_df)
            atr_df = calculate_atr(candle_df)
            put_entry_conditions(candle_df, atr_df)
            call_entry_conditions(candle_df, atr_df)

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
    fetch_candle_data_thread = threading.Thread(target=fetch_candle_data_loop)
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    amt_loop_thread = threading.Thread(target=atm_loop)
    ce_order_thread = threading.Thread(target=ce_order_place)
    pe_order_thread = threading.Thread(target=pe_order_place)
    ce_exit_thread = threading.Thread(target=ce_exit_loop)
    pe_exit_thread = threading.Thread(target=pe_exit_loop)
    atm_thread = threading.Thread(target=atm_loop)
    
    # Start the threads
    fetch_candle_data_thread.start()
    ltp_data_thread.start()
    amt_loop_thread.start()
    ce_order_thread.start()
    pe_order_thread.start()
    ce_exit_thread.start()
    pe_exit_thread.start()
    atm_thread.start()
  