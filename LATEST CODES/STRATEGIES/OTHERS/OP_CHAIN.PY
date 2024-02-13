from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
from datetime import datetime, timedelta
from datetime import datetime
import pandas as pd
import pickle
import os
import time
import threading
import datetime
import math
import time
import pandas as pd 
import schedule
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
    print('ROLLING LOGIN SUCESSFULL')
    print('LOGIN TIME', current_time)
    return api


if __name__ == '__main__':
    api = login()

    def opt():
        global ce_tsym, pe_tsym

        ret = api.get_quotes(exchange='NSE', token='26000')
        ltp = ret.get("lp")
        ltp = float(ltp)

        strike = int(round(ltp/50,0)*50)

        month = 'DEC'
        atm = strike

        ce_txt = f'NIFTY {month} {atm} CE'
        pe_txt = f'NIFTY {month} {atm} PE'

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

        # Filter and sort PE DataFrame for 'W1' weekly values
        pe_filtered_df = pe_df[pe_df['weekly'] == pe_weekly].sort_values(by='tsym')
        pe_tsym_values = pe_filtered_df['tsym'].tolist()

          # Assuming you want the first value in the list
        if ce_tsym_values:
            ce_specific_tsym = ce_tsym_values[0]
            print(ce_specific_tsym)
        
        if pe_tsym_values:
            pe_specific_tsym = pe_tsym_values[0]
            print(pe_specific_tsym)
        

        opc = api.get_option_chain('NFO', ce_specific_tsym, atm, 20)
        option_chain_data = opc['values']
        option_chain_df = pd.DataFrame(option_chain_data)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)

        pe_opc = api.get_option_chain('NFO', pe_specific_tsym, atm, 20)
        pe_option_chain_data = pe_opc['values']
        pe_option_chain_df = pd.DataFrame(pe_option_chain_data)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)


        ce_df = option_chain_df[option_chain_df['optt'] == 'CE']
        close_ltp = 1
        strikelist = []
        for i in ce_df.index:
            strikeinfo = ce_df.loc[i]
            res = api.get_quotes(exchange='NFO', token=str(strikeinfo.token))
            lp = res.get("lp")
            print(lp)
            strikelist.append(res) 
        
        pe_df = pe_option_chain_df[pe_option_chain_df['optt'] == 'PE']
        pe_close_ltp = 1
        pe_strikelist = []
        for i in pe_df.index:
            pe_strikeinfo = pe_df.loc[i]
            pres = api.get_quotes(exchange='NFO', token=str(pe_strikeinfo.token))
            plp = pres.get("lp")
            print(plp)
            pe_strikelist.append(pres)

        

        strikedf = pd.DataFrame(strikelist)
        strikedf['lp'] = pd.to_numeric(strikedf['lp'], errors='coerce')  # Convert 'lp' column to numeric
        strikedf['diff'] = abs(strikedf['lp'] - close_ltp)
        closest_row = strikedf.loc[strikedf['diff'].idxmin()]
        ce_ltp = closest_row.get('lp')
        print(ce_ltp)
        ce_tsym = closest_row.get('tsym')
        print(ce_tsym)


        pestrikedf = pd.DataFrame(pe_strikelist)
        pestrikedf['lp'] = pd.to_numeric(pestrikedf['lp'], errors='coerce')  # Convert 'lp' column to numeric
        pestrikedf['diff'] = abs(pestrikedf['lp'] - pe_close_ltp)
        pe_closest_row = pestrikedf.loc[pestrikedf['diff'].idxmin()]
        pe_ltp = pe_closest_row.get('lp')
        print(pe_ltp)
        pe_tsym = pe_closest_row.get('tsym')
        print(pe_tsym)


def place():
    global ce_tsym, pe_tsym
    qty = 50
    ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_order')
    orderno = ret['norenordno']
    print(orderno)

    ret = api.place_order(buy_or_sell='B', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_order')
    PE_orderno = ret['norenordno']
    print(PE_orderno)


def exit_place():
    global ce_tsym, pe_tsym
    qty = 50
    ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=ce_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='ce_exit_order')
    orderno = ret['norenordno']
    print(orderno)

    ret = api.place_order(buy_or_sell='S', product_type='I',
                                  exchange='NFO', tradingsymbol=pe_tsym,
                                  quantity=qty, discloseqty=0, price_type='MKT',
                                  retention='DAY', remarks='pe_exit_order')
    PE_orderno = ret['norenordno']
    print(PE_orderno)
     
            
schedule.every().day.at("09:15:10").do(opt)
schedule.every().day.at("09:17:40").do(place)
schedule.every().day.at("15:15:00").do(place)



# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)