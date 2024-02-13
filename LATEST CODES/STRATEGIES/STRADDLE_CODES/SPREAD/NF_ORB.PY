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
high_point = 0
low_point = 0
premimum = 0
ce_tsym = None
pe_tsym = None
nifty_close = 0
total_count = 0
total_buy_count = 0 
total_sell_count = 0
ce_atm_symbol = 0
ce_otm_symbol = 0
pe_atm_symbol = 0
pe_otm_symbol = 0


PE_BUY_ORDER_DETAILS_FILE = 'orb_pe_buy_order_details.pickle'
PE_SELL_ORDER_DETAILS_FILE = 'orb_pe_sell_order_details.pickle'
PE_BUY_EXIT_ORDER_DETAILS_FILE = 'orb_pe_buy_exit_order.pickle'
PE_SELL_EXIT_ORDER_DETAILS_FILE = 'orb_pe_sell_exit_order.pickle'

CE_BUY_ORDER_DETAILS_FILE = 'orb_ce_buy_order_details.pickle'
CE_SELL_ORDER_DETAILS_FILE = 'orb_ce_sell_order_details.pickle'
CE_BUY_EXIT_ORDER_DETAILS_FILE = 'orb_ce_buy_exit_order.pickle'
CE_SELL_EXIT_ORDER_DETAILS_FILE = 'orb_ce_sell_exit_order.pickle'



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

