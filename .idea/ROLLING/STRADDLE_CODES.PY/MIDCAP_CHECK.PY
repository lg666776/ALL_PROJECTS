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

# Calculate the last Monday of the current month
last_monday = current_date_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=current_date_time.day)
while last_monday.weekday() != 0:  # 0 represents Monday
    last_monday -= datetime.timedelta(days=1)

# Check if today is after the last Monday of the current month
if current_date_time > last_monday:
    # Move to the next month
    current_date_time = current_date_time.replace(day=1) + datetime.timedelta(days=32)

# Extract the month abbreviation from the current date and convert to uppercase
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
    print('MIDCAP LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()
 

qty = 0
ce_avprc = 0
pe_avprc = 0
ce_exit_avprc = 0
pe_exit_avprc = 0
max_ce_mtm = 0
max_pe_mtm = 0
midcap_ltp = 0
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
ce_entry_trigger = 0
pe_entry_trigger = 0
formatted_final_mtm = 0

CE_ORDER_DETAILS_FILE = 'mdcnf_ce_order_details.pickle'
PE_ORDER_DETAILS_FILE = 'mdcnf_pe_order_details.pickle'
CE_SELL_DICT = 'mdcnf_ce_sell_prc.pickle'
PE_SELL_DICT = 'mdcnf_pe_sell_prc.pickle'
CE_EXIT_ORDER_DETAILS_FILE = 'mdcnf_ce_exit_order.pickle'
PE_EXIT_ORDER_DETAILS_FILE = 'mdcnf_pe_exit_order.pickle'
CE_MTM_DICT = 'mdcnf_ce_mtm.pickle'
PE_MTM_DICT = 'mdcnf_pe_mtm.pickle'


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
    global midcap_ltp

    while True:
        try:
            # Read data from data_bajfinance.pickle
            with open('data_ltp.pickle', 'rb') as file:
                try:
                    data_nf = pickle.load(file)
                    if isinstance(data_nf, dict):
                        midcap_ltp = data_nf.get('midcap_lp')
                           
                except EOFError:
                    midcap_ltp = 0

        except FileNotFoundError:
            midcap_ltp = 0
            
        except Exception as e:
            midcap_ltp = 0
            
        time.sleep(0.5)



def atm_loop():
    global midcap_ltp, atmstrike, ce_tsym_values, pe_tsym_values, pe_order_details, qty, ce_trigger, pe_trigger, ce_entry_trigger, pe_entry_trigger

    while True:

        strike = int(round(midcap_ltp/25,0)*25)

        month = 'JAN'
        atm = strike

        ce_txt = f'MIDCPNIFTY {month} {atm} CE'
        pe_txt = f'MIDCPNIFTY {month} {atm} PE'

        # Search for CE options
        ce_res_c = api.searchscrip('NFO', ce_txt)
        ce_df = pd.DataFrame(ce_res_c['values'])

        # Search for PE options
        pe_res_p = api.searchscrip('NFO', pe_txt)
        pe_df = pd.DataFrame(pe_res_p['values'])

        
        # Extract the 'weekly' value from the first row
        ce_tsym = ce_df.loc[0, 'tsym']
        pe_tsym = pe_df.loc[0, 'tsym']

        # Filter and sort CE DataFrame for the value in first_row_weekly
        ce_filtered_df = ce_df[ce_df['tsym'] == ce_tsym].sort_values(by='tsym')
        ce_tsym_values = ce_filtered_df['tsym'].tolist()
        ce_token_values = ce_filtered_df['token'].tolist()
        micscap_ls = ce_filtered_df['ls'].tolist()
       
        # Filter and sort PE DataFrame for 'W1' weekly values
        pe_filtered_df = pe_df[pe_df['tsym'] == pe_tsym].sort_values(by='tsym')
        pe_tsym_values = pe_filtered_df['tsym'].tolist()
        pe_token_values = pe_filtered_df['token'].tolist()
   
        if micscap_ls:
            lot_size = micscap_ls[0]
            qty = float(lot_size) * 1
            qty = int(qty)
            with open('qty.txt', 'w') as file:
                file.write(str(qty))

        # Assuming you want the first value in the list
        if ce_token_values:
            ce_token = ce_token_values[0]
            ce_res = api.get_quotes(exchange='NFO', token=str(ce_token))
            ce_lp = ce_res.get("lp")
            ce_lp = float(ce_lp)
            ce_trigger_prc = ce_lp * 0.15
            ce_trigger = ce_lp - ce_trigger_prc
            ce_entry_trigger = f'{round(ce_trigger):.2f}'
            with open('ce_ws_token.txt', 'w') as file:
                file.write(ce_token)

        if pe_token_values:
            pe_token = pe_token_values[0]
            pe_res = api.get_quotes(exchange='NFO', token=str(pe_token))
            pe_lp = pe_res.get("lp")
            pe_lp = float(pe_lp)
            pe_trigger_prc = pe_lp * 0.15
            pe_trigger = pe_lp - pe_trigger_prc
            pe_entry_trigger = f'{round(pe_trigger):.2f}'
            with open('pe_ws_token.txt', 'w') as file:
                file.write(pe_token)
        
        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]

            with open('ce_symbol.txt', 'w') as file:
                    file.write(ce_specific_tsym)
                
            with open('ce_symbol.txt', 'r') as file:
                ce_symbol = file.read()
        
        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]


            with open('pe_symbol.txt', 'w') as file:
                file.write(pe_specific_tsym)
                    
            with open('pe_symbol.txt', 'r') as file:
                pe_symbol = file.read()

