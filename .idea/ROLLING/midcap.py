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
 
ce_prc = 0
ce_trigger = 0
pe_trigger = 0 
pe_prc = 0
qty = 0
midcap_ltp = 0
ce_price = 0
pe_price = 0
bnf_ce_lp = 0
bnf_pe_lp = 0
atmstrike = 0
final_ce_mtm = 0
final_pe_mtm = 0
total_count = 0
total_ce_count = 0
total_pe_count = 0
ce_tsym_values = 0
pe_tsym_values = 0
formatted_final_mtm = 0
ce_sl_orderno = None
pe_sl_orderno = None

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
            
        time.sleep(0.001)

ce_lp = 0
pe_lp = 0


def atm_loop():
    global midcap_ltp, atmstrike, ce_tsym_values, ce_lp, pe_lp, pe_tsym_values, ce_order_details, pe_order_details, qty, ce_prc, ce_trigger, pe_prc, pe_trigger

    while True:

        strike = int(round(midcap_ltp/25,0)*25)

        month = 'DEC'
        atm = strike

        ce_txt = f'MIDCPNIFTY {month} {atm} CE'
        pe_txt = f'MIDCPNIFTY {month} {atm} PE'

        # Search for CE options
        ce_res = api.searchscrip('NFO', ce_txt)
        ce_df = pd.DataFrame(ce_res['values'])

        # Search for PE options
        pe_res = api.searchscrip('NFO', pe_txt)
        pe_df = pd.DataFrame(pe_res['values'])

        # Extract the 'weekly' value from the first row
        ce_weekly = ce_df.loc[0, 'weekly']
        pe_weekly = pe_df.loc[0, 'weekly']
 
        # Filter and sort CE DataFrame for the value in first_row_weekly
        ce_filtered_df = ce_df[ce_df['weekly'] == ce_weekly].sort_values(by='tsym')
        ce_tsym_values = ce_filtered_df['tsym'].tolist()
        ce_token_values = ce_filtered_df['token'].tolist()
        micscap_ls = ce_filtered_df['ls'].tolist()
        print(ce_tsym_values)
        
        # Assuming you want the first value in the list
        if ce_token_values:
            ce_token = ce_token_values[0]
            with open('ce_ws_token.txt', 'w') as file:
                file.write(ce_token)


        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]

            #print(ce_specific_tsym)
            res = api.get_quotes(exchange='NFO', token=ce_specific_tsym)
            ce_lp = res.get("lp")
            ce_lp = float(ce_lp)
            ce_trigger = float(ce_lp) - 3
            ce_prc = float(ce_lp) + 10
            #print(ce_lp)
            #print(ce_prc)
        
        if micscap_ls:
            lot_size = micscap_ls[0]
            qty = float(lot_size) * 1
            qty = int(qty)
          
        
        # Filter and sort PE DataFrame for 'W1' weekly values
        pe_filtered_df = pe_df[pe_df['weekly'] == pe_weekly].sort_values(by='tsym')
        pe_tsym_values = pe_filtered_df['tsym'].tolist()

        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]
            #print(pe_specific_tsym)
            res = api.get_quotes(exchange='NFO', token=pe_specific_tsym)
            pe_lp = res.get("lp")
            pe_lp = float(pe_lp)
            pe_trigger = float(ce_lp) - 3
            pe_prc = float(pe_lp) + 10
            #print(pe_lp)
            #print(pe_prc)
        
   
       
 
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


        for orderno, order_info in ce_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                ce_token_str = order_info.get('ce_token', 0)  # Default to '0' if missing or not a number
                
                with open('ce_token.txt', 'w') as file:
                    file.write(ce_token_str)
                    
                with open('ce_token.txt', 'r') as file:
                    ce_token_read = file.read()
        
        for orderno, order_info in pe_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                pe_token_str = order_info.get('pe_token', 0)  # Default to '0' if missing or not a number
                
                 # Writing a float as a string to a file
                with open('pe_token.txt', 'w') as file:
                    file.write(str(pe_token_str))

                # Reading the string from the file and converting it back to a float
                with open('pe_token.txt', 'r') as file:
                    pe_token_read = file.read()
    time.sleep(0.01)


def ce_order_execute():
        global ce_tsym_values, pe_tsym_values, ce_order_details, qty, ce_prc, ce_trigger, ce_lp


        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]
            

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=ce_trigger,
                                  retention='DAY', remarks='ce_order')
            orderno = ret['norenordno']
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

        # Return the order details dictionary
        return ce_order_details