pe_buy_order_details: dict = load_data(PE_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_buy_order_details: dict = load_data(CE_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_buy_exit_order_details: dict = load_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
ce_buy_exit_order_details: dict = load_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)

pe_buy_order_details: dict = load_data(PE_BUY_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_sell_order_details: dict = load_data(PE_SELL_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_buy_exit_order_details: dict = load_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)
pe_sell_exit_order_details: dict = load_data(PE_SELL_EXIT_ORDER_DETAILS_FILE, initialize_empty_dict=True)



def save_data(file_path, data):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)


def all_values():
    global high_point, low_point, premimum
    try:
        with open('nifty_high.txt', 'r') as file:
            high_point = file.read()
            high_point = float(high_point)
    except FileNotFoundError as e:
        print(f"Error reading nifty_high.txt: {e}")
    
    try:
        with open('nifty_low.txt', 'r') as file:
            low_point = file.read()
            low_point = float(low_point)
    except FileNotFoundError as e:
        print(f"Error reading nifty_low.txt: {e}")



def symbol_fetch():
    global ce_tsym, pe_tsym, ce_atm_symbol, ce_otm_symbol, pe_atm_symbol, pe_otm_symbol, qty
   
    ret = api.get_quotes(exchange='NSE', token='26000')
    ltp = ret.get("lp")
    ltp = float(ltp) 

    month = current_month_abbrev 

    qty = 50

    ce_atm = ltp
    pe_atm = ltp

    ce_otm3 = ltp + 50
    pe_otm3 = ltp - 50

    ce_atm_strike = int(round(ce_atm/50,0)*50)
    ce_atm_txt = f'NIFTY {month} {ce_atm_strike} CE'
    
    # Search for CE options
    ce_atm_res = api.searchscrip('NFO', ce_atm_txt)
    ce_atm_df = pd.DataFrame(ce_atm_res['values'])

    # Extract the 'weekly' value from the first row
    ce_atm_tsym = ce_atm_df.loc[0, 'tsym']
    ce_atm_tysm_df = ce_atm_df[ce_atm_df['tsym'] == ce_atm_tsym].sort_values(by='tsym')
    ce_atm_symbol = ce_atm_tysm_df['tsym'].tolist()

    pe_atm_strike = int(round(pe_atm/50,0)*50)
    pe_atm_txt = f'NIFTY {month} {pe_atm_strike} PE'
    
    # Search for CE options
    pe_atm_res = api.searchscrip('NFO', pe_atm_txt)
    pe_atm_df = pd.DataFrame(pe_atm_res['values'])

    # Extract the 'weekly' value from the first row
    pe_atm_tsym = pe_atm_df.loc[0, 'tsym']
    pe_atm_tysm_df = pe_atm_df[pe_atm_df['tsym'] == pe_atm_tsym].sort_values(by='tsym')
    pe_atm_symbol = pe_atm_tysm_df['tsym'].tolist()
    

    ce_otm_strike = int(round(ce_otm3/50,0)*50)
    pe_otm_strike = int(round(pe_otm3/50,0)*50)

    ce_otm_txt = f'NIFTY {month} {ce_otm_strike} CE'
    pe_otm_txt = f'NIFTY {month} {pe_otm_strike} PE'

    # Search for CE options
    ce_otm_res = api.searchscrip('NFO', ce_otm_txt)
    ce_otm_df = pd.DataFrame(ce_otm_res['values'])

    # Search for PE options
    pe_otm_res = api.searchscrip('NFO', pe_otm_txt)
    pe_otm_df = pd.DataFrame(pe_otm_res['values'])
    
    # Extract the 'weekly' value from the first row
    ce_otm_tsym = ce_otm_df.loc[0, 'tsym']
    pe_otm_tsym = pe_otm_df.loc[0, 'tsym']

    # Filter and sort CE DataFrame for the value in first_row_weekly
    ce_otm_tysm_df = ce_otm_df[ce_otm_df['tsym'] == ce_otm_tsym].sort_values(by='tsym')
    ce_otm_symbol = ce_otm_tysm_df['tsym'].tolist()
        
    # Filter and sort PE DataFrame for 'W1' weekly values
    pe_otm_tsym_df = pe_otm_df[pe_otm_df['tsym'] == pe_otm_tsym].sort_values(by='tsym')
    pe_otm_symbol = pe_otm_tsym_df['tsym'].tolist()

    if ce_atm_symbol:
        ce_atm_symbol = ce_atm_symbol[0]
        print(ce_atm_symbol)
        with open('ce_atm.txt', 'w') as file:
            file.write(str(ce_atm_symbol))

    if ce_otm_symbol:
        ce_otm_symbol = ce_otm_symbol[0]
        print(ce_otm_symbol)
        with open('ce_otm.txt', 'w') as file:
            file.write(str(ce_otm_symbol))

    if pe_atm_symbol:
        pe_atm_symbol = pe_atm_symbol[0]
        print(pe_atm_symbol)
        with open('pe_atm.txt', 'w') as file:
            file.write(str(pe_atm_symbol))

    if pe_otm_symbol:
        pe_otm_symbol = pe_otm_symbol[0]
        print(pe_otm_symbol)
        with open('pe_otm.txt', 'w') as file:
            file.write(str(pe_otm_symbol))


def option_chain_calling():
    while True:
        # Calculate the date and time for the next minute
        current_time = datetime.datetime.now()
        next_minute = (current_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)

        # Calculate the seconds remaining until the next minute
        seconds_remaining = (next_minute - current_time).total_seconds()

        # Sleep for 50 seconds (or 0 seconds if less than 1 seconds remaining)
        time.sleep(max(seconds_remaining - 1, 0))  # 1 seconds before the next minute

        # Call the 'ltp' function
        symbol_fetch()
        all_values()
    
        # Wait for the next iteration to start (i.e., wait for the next minute)
        while datetime.datetime.now() < next_minute:
            time.sleep(1)
        

def pe_buy_order():
        global pe_otm_symbol, pe_buy_order_details, qty

        pe_otm = 0

        try:
            with open('pe_otm.txt', 'r') as file:
                pe_otm = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")

        # Assuming you want the first value in the list
        if pe_otm:
            print(pe_otm)

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_otm,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_buy_order')
            orderno = ret['norenordno']


            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    status = order_history[0].get('status')

                    if status == 'COMPLETE':
                        tsym = order_history[0].get('tsym')
                        
                        if orderno not in pe_buy_order_details:
                            pe_buy_order_details[orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'B',
                                'remarks': 'pe_buy_order',
                                'pe_buy_tsym': tsym,
                            }
                            save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)

                            # Exit the loop once ce_order_details is populated
                            break

        # Return the order details dictionary
        return pe_buy_order_details