def exits_token_loop():
    global ce_order_details, pe_order_details
    
    
    while True:
        
        for orderno, order_info in ce_order_details.items():
            if isinstance(order_info, dict):  
                ce_token_str = order_info.get('ce_token', 0) 
                
                with open('ce_token.txt', 'w') as file:
                    file.write(ce_token_str)
                    
                with open('ce_token.txt', 'r') as file:
                    ce_token_read = file.read()
            
        for orderno, order_info in pe_order_details.items():
            if isinstance(order_info, dict): 
                pe_token_str = order_info.get('pe_token', 0)  

                with open('pe_token.txt', 'w') as file:
                    file.write(str(pe_token_str))

                with open('pe_token.txt', 'r') as file:
                    pe_token_read = file.read()
            
        time.sleep(1)

def exits_token_loop():
    global ce_order_details, pe_order_details
    
    
    while True:
        
        for orderno, order_info in ce_order_details.items():
            if isinstance(order_info, dict):  
                ce_token_str = order_info.get('ce_token', 0) 
                
                with open('ce_token.txt', 'w') as file:
                    file.write(ce_token_str)
                    
                with open('ce_token.txt', 'r') as file:
                    ce_token_read = file.read()
            
        for orderno, order_info in pe_order_details.items():
            if isinstance(order_info, dict): 
                pe_token_str = order_info.get('pe_token', 0)  

                with open('pe_token.txt', 'w') as file:
                    file.write(str(pe_token_str))

                with open('pe_token.txt', 'r') as file:
                    pe_token_read = file.read()
            
        time.sleep(1)

def exits_trigger_loop(): 
    global ce_exit_trigger, pe_exit_trigger

    ce_token = 0
    pe_token = 0


    while True:
        try:
            with open('ce_token.txt', 'r') as file:
                ce_token = file.read()
        except FileNotFoundError as e:

            print(f"Error reading ce_token.txt: {e}")
    
        try:
            with open('pe_token.txt', 'r') as file:
                pe_token = file.read()
        except FileNotFoundError as e:
            print(f"Error reading pe_token.txt: {e}")
        

         # Check if ce_token has a value
        if ce_token:
            try:
                ce_res = api.get_quotes(exchange='NFO', token=str(ce_token))
                ce_lp = ce_res.get("lp")
                ce_lp = float(ce_lp)
                ce_trigger_prc = ce_lp * 0.15
                ce_trigger = ce_lp + ce_trigger_prc
                ce_exit_trigger = f'{round(ce_trigger):.2f}'
                # Add additional processing or actions here if needed
            except Exception as e:
                print(f"Error processing ce_token: {e}")
        
        else:
            print("No valid ce_token value")
                   
         # Check if pe_token has a value
        if pe_token:
            try:
                pe_res = api.get_quotes(exchange='NFO', token=str(pe_token))
                pe_lp = pe_res.get("lp")
                pe_lp = float(pe_lp)
                pe_trigger_prc = ce_lp * 0.15
                pe_trigger = pe_lp + pe_trigger_prc
                pe_exit_trigger = f'{round(pe_trigger):.2f}'
                # Add additional processing or actions here if needed
            except Exception as e:
                print(f"Error processing pe_token: {e}")
        else:
            print("No valid pe_token value")

        time.sleep(0.5)