def ce_exit_order():
    global ce_order_details, ce_exit_order_details, qty
    
    for orderno, order_info in ce_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_symbol = order_info.get('ce_tsym')
           
             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_symbol,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_exit_order')
            
            # Extract the orderno from the ret value
            ce_exit_orderno = ret['norenordno']

            order_history = api.single_order_history(orderno=ce_exit_orderno)

            if order_history:
                # Check the order status
                status = order_history[0].get('status')

                if status == 'COMPLETE':

                    # Check if the order has not been processed before
                    if ce_exit_orderno not in ce_exit_order_details:
                        # Store the details in the global dictionary
                        ce_exit_order_details[ce_exit_orderno] = {
                            'Status': 'COMPLETE',
                            'trantype': 'B',  # Add custom field trantype with value "B" (Buy)
                            'remarks': 'ce_exit_order',  # Add custom field remarks to identify the buy order
                        }
                        # Save the updated exit buy_order_details dictionary to a file after removing the item
                        save_data(PE_EXIT_ORDER_DETAILS_FILE, ce_exit_order_details)

    # Return the order details dictionary
    return ce_exit_order_details

def ce_sl_order():
    global ce_order_details, ce_exit_order_details, ce_sl_orderno, qty
    for orderno, order_info in ce_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_symbol = order_info.get('ce_tsym')
            ce_price = order_info.get('ce_avgprc', 0)
            sl_price = float(ce_price) + 70
            trigger = sl_price - 5
           

             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_symbol,
                                  quantity=qty, discloseqty=0, price_type='SL-LMT', price=sl_price, trigger_price=trigger,
                                  retention='DAY', remarks='ce_exit_order')
            
            # Extract the orderno from the ret value
            ce_sl_orderno = ret['norenordno']

def ce_cancel_order():
    global ce_sl_orderno

    ret = api.cancel_order(orderno=ce_sl_orderno)



def pe_order_execute():
        global pe_tsym_values, pe_order_details, qty, pe_prc, pe_trigger, pe_lp


        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=pe_trigger,
                                  retention='DAY', remarks='pe_order')
            
            orderno = ret['norenordno']
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
                            'pe_avprc': pe_avprc,
                            'pe_token': pe_token,
                            'pe_tsym': pe_tsym,
                            
                        }
                        save_data(PE_ORDER_DETAILS_FILE, pe_order_details)

        # Return the order details dictionary
        return pe_order_details


def pe_exit_order():
    global pe_order_details, pe_exit_order_details, qty
    
    for orderno, order_info in pe_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_symbol = order_info.get('pe_tsym')
       
             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_symbol,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_exit_order')
            
            # Extract the orderno from the ret value
            pe_exit_orderno = ret['norenordno']

            order_history = api.single_order_history(orderno=pe_exit_orderno)

            if order_history:
                # Check the order status
                status = order_history[0].get('status')

                if status == 'COMPLETE':

                    # Check if the order has not been processed before
                    if pe_exit_orderno not in pe_exit_order_details:
                        # Store the details in the global dictionary
                        pe_exit_order_details[pe_exit_orderno] = {
                            'Status': 'COMPLETE',
                            'trantype': 'B',  # Add custom field trantype with value "B" (Buy)
                            'remarks': 'pe_exit_order',  # Add custom field remarks to identify the buy order
                        }
                        # Save the updated exit buy_order_details dictionary to a file after removing the item
                        save_data(CE_EXIT_ORDER_DETAILS_FILE, pe_exit_order_details)

    # Return the order details dictionary
    return pe_exit_order_details

def pe_sl_order():
    global pe_order_details, pe_exit_order_details, pe_sl_orderno, qty
    for orderno, order_info in pe_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_symbol = order_info.get('pe_tsym')
            pe_price = order_info.get('pe_avgprc', 0)
            sl_price = float(pe_price) + 70
            trigger = sl_price - 1

             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_symbol,
                                  quantity=qty, discloseqty=0, price_type='LMT', price=sl_price,
                                  retention='DAY', remarks='pe_exit_order')
            
            # Extract the orderno from the ret value
            pe_sl_orderno = ret['norenordno']

def pe_cancel_order():
    global pe_sl_orderno

    ret = api.cancel_order(orderno=pe_sl_orderno)