def pe_sell_order():
        global pe_atm_symbol, pe_sell_order_details, qty

        pe_atm = 0

        try:
            with open('pe_atm.txt', 'r') as file:
                pe_atm = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")

        # Assuming you want the first value in the list
        if pe_atm:

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_atm,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_sell_order')
            orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    status = order_history[0].get('status')

                    if status == 'COMPLETE':
                        tsym = order_history[0].get('tsym')
                        
                        if orderno not in pe_sell_order_details:
                            pe_sell_order_details[orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',
                                'remarks': 'pe_sell_order',
                                'pe_sell_tsym': tsym,
                            }
                            save_data(PE_SELL_ORDER_DETAILS_FILE, pe_sell_order_details)

                            # Exit the loop once ce_order_details is populated
                            break

        # Return the order details dictionary
        return pe_sell_order_details


def pe_buy_exit_order():
    global pe_buy_order_details, pe_buy_exit_order_details, qty
    
    for orderno, order_info in pe_buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_buy_exit_symbol = order_info.get('pe_buy_tsym')
           
             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_buy_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_buy_exit_order')
            
            # Extract the orderno from the ret value
            pe_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=pe_exit_orderno)

                if order_history:
                    status = order_history[0].get('status')
                    
                    if status == 'COMPLETE':
                        if pe_exit_orderno not in pe_buy_exit_order_details:
                            pe_buy_exit_order_details[pe_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',  
                                'remarks': 'pe_buy_exit_order',  
                            }
                            save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                            # Exit the loop once ce_order_details is populated
                            break

    # Return the order details dictionary
    return pe_buy_exit_order_details


def pe_sell_exit_order():
    global pe_sell_order_details, pe_sell_exit_order_details, qty
    
    for orderno, order_info in pe_sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            pe_sell_exit_symbol = order_info.get('pe_sell_tsym')
           
            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_sell_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_sell_exit_order')
            
            # Extract the orderno from the ret value
            ce_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=ce_exit_orderno)

                if order_history:
                    status = order_history[0].get('status')
                    
                    if status == 'COMPLETE':
                        if ce_exit_orderno not in pe_sell_exit_order_details:
                            pe_sell_exit_order_details[ce_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',  
                                'remarks': 'pe_sell_exit_order',  
                            }
                            save_data(PE_SELL_EXIT_ORDER_DETAILS_FILE, pe_sell_exit_order_details)
                            # Exit the loop once ce_order_details is populated
                            break

    # Return the order details dictionary
    return pe_sell_exit_order_details

def ce_buy_order():
        global ce_otm_symbol, ce_buy_order_details, qty

        ce_otm = 0
        try:
            with open('ce_otm.txt', 'r') as file:
                ce_otm = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")

        # Assuming you want the first value in the list
        if ce_otm:
            print(ce_otm)

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_otm,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_buy_order')
            orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    status = order_history[0].get('status')

                    if status == 'COMPLETE':
                        tsym = order_history[0].get('tsym')
                        
                        if orderno not in ce_buy_order_details:
                            ce_buy_order_details[orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'B',
                                'remarks': 'ce_buy_order',
                                'ce_buy_tsym': tsym,
                            }
                            save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)

                            # Exit the loop once ce_order_details is populated
                            break

        # Return the order details dictionary
        return ce_buy_order_details