def ce_order_execute():
        global ce_tsym_values, pe_tsym_values, ce_order_details, qty, ce_entry_trigger, ce_avprc

        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]
            

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=ce_entry_trigger,
                                  retention='DAY', remarks='ce_order')
            orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    break  # Exit the loop if order_history is not empty
            
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

        # Return the order details dictionary
        return ce_order_details


def ce_exit_order():
    global ce_order_details, ce_exit_order_details, qty, ce_exit_trigger, ce_exit_avprc
    
    for orderno, order_info in ce_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_symbol = order_info.get('ce_tsym')

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=ce_exit_trigger,
                                  retention='DAY', remarks='ce_exit_order')
            
            # Extract the orderno from the ret value
            ce_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=ce_exit_orderno)

                if order_history:
                    break  # Exit the loop if order_history is not empty
    
            status = order_history[0].get('status')

            if status == 'COMPLETE':
                ce_exit_avprc = order_history[0].get('avgprc')

                if ce_exit_orderno not in ce_exit_order_details:
                    ce_exit_order_details[ce_exit_orderno] = {
                        'Status': 'COMPLETE',
                        'trantype': 'B',  # Add custom field trantype with value "B" (Buy)
                        'remarks': 'ce_exit_order',  # Add custom field remarks to identify the buy order
                    }
                    save_data(PE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)

    # Return the order details dictionary
    return ce_exit_order_details



def pe_order_execute():
        global pe_tsym_values, pe_order_details, qty, pe_prc, pe_trigger, pe_entry_trigger, pe_avprc


        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=pe_entry_trigger,
                                  retention='DAY', remarks='pe_order')
            
            orderno = ret['norenordno']
            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    break  # Exit the loop if order_history is not empty
            
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
                            'pe_avprc': pe_avprc,
                            'pe_token': pe_token,
                            'pe_tsym': pe_tsym,
                            
                        }
                        save_data(PE_ORDER_DETAILS_FILE, pe_order_details)

        # Return the order details dictionary
        return pe_order_details


def pe_exit_order():
    global pe_order_details, pe_exit_order_details, qty, pe_exit_trigger, pe_exit_avprc
    
    for orderno, order_info in pe_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_symbol = order_info.get('pe_tsym')

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=pe_exit_trigger,
                                  retention='DAY', remarks='ce_exit_order')

            # Extract the orderno from the ret value
            pe_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=pe_exit_orderno)

                if order_history:
                    break  # Exit the loop if order_history is not empty

            status = order_history[0].get('status')

            if status == 'COMPLETE':
                pe_exit_avprc = order_history[0].get('avgprc')
                if pe_exit_orderno not in pe_exit_order_details:
                    pe_exit_order_details[pe_exit_orderno] = {
                        'Status': 'COMPLETE',
                        'trantype': 'B',  
                        'remarks': 'pe_exit_order',  
                    }
                    # Save the updated exit buy_order_details dictionary to a file after removing the item
                    save_data(CE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)

    # Return the order details dictionary
    return pe_exit_order_details