def ce_order_place():
    global ce_order_details, pe_order_details, total_count, total_ce_count, total_pe_count

    max_retries = 2  # Maximum number of retries for placing the buy order
    retries = 0  # Counter for retries
    ce_order_limit = False

    while retries < max_retries:
        if not ce_order_details:
            current_time = datetime.datetime.now().time()
            if current_time > datetime.time(13, 14):
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
        if current_time > datetime.time(13, 14):
            if total_count < 20:
                pe_order_details = pe_order_execute()
                print(pe_order_details)

                while any(isinstance(order_info, dict) and order_info.get('Status') == 'PENDING'
                          for orderno, order_info in pe_order_details.items()):
                    # Retry the order placement
                    pe_order_details = pe_order_execute()

                # The rest of your code
                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                       for orderno, order_info in pe_order_details.items()):
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


    while retries < max_retries:
        if not pe_order_details:
            current_time = datetime.datetime.now().time()
            if current_time > datetime.time(13, 14):
                if total_count < 20:
                    pe_order_details = pe_order_execute()
                    print(pe_order_details)

                      if any(isinstance(order_info, dict) and order_info.get('Status') == 'PENDING'
                           for
                           orderno, order_info in pe_order_details.items()):
                        pe_order_details = pe_order_execute()



                    if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE'
                           for
                           orderno, order_info in pe_order_details.items()):
                        total_ce_count += 1  # Increment the total buy count
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
    

def exit_mtm_loop():
    global ce_price, pe_price, final_ce_mtm, final_pe_mtm, qty, total_ce_count, ce_mtm_dictionary_file, total_pe_count, pe_mtm_dictionary_file

    while True:

        try:
            with open('ce_closing_prc.txt', 'r') as file:
                ce_closing_price = file.read()
                # Convert ce_closing_price to a numeric type (float in this case)
                ce_closing_price = float(ce_closing_price)

        except FileNotFoundError:
            ce_closing_price = 0
     
        try:
            with open('pe_closing_prc.txt', 'r') as file:
                pe_closing_price = file.read()
                # Convert ce_closing_price to a numeric type (float in this case)
                pe_closing_price = float(pe_closing_price)
                

        except FileNotFoundError:
            pe_closing_price = 0
        
        # ce_exit_mtm
        if ce_price != 0:
            if ce_closing_price != 0:
                ce_mtm = ce_price - ce_closing_price
                final_ce_mtm = ce_mtm * qty
                print('CE MTM', final_ce_mtm)
                with open('ce_price.txt', 'w') as file:
                    file.write(str(final_ce_mtm))
        
        if total_ce_count == 1:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_1': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 2:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_2': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 3:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_3': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 4:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_4': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 5:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_5': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 6:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_6': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 7:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_7': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 8:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_8': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 9:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_9': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)
        
        if total_ce_count == 10:
            ce_mtm_dictionary = {
                'FINAL_CE_MTM_10': final_ce_mtm
                }
            ce_mtm_dictionary_file.update(ce_mtm_dictionary)
            save_data(CE_MTM_DICT, ce_mtm_dictionary_file)

        # pe_exit_mtm
        if pe_price != 0:
            if pe_closing_price != 0:
                pe_mtm = pe_price - pe_closing_price
                final_pe_mtm = pe_mtm * qty
                print('PE MTM', final_pe_mtm)
                with open('pe_price.txt', 'w') as file:
                    file.write(str(final_pe_mtm))
        
        if total_pe_count == 1:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_1': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 2:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_2': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 3:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_3': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 4:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_4': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)

        if total_pe_count == 5:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_5': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 6:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_6': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 7:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_7': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 8:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_8': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 9:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_9': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        if total_pe_count == 10:
            pe_mtm_dictionary = {
                'FINAL_PE_MTM_10': final_pe_mtm
                }
            pe_mtm_dictionary_file.update(pe_mtm_dictionary)
            save_data(PE_MTM_DICT, pe_mtm_dictionary_file)
        
        ce_mtm_1 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_1', 0)
        ce_mtm_2 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_2', 0)
        ce_mtm_3 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_3', 0)
        ce_mtm_4 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_4', 0)
        ce_mtm_5 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_5', 0)
        ce_mtm_6 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_6', 0)
        ce_mtm_7 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_7', 0)
        ce_mtm_8 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_8', 0)
        ce_mtm_9 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_9', 0)
        ce_mtm_10 = ce_mtm_dictionary_file.get('FINAL_CE_MTM_10', 0)

        pe_mtm_1 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_1', 0)
        pe_mtm_2 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_2', 0)
        pe_mtm_3 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_3', 0)
        pe_mtm_4 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_4', 0)
        pe_mtm_5 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_5', 0)
        pe_mtm_6 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_6', 0)
        pe_mtm_7 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_7', 0)
        pe_mtm_8 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_8', 0)
        pe_mtm_9 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_9', 0)
        pe_mtm_10 = pe_mtm_dictionary_file.get('FINAL_PE_MTM_10', 0)

        max_ce_mtm = ce_mtm_1 + ce_mtm_2 + ce_mtm_3 + ce_mtm_4 + ce_mtm_5 + ce_mtm_6 + ce_mtm_7 + ce_mtm_8 + ce_mtm_9 + ce_mtm_10
        max_pe_mtm = pe_mtm_1 + pe_mtm_2 + pe_mtm_3 + pe_mtm_4 + pe_mtm_5 + pe_mtm_6 + pe_mtm_7 + pe_mtm_8 + pe_mtm_9 + pe_mtm_10

        print('max ce mtm', max_ce_mtm)
        print('max pe mtm', max_pe_mtm)

        max_mtm = max_ce_mtm + max_pe_mtm
        formatted_final_mtm = f'{max_mtm:.2f}'  # Format to display with 2 decimal places
        print('TOTAL MTM', formatted_final_mtm)









        time.sleep(1)