def ce_sell_order():
        global ce_atm_symbol, ce_sell_order_details, qty
        ce_atm = 0
        try:
            with open('ce_atm.txt', 'r') as file:
                ce_atm = file.read()
        except FileNotFoundError as e:
            print(f"Error reading ce_ws_token.txt: {e}")

        # Assuming you want the first value in the list
        if ce_atm:
            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_atm,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_sell_order')
            orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=orderno)

                if order_history:
                    status = order_history[0].get('status')

                    if status == 'COMPLETE':
                        tsym = order_history[0].get('tsym')
                        
                        if orderno not in ce_sell_order_details:
                            ce_sell_order_details[orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',
                                'remarks': 'ce_sell_order',
                                'ce_sell_tsym': tsym,
                            }
                            save_data(CE_SELL_ORDER_DETAILS_FILE, ce_sell_order_details)

                            # Exit the loop once ce_order_details is populated
                            break

        # Return the order details dictionary
        return ce_sell_order_details


def ce_buy_exit_order():
    global ce_buy_order_details, ce_buy_exit_order_details, qty
    
    for orderno, order_info in ce_buy_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_buy_exit_symbol = order_info.get('ce_buy_tsym')
           
             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_buy_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_buy_exit_order')
            
            # Extract the orderno from the ret value
            pe_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=pe_exit_orderno)

                if order_history:
                    status = order_history[0].get('status')
                    
                    if status == 'COMPLETE':
                        if pe_exit_orderno not in ce_buy_exit_order_details:
                            ce_buy_exit_order_details[pe_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',  
                                'remarks': 'ce_buy_exit_order',  
                            }
                            save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                            # Exit the loop once ce_order_details is populated
                            break

    # Return the order details dictionary
    return ce_buy_exit_order_details


def ce_sell_exit_order():
    global ce_sell_order_details, ce_sell_exit_order_details, qty
    
    for orderno, order_info in ce_sell_order_details.items():
        if isinstance(order_info, dict):  # Check if order_info is a dictionary
            ce_sell_exit_symbol = order_info.get('ce_sell_tsym')
           
             # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_sell_exit_symbol,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_sell_exit_order')
            
            # Extract the orderno from the ret value
            ce_exit_orderno = ret['norenordno']

            while True:
                order_history = api.single_order_history(orderno=ce_exit_orderno)

                if order_history:
                    status = order_history[0].get('status')
                    
                    if status == 'COMPLETE':
                        if ce_exit_orderno not in ce_sell_exit_order_details:
                            ce_sell_exit_order_details[ce_exit_orderno] = {
                                'Status': 'COMPLETE',
                                'trantype': 'S',  
                                'remarks': 'ce_sell_exit_order',  
                            }
                            save_data(CE_SELL_EXIT_ORDER_DETAILS_FILE, ce_sell_exit_order_details)
                            # Exit the loop once ce_order_details is populated
                            break

    # Return the order details dictionary
    return ce_sell_exit_order_details

def buy_order_place():
    global pe_buy_order_details, ce_buy_order_details, ce_sell_order_details, pe_sell_order_details, total_count, total_buy_count, total_sell_count, nifty_close, high_point

    max_retries = 2  # Maximum number of retries for placing the buy order
    trades = 2 #Total trades
    retries = 0  # Counter for retries
   
    while retries < max_retries:
        nifty_close = float(nifty_close)
        high_point = float(high_point)
        if nifty_close and high_point:
            if not pe_buy_order_details and not pe_sell_order_details and not ce_sell_order_details and not ce_buy_order_details:
                current_time = datetime.datetime.now().time()
                start_time = datetime.time(9, 36)
                end_time = datetime.time(15, 00)
                if start_time <= current_time <= end_time:
                    if total_count < trades:
                        if nifty_close > high_point:
                            pe_buy_order_details = pe_buy_order()
                            time.sleep(1)
                            if pe_buy_order_details:
                                pe_sell_order_details = pe_sell_order()
                                if pe_buy_order_details and pe_sell_order_details:
                                    total_buy_count += 1  # Increment the total buy count
                                    total_count = total_buy_count + total_sell_count
                                    print(total_count)
                                    time.sleep(2)  
                                else:
                                    retries += 1
                                    break
        time.sleep(1)  


