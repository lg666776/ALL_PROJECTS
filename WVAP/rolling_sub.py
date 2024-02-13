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

        # Filter and sort CE DataFrame for 'W1' weekly values
        ce_filtered_df = ce_df[ce_df['weekly'] == 'W1'].sort_values(by='tsym')
        ce_tsym_values = ce_filtered_df['tsym'].tolist()

        # Search for PE options
        pe_res = api.searchscrip('NFO', pe_txt)
        pe_df = pd.DataFrame(pe_res['values'])

        # Filter and sort PE DataFrame for 'W1' weekly values
        pe_filtered_df = pe_df[pe_df['weekly'] == 'W1'].sort_values(by='tsym')
        pe_tsym_values = pe_filtered_df['tsym'].tolist()

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
    amt_loop_thread = threading.Thread(target=atm_loop)
    place_rder_thread = threading.Thread(target=place_rder)

    # Start the threads
    ltp_data_thread.start()
    amt_loop_thread.start()
    place_rder_thread.start()





    api.subscribe(
        ['NSE|26000', 'NSE|11536', 'NSE|1363', 'NSE|3045', 'NSE|3499', 'NSE|5258', 'NSE|1660', 'NSE|5900',
         'NSE|3506', 'NSE|2031', 'NSE|11723', 'NSE|16675', 'NSE|1922', 'NSE|14732', 'NSE|1594', 'NSE|317', 'NSE|3787',
         'NSE|4963', 'NSE|11483', 'NSE|13538', 'NSE|16669', 'NSE|2303', 'NSE|7229', 'NSE|11630', 'NSE|17818'])



    dd = '26000'
    aa = '43214'

    dd = '26000'
    token = 'NSE|' + dd

    api.subscribe([token])