def final_mtm_loop():
    global final_ce_mtm, final_pe_mtm, total_pe_count, total_ce_count, ce_mtm_dictionary_file, formatted_final_mtm, pe_mtm_dictionary_file

    max_ce_mtm = 0
    max_pe_mtm = 0

    while True:
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

        print('max ce mtm', max_ce_mtm)
        print('max pe mtm', max_pe_mtm)

        max_mtm = max_ce_mtm + max_pe_mtm
        formatted_final_mtm = f'{max_mtm:.2f}'  # Format to display with 2 decimal places
        print('TOTAL MTM', formatted_final_mtm)
     

        time.sleep(1)


def ce_exit_loop():
    global ce_order_details, ce_exit_order_details, pe_order_details, pe_exit_order_details

    # Initialize the exit1_order_executed flag outside the loop
    ce_exit_order11 = False

    ce_loss = 600
    max_loss = 1500

    while True:
        if not ce_order_details:
            time.sleep(0.01)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in ce_order_details.items():
            if isinstance(order_info, dict):
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'ce_order':
                    try:
                        with open('ce_price.txt', 'r') as file:
                            ce_mtm = file.read()  
                            if ce_mtm != '0':  
                                ce_mtm = float(ce_mtm)  
                                if ce_mtm > ce_loss:
                                    ce_exit_order()
                                    pe_exit_order()
                    except (ValueError, FileNotFoundError) as e:
                        print(f"Error reading 'ce_price.txt': {e}")
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
                                break
                    
                    if formatted_final_mtm != 0:
                        max_loss = float(max_loss)
                        if float(formatted_final_mtm) > max_loss:
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
                                break
        time.sleep(1)

def pe_exit_loop():
    global pe_order_details, ce_exit_order_details, pe_exit_order_details, ce_order_details

    # Initialize the exit1_order_executed flag outside the loop
    pe_exit_order11 = False

    pe_loss = 600
    max_loss = 1500

    while True:
        if not pe_order_details:
            time.sleep(0.01)  # Add a sleep time of 1 second before the next iteration
            continue

        # Get the current time
        current_time = datetime.datetime.now().time()

        for orderno, order_info in pe_order_details.items():
            if isinstance(order_info, dict):
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'S' and order_info.get(
                        'remarks') == 'pe_order':
                    try:
                        with open('pe_price.txt', 'r') as file:
                            pe_mtm = file.read()
                            pe_mtm = float(pe_mtm)
                            if pe_mtm != '0':  # Check if ce_mtm is not empty and not equal to '0'
                                if pe_mtm > pe_loss:
                                    pe_exit_order()
                                    ce_exit_order()
                    except (ValueError, FileNotFoundError) as e:
                        print(f"Error reading 'pe_price.txt': {e}")
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
                                break
                    
                    if formatted_final_mtm != 0:
                        max_loss = float(max_loss)
                        if float(formatted_final_mtm) > max_loss:
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
                                break
  
        time.sleep(1)

if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    amt_loop_thread = threading.Thread(target=atm_loop)
    ce_order_thread = threading.Thread(target=ce_order_place)
    pe_order_thread = threading.Thread(target=pe_order_place)
    exit_mtm_thread = threading.Thread(target=exit_mtm_loop)
    final_mtm_thread = threading.Thread(target=final_mtm_loop)
    ce_exit_thread = threading.Thread(target=ce_exit_loop)
    pe_exit_thread = threading.Thread(target=pe_exit_loop)
    
    # Start the threads
    ltp_data_thread.start()
    amt_loop_thread.start()
    ce_order_thread.start()
    pe_order_thread.start()
    exit_mtm_thread.start()
    final_mtm_thread.start()
    ce_exit_thread.start()
    pe_exit_thread.start()