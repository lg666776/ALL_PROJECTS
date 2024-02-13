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
import schedule

global api

# Credentials
user = open('user.txt', 'r').read()
pwd = open('pass.txt', 'r').read()

# Get the current date and time
current_date_time = datetime.datetime.now()
# Extract the month from the current date
current_month_abbrev = current_date_time.strftime("%b").upper()

print("Current Month:", current_month_abbrev)


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
    print('NIFTY LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()
    
qty = 0
max_ce_mtm = 0
max_pe_mtm = 0
sensex_ltp = 0
ce_price = 0
pe_price = 0
atmstrike = 0
final_ce_mtm = 0
final_pe_mtm = 0
total_count = 0
total_ce_count = 0
total_pe_count = 0
ce_tsym_values = 0
pe_tsym_values = 0
ce_exit_trigger = 0
pe_exit_trigger = 0
formatted_final_mtm = 0

CE_ORDER_DETAILS_FILE = 'ss_ce_order_details.pickle'
PE_ORDER_DETAILS_FILE = 'ss_pe_order_details.pickle'
CE_SELL_DICT = 'ss_ce_sell_prc.pickle'
PE_SELL_DICT = 'ss_pe_sell_prc.pickle'
CE_EXIT_ORDER_DETAILS_FILE = 'ss_ce_exit_order.pickle'
PE_EXIT_ORDER_DETAILS_FILE = 'ss_pe_exit_order.pickle'
CE_MTM_DICT = 'ss_ce_mtm.pickle'
PE_MTM_DICT = 'ss_pe_mtm.pickle'


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
    

ce_order_details: dict = load_data(CE_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_order_details: dict = load_data(PE_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_sell_price_file: dict = load_data(CE_SELL_DICT, initialize_empty_dict=True)
pe_sell_price_file: dict = load_data(PE_SELL_DICT, initialize_empty_dict=True)
ce_exit_order_details: dict = load_data(CE_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_exit_order_details: dict = load_data(PE_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_mtm_dictionary_file: dict = load_data(CE_MTM_DICT, initialize_empty_dict=True)
pe_mtm_dictionary_file: dict = load_data(PE_MTM_DICT, initialize_empty_dict=True)


def save_data(file_path, data):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


def ltp_quantity_loop():
    global sensex_ltp

    while True:
        try:
            # Read data from data_bajfinance.pickle
            with open('data_ltp.pickle', 'rb') as file:
                try:
                    data_nf = pickle.load(file)
                    if isinstance(data_nf, dict):
                        sensex_ltp = data_nf.get('sensex_lp')
                       
                except EOFError:
                    sensex_ltp = 0

        except FileNotFoundError:
            sensex_ltp = 0
            

        except Exception as e:
            sensex_ltp = 0

        time.sleep(1)


def atm_loop():
    global sensex_ltp, atmstrike, ce_tsym_values, pe_tsym_values, ce_order_details, pe_order_details, qty, ce_entry_trigger, pe_entry_trigger

    while True:

        strike = int(round(sensex_ltp/100,0)*100)

        month = current_month_abbrev
        atm = strike

        ce_txt = f'SENSEX {month} {atm} CE'
        pe_txt = f'SENSEX {month} {atm} PE'

        ss_ls = 0
        ce_token_values = 0
        pe_token_values = 0
        ce_tsym_values = 0
        pe_tsym_values = 0
        
        try:
            ce_res = api.searchscrip('BFO', ce_txt)
            if 'values' in ce_res:
                ce_df = pd.DataFrame(ce_res['values'])
                ce_tsym = ce_df.loc[0, 'tsym']
                ce_filtered_df = ce_df[ce_df['tsym'] == ce_tsym].sort_values(by='tsym')
                ce_tsym_values = ce_filtered_df['tsym'].tolist()
                ce_token_values = ce_filtered_df['token'].tolist()
                ss_ls = ce_filtered_df['ls'].tolist()
            else:
                raise ValueError("No 'values' key found in CE options result")
        
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
            pe_res = api.searchscrip('BFO', pe_txt)
            
            if 'values' in pe_res:
                pe_df = pd.DataFrame(pe_res['values'])
                pe_tsym = pe_df.loc[0, 'tsym']
                pe_filtered_df = pe_df[pe_df['tsym'] == pe_tsym].sort_values(by='tsym')
                pe_tsym_values = pe_filtered_df['tsym'].tolist()
                pe_token_values = pe_filtered_df['token'].tolist()
            else:
                raise ValueError("No 'values' key found in PE options result")
        
        except ValueError as pe_value_error:
            print(f"ValueError occurred while fetching PE options: {pe_value_error}")
            pe_df = pd.DataFrame()  # Create an empty DataFrame or handle it as per your requirement
        
        except TypeError as pe_type_error:
            print(f"TypeError occurred while fetching PE options: {pe_type_error}")
            pe_df = pd.DataFrame()  
        
        except Exception as pe_general_error:
            print(f"Error occurred while fetching PE options: {pe_general_error}")
            pe_df = pd.DataFrame()  

        if ss_ls:
            lot_size = ss_ls[0]
            qty = float(lot_size) * 1
            qty = int(qty)
            print(qty)
            with open('qty.txt', 'w') as file:
                file.write(str(qty))
           
        # Assuming you want the first value in the list
        if ce_token_values:
            ce_token = ce_token_values[0]
            with open('ce_ws_token.txt', 'w') as file:
                file.write(ce_token)
        
        if pe_token_values:
            pe_token = pe_token_values[0]
            with open('pe_ws_token.txt', 'w') as file:
                file.write(pe_token)
 
        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]

            with open('ce_symbol.txt', 'w') as file:
                    file.write(ce_specific_tsym)
                
            with open('ce_symbol.txt', 'r') as file:
                ce_symbol = file.read()
                print(ce_symbol)
        
        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]

            with open('pe_symbol.txt', 'w') as file:
                    file.write(pe_specific_tsym)
                    
            with open('pe_symbol.txt', 'r') as file:
                pe_symbol = file.read()
                print(pe_symbol)
        
        # Assuming you want the first value in the list
        if ce_token_values:
            ce_token = ce_token_values[0]
            ce_res = api.get_quotes(exchange='BFO', token=str(ce_token))
            ce_lp = ce_res.get("lp")
            ce_lp = float(ce_lp)
            ce_trigger_prc = ce_lp * 0.15
            ce_trigger = ce_lp - ce_trigger_prc
            ce_entry_trigger = f'{round(ce_trigger):.2f}'
            print(ce_entry_trigger)
            with open('ce_ws_token.txt', 'w') as file:
                file.write(ce_token)

        if pe_token_values:
            pe_token = pe_token_values[0]
            pe_res = api.get_quotes(exchange='BFO', token=str(pe_token))
            pe_lp = pe_res.get("lp")
            pe_lp = float(pe_lp)
            pe_trigger_prc = pe_lp * 0.15
            pe_trigger = pe_lp - pe_trigger_prc
            pe_entry_trigger = f'{round(pe_trigger):.2f}'
            print(pe_entry_trigger)
            with open('pe_ws_token.txt', 'w') as file:
                file.write(pe_token)
        
        time.sleep(1)


if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    amt_loop_thread = threading.Thread(target=atm_loop)
   

    
    # Start the threads
    ltp_data_thread.start()
    amt_loop_thread.start()
