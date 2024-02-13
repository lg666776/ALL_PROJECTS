from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
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
    print('TATA MOTORS LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()

import pandas as pd  # Make sure to import the pandas library if not already done

tata_motors_lp_value = 0
atmstrike = 0


def ltp_quantity_loop():
    global tata_motors_lp_value

    while True:
        try:
            # Read data from data.pickle
            with open('data.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        tata_motors_lp_value = data.get('tata_motors_lp_value')
                        
                        

                except EOFError:
                    tata_motors_lp_value = 0

        except FileNotFoundError:
            tata_motors_lp_value = 0

        except Exception as e:
            tata_motors_lp_value = 0
        time.sleep(0.1)


def ltp_quantity_loop2():
    global tcs_lp_value, tcs_quantity, original_quantity

    while True:
        try:
            # Read data from data_test03.pickle
            with open('data_test03.pickle', 'rb') as file:
                try:
                    data_test03 = pickle.load(file)
                    if isinstance(data_test03, dict):
                        tcs_lp_value = data_test03.get('tcs_lp_value')
                        original_quantity = data_test03.get('tcs_quantity')
                        print(tcs_lp_value)
                        

                except EOFError:
                    # Reset the tcs_lp_value and tcs_quantity to None if EOFError
                    tcs_lp_value = 0

        except FileNotFoundError:

            # Reset the tcs_lp_value and tcs_quantity to None if data not found
            tcs_lp_value = 0

        except Exception as e:

            # Reset the tcs_lp_value and tcs_quantity to None in case of any other exception
            tcs_lp_value = 0
        time.sleep(0.1)

ce_tsym_values = 0
pe_tsym_values = 0


def atm_loop():
    global tata_motors_lp_value, atmstrike, ce_tsym_values, pe_tsym_values

    while True:

        mod = int(tata_motors_lp_value) % 50
        if mod < 25:
            atmstrike = int(math.floor(tata_motors_lp_value / 50)) * 50
        else:
            atmstrike = int(math.ceil(tata_motors_lp_value / 50)) * 50

        month = 'DEC'
        atm = atmstrike

        ce_txt = f'NIFTY {month} {atm} CE'
        pe_txt = f'NIFTY {month} {atm} PE'

        # Search for CE options
        ce_res = api.searchscrip('NFO', ce_txt)
        ce_df = pd.DataFrame(ce_res['values'])

        # Search for PE options
        pe_res = api.searchscrip('NFO', pe_txt)
        pe_df = pd.DataFrame(pe_res['values'])
        
        # Filter and sort CE DataFrame for 'W1' weekly values
        ce_filtered_df = ce_df[ce_df['weekly'] == 'W1'].sort_values(by='tsym')
        ce_tsym_values = ce_filtered_df['tsym'].tolist()
        token_ce = ce_filtered_df['token'].tolist()
       
        # Filter and sort PE DataFrame for 'W1' weekly values
        pe_filtered_df = pe_df[pe_df['weekly'] == 'W1'].sort_values(by='tsym')
        pe_tsym_values = pe_filtered_df['tsym'].tolist()
        token_pe = pe_filtered_df['token'].tolist()

        # Define your values
        ce_token = token_ce
        pe_token = token_pe

        # Assuming you want the first value in the list
        if ce_token:
            ce_specific_tkn = ce_token[0]

        if pe_token:
            pe_specific_tkn = pe_token[0]
           
        

        # Create a dictionary to store these values
        token = {
            'ce_token': ce_specific_tkn,
            'pe_token': pe_specific_tkn,
        }

        # Specify the file path where you want to save the text file
        file_path = 'tokens.txt'
        
        # Open the file in write mode and write the data
        with open(file_path, 'w') as file:
            for key, value in token.items():
                file.write(f"{key}: {value}\n")

        time.sleep(1)


def place_rder():
    global ce_tsym_values, pe_tsym_values

    while True:
        time.sleep(10)
        print(ce_tsym_values)
        print(pe_tsym_values)

        qty = 50

        # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='my_order_001')
        # Assuming you want the first value in the list

        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]

            # Place an order with the specific trading symbol
            ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_specific_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='my_order_001')

        time.sleep(1)


if __name__ == "__main__":
    # Create and start the threads for TCS data and Candle data
    ltp_data_thread = threading.Thread(target=ltp_quantity_loop)
    ltp_data2_thread = threading.Thread(target=ltp_quantity_loop2)
    amt_loop_thread = threading.Thread(target=atm_loop)
    

    # Start the threads
    ltp_data_thread.start()
    amt_loop_thread.start()
    
    ltp_data2_thread.start()
   