def ce_order_place():
    global ce_order_details, pe_order_details, total_count, total_ce_count, total_pe_count, formatted_final_mtm

    max_retries = 2  # Maximum number of retries for placing the buy order
    retries = 0  # Counter for retries
    ce_order_limit = False

    while retries < max_retries:
        if not ce_order_details:
            current_time = datetime.datetime.now().time()
            start_time = datetime.time(9, 23)
            end_time = datetime.time(15, 10)
            if start_time <= current_time <= end_time:
                try:
                    with open('formatted_max_exit_limit.txt', 'r') as file:
                        max_exit_limit = file.read()
                        max_exit_limit_ce = float(max_exit_limit)
                except FileNotFoundError:
                    max_exit_limit_ce = 0
                except ValueError as e:
                    max_exit_limit_ce = 0
                if max_exit_limit_ce != 0:
                    if float(formatted_final_mtm) > max_exit_limit_ce:
                        if total_count < 20:
                            ce_order_details = ce_order_execute()
                            print(ce_order_details)
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                                   for
                                   orderno, order_info in ce_order_details.items()):
                                total_ce_count += 1  # Increment the total buy count
                                total_count = total_ce_count + total_pe_count
                                print(total_count)
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(2)  
                            else:
                                retries += 1
                                break
                      
        time.sleep(0.01)  # Adjust the interval as needed

def pe_order_place():
    global pe_order_details, total_count, total_ce_count, total_pe_count

    max_retries = 2  # Maximum number of retries for placing the buy order
    retries = 0  # Counter for retries
    pe_order_limit = False

    while retries < max_retries:
        if not pe_order_details:
            current_time = datetime.datetime.now().time()
            start_time = datetime.time(9, 23)
            end_time = datetime.time(15, 10)
            if start_time <= current_time <= end_time:
                try:
                    with open('formatted_max_exit_limit.txt', 'r') as file:
                        max_exit_limit = file.read()
                        max_exit_limit_pe = float(max_exit_limit)
                except FileNotFoundError:
                    max_exit_limit_pe = 0
                except ValueError as e:
                    max_exit_limit_pe = 0
                if max_exit_limit_pe != 0:
                    if float(formatted_final_mtm) > max_exit_limit_pe:
                        if total_count < 20:
                            pe_order_details = pe_order_execute()
                            print(pe_order_details)
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                                   for
                                   orderno, order_info in pe_order_details.items()):
                                total_pe_count += 1  # Increment the total buy count
                                total_count = total_ce_count + total_pe_count
                                print(total_count)
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(2) 
                            else:
                                retries += 1
                                break
            
        time.sleep(0.01)  # Adjust the interval as needed
    

def ce_sell():
    global ce_price, ce_order_details, ce_sell_price_file
    ce_price = ce_sell_price_file.get('CE_SELL_PRICE', 0)

    for orderno, order_info in ce_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            ce_avgprc_str = order_info.get('ce_avgprc', '0')  # Default to '0' if missing or not a number
            ce_avg_prc = float(ce_avgprc_str)  # Convert to float

            # Create a dictionary to store these values
            ce_sell_avg = {
                'CE_SELL_PRICE': ce_avg_prc,
            }
            # Assign values to the keys in trade_details_file
            ce_sell_price_file.update(ce_sell_avg)
            save_data(CE_SELL_DICT, ce_sell_price_file)
                       
def pe_sell():
    global pe_price, pe_order_details, pe_sell_price_file
    pe_price = pe_sell_price_file.get('PE_SELL_PRICE', 0)

    for orderno, order_info in pe_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            # Get the quantity of the existing buy order
            pe_avgprc_str = order_info.get('pe_avprc', '0')  # Default to '0' if missing or not a number
            pe_avg_prc = float(pe_avgprc_str)  # Convert to float

            # Create a dictionary to store these values
            pe_sell_avg = {
                'PE_SELL_PRICE': pe_avg_prc,
            }
            # Assign values to the keys in trade_details_file
            pe_sell_price_file.update(pe_sell_avg)
            save_data(PE_SELL_DICT, pe_sell_price_file)
    