def buy_exit_loop():
    global pe_buy_order_details, low_point, nifty_close, pe_sell_order_details, pe_buy_exit_order_details, pe_sell_exit_order_details

    # Initialize the exit1_order_executed flag outside the loop
    ce_order_executed = False

    while True:
        if not pe_buy_order_details and not pe_sell_order_details:
            time.sleep(1)  # Add a sleep time of 1 second before the next iteration
            continue

        current_time = datetime.datetime.now().time()
        if pe_buy_order_details:
            if pe_sell_order_details:
                    nifty_close = float(nifty_close)
                    low_point = float(low_point)
                    if nifty_close and low_point:
                        if nifty_close < low_point:
                            pe_sell_exit_order()
                            if pe_sell_exit_order_details:
                                pe_buy_exit_order()
                                time.sleep(1)
                                if pe_sell_exit_order_details and pe_buy_exit_order_details:
                                    pe_buy_order_details.clear()
                                    pe_sell_order_details.clear()
                                    pe_buy_exit_order_details.clear()
                                    pe_sell_exit_order_details.clear()
                                    save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)
                                    save_data(PE_SELL_ORDER_DETAILS_FILE, pe_sell_order_details)
                                    save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                                    save_data(PE_SELL_EXIT_ORDER_DETAILS_FILE, pe_sell_exit_order_details)
                                    time.sleep(2)
                                    ce_order_executed = True
                                    break
                            
                            
                    if current_time > datetime.time(15, 20):
                        pe_sell_exit_order()
                        if pe_sell_exit_order_details:
                            pe_buy_exit_order()
                            time.sleep(1)
                            if pe_sell_exit_order_details and pe_buy_exit_order_details:
                                pe_buy_order_details.clear()
                                pe_sell_order_details.clear()
                                pe_buy_exit_order_details.clear()
                                pe_sell_exit_order_details.clear()
                                save_data(PE_BUY_ORDER_DETAILS_FILE, pe_buy_order_details)
                                save_data(PE_SELL_ORDER_DETAILS_FILE, pe_sell_order_details)
                                save_data(PE_BUY_EXIT_ORDER_DETAILS_FILE, pe_buy_exit_order_details)
                                save_data(PE_SELL_EXIT_ORDER_DETAILS_FILE, pe_sell_exit_order_details)
                                time.sleep(2)
                                ce_order_executed = True
                                break
        time.sleep(1) 


def sell_order_place():
    global pe_buy_order_details, pe_sell_order_details, ce_sell_order_details, ce_buy_order_details, total_count, total_buy_count, total_sell_count, nifty_close, low_point

    max_retries = 2  # Maximum number of retries for placing the buy order
    trades = 2 #Total trades
    retries = 0  # Counter for retries
   
    while retries < max_retries:
        nifty_close = float(nifty_close)
        low_point = float(low_point)
        if nifty_close and low_point:
            if not pe_buy_order_details and not pe_sell_order_details and not ce_sell_order_details and not ce_buy_order_details:
                current_time = datetime.datetime.now().time()
                start_time = datetime.time(9, 36)
                end_time = datetime.time(15, 00)
                if start_time <= current_time <= end_time:
                    if total_count < trades:

                        if nifty_close < low_point:
                            ce_buy_order_details = ce_buy_order()
                            time.sleep(1)
                            if ce_buy_order_details:
                                ce_sell_order_details = ce_sell_order()
                                if ce_buy_order_details and ce_sell_order_details:
                                    total_buy_count += 1  # Increment the total buy count
                                    total_count = total_buy_count + total_sell_count
                                    print(total_count)
                                    time.sleep(2)  
                                else:
                                    retries += 1
                                    break
        time.sleep(1)  


def sell_exit_loop():
    global ce_buy_order_details, high_point, nifty_close, ce_sell_order_details, ce_buy_exit_order_details, ce_sell_exit_order_details

    # Initialize the exit1_order_executed flag outside the loop
    ce_order_executed = False

    while True:
        if not ce_buy_order_details and not ce_sell_order_details:
            time.sleep(1)  # Add a sleep time of 1 second before the next iteration
            continue

        current_time = datetime.datetime.now().time()
        if ce_buy_order_details:
            if ce_sell_order_details:
                    if nifty_close and high_point:
                        nifty_close = float(nifty_close)
                        high_point = float(high_point)
                        if nifty_close > high_point:
                            ce_sell_exit_order()
                            if ce_sell_exit_order_details:
                                ce_buy_exit_order()
                                time.sleep(1)
                                if ce_sell_exit_order_details and ce_buy_exit_order_details:
                                    ce_buy_order_details.clear()
                                    ce_sell_order_details.clear()
                                    ce_buy_exit_order_details.clear()
                                    ce_sell_exit_order_details.clear()
                                    save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)
                                    save_data(CE_SELL_ORDER_DETAILS_FILE, ce_sell_order_details)
                                    save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                                    save_data(CE_SELL_EXIT_ORDER_DETAILS_FILE, ce_sell_exit_order_details)
                                    time.sleep(2)
                                    ce_order_executed = True
                                    break

                    if current_time > datetime.time(15, 20):
                        ce_sell_exit_order()
                        if ce_sell_exit_order_details:
                            ce_buy_exit_order()
                            time.sleep(1)
                            if ce_sell_exit_order_details and ce_buy_exit_order_details:
                                ce_buy_order_details.clear()
                                ce_sell_order_details.clear()
                                ce_buy_exit_order_details.clear()
                                ce_sell_exit_order_details.clear()
                                save_data(CE_BUY_ORDER_DETAILS_FILE, ce_buy_order_details)
                                save_data(CE_SELL_ORDER_DETAILS_FILE, ce_sell_order_details)
                                save_data(CE_BUY_EXIT_ORDER_DETAILS_FILE, ce_buy_exit_order_details)
                                save_data(CE_SELL_EXIT_ORDER_DETAILS_FILE, ce_sell_exit_order_details)
                                time.sleep(2)
                                ce_order_executed = True
                                break
        time.sleep(1) 


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


def print_candle_df(candle_df):
    global nifty_close

    # Extract the 'into' column
    intc_column = candle_df['intc']

    # Check if there are any rows in the DataFrame
    if not intc_column.empty:
        # Extract the latest 'into' value
        nifty_close = intc_column.iloc[-1]
        
        # Print the latest 'into' value
        print("Latest 'intc' value:", nifty_close)
    else:
        print("DataFrame is empty.")


def candle_data_fetch():

    # Calculate the date 5 days ago from the current date
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    five_days = five_days_ago.strftime('%d-%m-%Y')

    # Define the start and end times for the 5-minute candles
    start_time = datetime.datetime.strptime(f'{five_days} 09:15:00', '%d-%m-%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(f'{current_date} 15:30:00', '%d-%m-%Y %H:%M:%S')

    while True:
        # Calculate the date and time for the next minute
        current_time = datetime.datetime.now()
        next_minute = (current_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)

        # Calculate the seconds remaining until the next minute
        seconds_remaining = (next_minute - current_time).total_seconds()

        # Sleep until the next minute
        time.sleep(seconds_remaining)  # Sleep until the next minute + 5 seconds

        # Fetch candle data (replace this with your implementation)
        candle_df = get_time_series('NSE', '26000', start_time, end_time, interval=1)

        if candle_df is not None:
            print_candle_df(candle_df)


if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    option_chain_thread = threading.Thread(target=option_chain_calling)
    candle_data_fetch_thread = threading.Thread(target=candle_data_fetch)
    buy_order_thread = threading.Thread(target=buy_order_place)
    buy_exit_thread = threading.Thread(target=buy_exit_loop)
    sell_order_thread = threading.Thread(target=sell_order_place)
    sell_exit_thread = threading.Thread(target=sell_exit_loop)

    candle_data_fetch_thread.start()
    option_chain_thread.start()
    buy_order_thread.start()
    buy_exit_thread.start()
    sell_order_thread.start()
    sell_exit_thread.start()