def ltp():
    global ce_price, pe_price, final_pe_mtm, qty, final_ce_mtm, total_pe_count, total_ce_count, ce_mtm_dictionary_file, formatted_final_mtm, pe_mtm_dictionary_file, max_ce_mtm, max_pe_mtm
    ce_ltp = 0
    pe_ltp = 0
    max_ce_mtm = 0
    max_pe_mtm = 0
    ce_token = 0
    pe_token = 0

    try:
        with open('ce_token.txt', 'r') as file:
            ce_token = file.read()
    except FileNotFoundError as e:
        print(f"Error reading ce_token.txt: {e}")
    
    try:
        with open('pe_token.txt', 'r') as file:
            pe_token = file.read()
    except FileNotFoundError as e:
        print(f"Error reading pe_token.txt: {e}")
    
    # Check if ce_token has a value
    if ce_token:
        try:
            ce_res = api.get_quotes(exchange='NFO', token=str(ce_token))
            ce_lp = ce_res.get("lp")
            ce_ltp = float(ce_lp)
            with open('ce_closing_prc.txt', 'w') as file:
                file.write(ce_ltp)
        # Add additional processing or actions here if needed
        except Exception as e:
            print(f"Error processing ce_token: {e}") 
            ce_ltp = 0
    else:
        print("No valid ce_token value")
    
    # Check if pe_token has a value
    if pe_token:
        try:
            pe_res = api.get_quotes(exchange='NFO', token=str(pe_token))
            pe_lp = pe_res.get("lp")
            pe_ltp = float(pe_lp)
            with open('pe_closing_prc.txt', 'w') as file:
                file.write(pe_ltp)
        # Add additional processing or actions here if needed
        except Exception as e:
            print(f"Error processing pe_token: {e}")
            pe_ltp = 0
    else:
        print("No valid pe_token value")

    # ce_exit_mtm
    if ce_price != 0:
        if ce_ltp != 0:
            ce_mtm = ce_price - ce_ltp
            final_ce_mtm = ce_mtm * qty
            with open('ce_price.txt', 'w') as file:
                file.write(str(final_ce_mtm))
    
    # pe_exit_mtm
    if pe_price != 0:
        if pe_ltp != 0:
            pe_mtm = pe_price - pe_ltp
            final_pe_mtm = pe_mtm * qty
            with open('pe_price.txt', 'w') as file:
                file.write(str(final_pe_mtm))

    if 1 <= total_ce_count <= 10:
        ce_mtm_dictionary = {
            f'FINAL_CE_MTM_{total_ce_count}': final_ce_mtm
              }
        ce_mtm_dictionary_file.update(ce_mtm_dictionary)
        save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
    
    if 1 <= total_pe_count <= 10:
        pe_mtm_dictionary = {
            f'FINAL_PE_MTM_{total_pe_count}': final_pe_mtm
            }
        pe_mtm_dictionary_file.update(pe_mtm_dictionary)
        save_data(PE_MTM_DICT, pe_mtm_dictionary_file)

    # Move the calculation of max_ce_mtm and max_pe_mtm outside the loop
    max_ce_mtm = sum(ce_mtm_dictionary_file.get(f'FINAL_CE_MTM_{i}', 0) for i in range(1, 11))
    max_pe_mtm = sum(pe_mtm_dictionary_file.get(f'FINAL_PE_MTM_{i}', 0) for i in range(1, 11))

    max_mtm = max_ce_mtm + max_pe_mtm
    formatted_final_mtm = f'{max_mtm:.2f}'  # Format to display with 2 decimal places



def mtm_calling_loop():
 
    while True:
        # Calculate the date and time for the next minute
        current_time = datetime.datetime.now()
        next_minute = (current_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)

        # Calculate the seconds remaining until the next minute
        seconds_remaining = (next_minute - current_time).total_seconds()

        # Sleep until the next minute
        time.sleep(seconds_remaining) 
        ltp()

def all_prints():
    global final_ce_mtm, final_pe_mtm, max_ce_mtm, max_pe_mtm, formatted_final_mtm, total_pe_count, total_ce_count, ce_price, pe_price, midcap_ltp, pe_entry_trigger, ce_entry_trigger

    current_mtm = 0
    exit_mtm = 0
   
    while True:

        try:
            with open('ce_closing_prc.txt', 'r') as file:
                ce_closing_price = file.read().strip()
                ce_closing_price = float(ce_closing_price)
        except FileNotFoundError:
            ce_closing_price = 0
        except ValueError as e:
            ce_closing_price = 0
        try:
            with open('pe_closing_prc.txt', 'r') as file:
                pe_closing_price = file.read().strip()
                pe_closing_price = float(pe_closing_price)
        except FileNotFoundError:
            pe_closing_price = 0
        except ValueError as e:
            pe_closing_price = 0 
        
        try:
            with open('formatted_exit_limit.txt', 'r') as file:
                exit_limit = file.read().strip()
                exit_limit_ce = float(exit_limit)
        except FileNotFoundError:
            exit_limit_ce = None
        except ValueError as e:
            exit_limit_ce = None
        
        try:
            with open('formatted_max_exit_limit.txt', 'r') as file:
                max_exit_limit = file.read().strip()
                max_exit_limit_ce = float(max_exit_limit)
        except FileNotFoundError:
            max_exit_limit_ce = None
        except ValueError as e:
            max_exit_limit_ce = None


        print('MIDCAP LTP', midcap_ltp)
        print('ce_entry', ce_entry_trigger)
        print('pe_entry', pe_entry_trigger)
        print('LOSS LIMIT', exit_limit_ce)
        print('MAX LOSS', max_exit_limit_ce)
        print('CE AVPRC', ce_price)
        print('PE AVPRC', pe_price)
        print('CE LTP', ce_closing_price)
        print('PE LTP', pe_closing_price)
        print('CE MTM', final_ce_mtm)
        print('PE MTM', final_pe_mtm)
        print('MAX CE MTM', max_ce_mtm)
        print('MAX PE mtm', max_pe_mtm)
        print('TOTAL MTM', formatted_final_mtm)
        print('TOTAL CE COUNTS', total_ce_count)
        print('TOTAL PE COUNTS', total_pe_count)
        print('..................................')
        print('..................................')

        time.sleep(1)


def ce_exit_loop():
    global ce_order_details, ce_exit_order_details, pe_order_details, pe_exit_order_details

    # Initialize the exit1_order_executed flag outside the loop
    ce_exit_order11 = False

    while True:
        if not ce_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in ce_order_details.items():
            if isinstance(order_info, dict):
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'ce_order':
                    try:
                        with open('formatted_exit_limit.txt', 'r') as file:
                            exit_limit = file.read()
                            exit_limit_ce = float(exit_limit)
                    except FileNotFoundError:
                        exit_limit_ce = 0
                    except ValueError as e:
                        exit_limit_ce = 0  
                    try:
                        with open('ce_price.txt', 'r') as file:
                            ce_mtm = file.read()  
                            ce_mtm = float(ce_mtm)
                    except (ValueError, FileNotFoundError) as e:
                        ce_mtm = 0  
                    
                    if ce_mtm != 0 and exit_limit_ce != 0: 
                        if ce_mtm < exit_limit_ce:
                            ce_exit_order()
                            pe_exit_order()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   ce_exit_orderno, order_info in ce_exit_order_details.items()):
                               
                                ce_order_details.clear()
                                ce_exit_order_details.clear()
                                save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                                save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                                # Open the file in write mode to clear/remove data
                                with open('ce_token.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                with open('ce_closing_prc.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                with open('ce_price.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                pe_order_details.clear()
                                pe_exit_order_details.clear()
                                save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                                save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                                # Open the file in write mode to clear/remove data
                                with open('pe_token.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(0.1)
                                ce_sell()
                                ce_exit_order11 = True
                                time.sleep(2)
                                break  
                   
                    if formatted_final_mtm != 0:
                        try:
                            with open('formatted_max_exit_limit.txt', 'r') as file:
                                max_exit_limit = file.read()
                                max_exit_limit_ce = float(max_exit_limit)
                        except FileNotFoundError:
                            max_exit_limit_ce = 0
                        except ValueError as e:
                            max_exit_limit_ce = 0
                        if max_exit_limit_ce != 0:
                            if float(formatted_final_mtm) < max_exit_limit_ce:
                                ce_exit_order()
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       ce_exit_orderno, order_info in ce_exit_order_details.items()):
                                    ce_order_details.clear()
                                    ce_exit_order_details.clear()
                                    save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                                    save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                                    # Open the file in write mode to clear/remove data
                                    with open('ce_token.txt', 'w') as file:
                                        file.truncate()
                                        file.write('0')
                                    time.sleep(0.1)
                                    ce_sell()
                                    time.sleep(0.1)
                                    ce_sell()
                                    time.sleep(0.1)
                                    ce_sell()
                                    ce_exit_order11 = True
                                    time.sleep(2)
                                    break
        
                    if current_time > datetime.time(15, 14):
                        ce_exit_order()
                        if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   ce_exit_orderno, order_info in ce_exit_order_details.items()):
                                
                                ce_order_details.clear()
                                ce_exit_order_details.clear()
                                save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                                save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                                # Open the file in write mode to clear/remove data
                                with open('ce_token.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(0.1)
                                ce_sell()
                                time.sleep(0.1)
                                ce_sell()
                                ce_exit_order11 = True
                                time.sleep(2)
                                break
        time.sleep(0.5)

def pe_exit_loop():
    global pe_order_details, ce_exit_order_details, pe_exit_order_details, ce_order_details

    # Initialize the exit1_order_executed flag outside the loop
    pe_exit_order11 = False

    while True:
        if not pe_order_details:
            time.sleep(0.5)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in pe_order_details.items():
            if isinstance(order_info, dict):
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'pe_order':
                    try:
                        with open('formatted_exit_limit.txt', 'r') as file:
                            exit_limit = file.read()
                            exit_limit_pe = float(exit_limit)
                    except FileNotFoundError:
                        exit_limit_pe = 0
                    except ValueError as e:
                        exit_limit_pe = 0  
                    try:
                        with open('pe_price.txt', 'r') as file:
                            pe_mtm = file.read()
                            pe_mtm = float(pe_mtm)
                    except (ValueError, FileNotFoundError) as e:
                        pe_mtm = 0
                    if pe_mtm != 0 and exit_limit_pe != 0:
                        if pe_mtm < exit_limit_pe:
                            pe_exit_order()
                            ce_exit_order()
                            if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   pe_exit_orderno, order_info in pe_exit_order_details.items()):
                                pe_order_details.clear()
                                pe_exit_order_details.clear()
                                save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                                save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                                # Open the file in write mode to clear/remove data
                                with open('pe_token.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                with open('pe_closing_prc.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                with open('pe_price.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                ce_order_details.clear()
                                ce_exit_order_details.clear()
                                save_data(CE_ORDER_DETAILS_FILE, ce_order_details)
                                save_data(CE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)
                                # Open the file in write mode to clear/remove data
                                with open('ce_token.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(0.1)
                                pe_sell()
                                pe_exit_order11 = True
                                time.sleep(2)
                                break
                    
                    if formatted_final_mtm != 0:
                        try:
                            with open('formatted_max_exit_limit.txt', 'r') as file:
                                max_exit_limit = file.read()
                                max_exit_limit_pe = float(max_exit_limit)
                        except FileNotFoundError:
                            max_exit_limit_pe = 0
                        except ValueError as e:
                            max_exit_limit_pe = 0
                        if max_exit_limit_pe != 0:
                            if float(formatted_final_mtm) < max_exit_limit_pe:
                                pe_exit_order()
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       pe_exit_orderno, order_info in pe_exit_order_details.items()):
                                    pe_order_details.clear()
                                    pe_exit_order_details.clear()
                                    save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                                    save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                                    # Open the file in write mode to clear/remove data
                                    with open('pe_token.txt', 'w') as file:
                                        file.truncate()
                                        file.write('0')
                                    time.sleep(0.1)
                                    pe_sell()
                                    time.sleep(0.1)
                                    pe_sell()
                                    time.sleep(0.1)
                                    pe_sell()
                                    pe_exit_order11 = True
                                    time.sleep(2)
                                    break      

                    if current_time > datetime.time(15, 14):
                        pe_exit_order()
                        if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                   pe_exit_orderno, order_info in ce_exit_order_details.items()):
                           
                                pe_order_details.clear()
                                pe_exit_order_details.clear()
                                save_data(PE_ORDER_DETAILS_FILE, pe_order_details)
                                save_data(PE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)
                                # Open the file in write mode to clear/remove data
                                with open('pe_token.txt', 'w') as file:
                                    file.truncate()
                                    file.write('0')
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(0.1)
                                pe_sell()
                                time.sleep(0.1)
                                pe_sell()
                                pe_exit_order11 = True
                                time.sleep(2)
                                break
  
        time.sleep(0.5)


def math_calculation():
    ce_token = 0
    pe_token = 0
    ce_lp = 0
    pe_lp = 0
    formatted_exit_limit = 0
    for_max_exit_limit = 0

    try:
        with open('ce_ws_token.txt', 'r') as file:
            ce_token = file.read()
    except FileNotFoundError as e:
        print(f"Error reading ce_ws_token.txt: {e}")
    try:
        with open('pe_ws_token.txt', 'r') as file:
            pe_token = file.read()
    except FileNotFoundError as e:
        print(f"Error reading pe_ws_token.txt: {e}")
    try:
        with open('qty.txt', 'r') as file:
            qty = file.read()
    except FileNotFoundError as e:
        print(f"Error reading ce_ws_token.txt: {e}")

          
    if ce_token:
        try:
            ce_res = api.get_quotes(exchange='NFO', token=str(ce_token))
            ce_lp = ce_res.get("lp")
            ce_lp = float(ce_lp)
        except Exception as e:
            print(f"Error processing ce_token: {e}")
    else:
        print("No valid ce_token value")
                      
    if pe_token:
        try:
            pe_res = api.get_quotes(exchange='NFO', token=str(pe_token))
            pe_lp = pe_res.get("lp")
            pe_lp = float(pe_lp)
        except Exception as e:
            print(f"Error processing pe_token: {e}")
        else:
            print("No valid pe_token value")

    combined_premium_points = ce_lp + pe_lp
    formatted_premium = f'{combined_premium_points:.2f}'  # Format to display with 2 decimal places
        
    # Convert formatted_premium and qty to float before multiplication
    formatted_premium_float = float(formatted_premium)
    qty_float = float(qty)
        
    combined_premium_amount = formatted_premium_float * qty_float

    # Calculate 20% of formatted_amount
    exit_limit = - 0.2 * combined_premium_amount
    formatted_exit_limit = f'{exit_limit:.2f}'

    # Calculate 20% of formatted_amount
    max_exit_lmt = - 0.5 * combined_premium_amount
    for_max_exit_limit = f'{max_exit_lmt:.2f}'

    if float(formatted_exit_limit) > -600.0:
        formatted_exit_limit = '-600.00' 
        with open('formatted_exit_limit.txt', 'w') as file:
            file.write(formatted_exit_limit)
    else:
        formatted_exit_limit = formatted_exit_limit
        with open('formatted_exit_limit.txt', 'w') as file:
            file.write(formatted_exit_limit)

    if float(for_max_exit_limit) > -2000.0:
        for_max_exit_limit = '-2000.00' 
        with open('formatted_max_exit_limit.txt', 'w') as file:
            file.write(for_max_exit_limit)
    else:
        for_max_exit_limit = for_max_exit_limit
        with open('formatted_max_exit_limit.txt', 'w') as file:
            file.write(for_max_exit_limit)

if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    amt_loop_thread = threading.Thread(target=atm_loop)
    ce_order_thread = threading.Thread(target=ce_order_place)
    pe_order_thread = threading.Thread(target=pe_order_place)
    ce_exit_thread = threading.Thread(target=ce_exit_loop)
    pe_exit_thread = threading.Thread(target=pe_exit_loop)
    exit_tkn_thread = threading.Thread(target=exits_token_loop)
    all_prints_thread = threading.Thread(target=all_prints)
    exits_trigger_thread = threading.Thread(target=exits_trigger_loop)
    mtm_calling_thread = threading.Thread(target=mtm_calling_loop)

    
    # Start the threads
    ltp_data_thread.start()
    amt_loop_thread.start()
    ce_order_thread.start()
    pe_order_thread.start()
    ce_exit_thread.start()
    pe_exit_thread.start()
    exit_tkn_thread.start()
    all_prints_thread.start()
    exits_trigger_thread.start()
    mtm_calling_thread.start()


schedule.every().day.at("09:22:55").do(math_calculation)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
