from NorenRestApiPy.NorenApi import NorenApi
import pickle
import time
import threading

global api

user = open('user.txt', 'r').read()
pwd = open('pass.txt', 'r').read()


def login():
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                              websocket='wss://api.shoonya.com/NorenWSTP/')

    global api  # Make the api variable global
    api = ShoonyaApiPy()
    # Make the API call
    # res = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)
    session_token = open('session_token.txt', 'r').read()
    api.set_session(user, pwd, session_token)
    print('WEBSOCKET LOGIN SUCESSFULL')

    return api

if __name__ == '__main__':
    api = login()
        
    feed_opened = False
    ce_token = 0
    pe_token = 0
    bnf_ltp = 0
    nifty_lp = 0
    finnifty_lp = 0
    midcap_lp = 0
    ce_ltp = 0
    pe_ltp = 0
    ce_exit_token = 0
    pe_exit_token = 0
    exit_lp_ce = 0
    exit_lp_pe = 0


    def token():
        global ce_token, pe_token, ce_exit_token, pe_exit_token
        while True:
            try:
                with open('Ce_ws_token.txt', 'r') as file:
                    ce_token = file.read()
            except FileNotFoundError as e:
                print(f"Error reading ce_ws_token.txt: {e}")
            try:
                with open('Pe_ws_token.txt', 'r') as file:
                    pe_token = file.read()
            except FileNotFoundError as e:
                print(f"Error reading pe_ws_token.txt: {e}")

            try:
                with open('ce_token.txt', 'r') as file:
                    ce_exit_token = file.read()
            except FileNotFoundError as e:
                print(f"Error reading ce_token.txt: {e}")

            try:
                with open('pe_token.txt', 'r') as file:
                    pe_exit_token = file.read()
            except FileNotFoundError as e:
                print(f"Error reading pe_token.txt: {e}")
            
            time.sleep(1)


    stop_event = threading.Event()

    def event_handler_feed_update(tick_data): 
        global bnf_ltp, nifty_lp, finnifty_lp, midcap_lp, exit_lp_ce, ce_token, ce_ltp, pe_token, pe_ltp, ce_exit_token, exit_lp_pe, pe_exit_token

        try:
            token = tick_data['tk']
            lp = tick_data['lp']
        
            
            if token == '26009':
                bnf_ltp = float(lp)
                export_data()
            
            elif token == ce_token:  
                ce_ltp = float(lp)
                export_data()
            
            elif token == pe_token:  
                pe_ltp = float(lp)
                export_data()
            
            elif token == ce_exit_token:  
                exit_lp_ce = float(lp)
                export_data()
            
            elif token == pe_exit_token:  
                exit_lp_pe = float(lp)
                export_data()
      
            elif token == '26000':  
                nifty_lp = float(lp)
                export_data()
            
            elif token == '26037':  
                finnifty_lp = float(lp)
                export_data()
            
            elif token == '26074':  
                midcap_lp = float(lp)
                export_data()
        
        except KeyError:
            pass
    
    def open_callback():
        global feed_opened
        feed_opened = True

    api.start_websocket(subscribe_callback=event_handler_feed_update, socket_open_callback=open_callback)

    while not feed_opened:
        pass
    # NIFTY = 26000, BANKNIFTY = 26009, SENSEX = 1, FINNIFTY = 26037, MIDCAPNIFTY = 26074,

    def sub():
        global ce_token, pe_token, ce_exit_token, pe_exit_token
        
        while True:
            
            nifty = '26000'
            banknify = '26009'
            fin = '26037'
            midcap = '26074'
            ce_tkn = str(ce_token)
            pe_tkn = str(pe_token)
            ce_tkn_exit = str(ce_exit_token)
            pe_tkn_exit = str(pe_exit_token)

            token_nf = 'NSE|' + nifty
            token_fnf = 'NSE|' + fin
            token_bnf = 'NSE|' + banknify
            token_mdc = 'NSE|' + midcap
            token_ce = 'NFO|' + ce_tkn
            token_pe = 'NFO|' + pe_tkn
            token_cee = 'NFO|' + ce_tkn_exit
            token_pee = 'NFO|' + pe_tkn_exit
        
            
            api.subscribe([token_nf, token_bnf, token_ce, token_fnf, token_pe, token_mdc, token_cee, token_pee])

            time.sleep(1)

    def check_lp_values():

        while not stop_event.is_set():
            
            time.sleep(1)
    
    def ltp_check():
        global pe_ltp, ce_ltp, exit_lp_ce, exit_lp_pe
       
        while True:
            ce_ltp = float(ce_ltp)
            ce_trigger = float(ce_ltp) - 10
            formatted_ce_trigger = f'{ce_trigger:.2f}'  # Format to display with 2 decimal places
            with open('formatted_ce_trigger.txt', 'w') as file:
                file.write(formatted_ce_trigger)

            pe_ltp = float(pe_ltp)
            pe_trigger = float(pe_ltp) - 10 
            formatted_pe_trigger = f'{pe_trigger:.2f}'  # Format to display with 2 decimal places
            with open('formatted_pe_trigger.txt', 'w') as file:
                file.write(formatted_pe_trigger)
            
            exit_lp_ce = float(exit_lp_ce)
            ce_exit_trigger = float(exit_lp_ce) - 10
            form_ce_exit_trigger = f'{ce_exit_trigger:.2f}'  # Format to display with 2 decimal places
            with open('form_ce_exit_trigger.txt', 'w') as file:
                file.write(form_ce_exit_trigger)
            
            exit_lp_pe = float(exit_lp_pe)
            pe_exit_trigger = float(exit_lp_pe) - 10 
            form_pe_exit_trigger = f'{pe_exit_trigger:.2f}'  # Format to display with 2 decimal places
            with open('form_pe_exit_trigger.txt', 'w') as file:
                file.write(form_pe_exit_trigger)


            with open('formatted_ce_trigger.txt', 'r') as file:
                ce_limit_price = file.read()
            with open('formatted_pe_trigger.txt', 'r') as file:
                pe_limit_price = file.read()
            with open('form_ce_exit_trigger.txt', 'r') as file:
                pe_exit_limit_price = file.read()
            with open('form_pe_exit_trigger.txt', 'r') as file:
                ce_exit_limit_price = file.read()
    
            time.sleep(1)
    
    def all_prints():
        global exit_lp_pe, exit_lp_ce, bnf_ltp, midcap_lp, nifty_lp, finnifty_lp, pe_ltp, ce_ltp
        while True:
            with open('formatted_ce_trigger.txt', 'r') as file:
                ce_limit_price = file.read()
            with open('formatted_pe_trigger.txt', 'r') as file:
                pe_limit_price = file.read()
            with open('form_ce_exit_trigger.txt', 'r') as file:
                pe_exit_limit_price = file.read()
            with open('form_pe_exit_trigger.txt', 'r') as file:
                ce_exit_limit_price = file.read()
                
            print('NIFTY LTP', nifty_lp)
            print('BANKNIFTY LTP', bnf_ltp)
            print('FINNNIFTY LTP', finnifty_lp)
            print('MIDCAP LTP', midcap_lp)
            #print('CE LIMIT PRICE', ce_limit_price)
            #print('PE LIMIT PRICE', pe_limit_price)
            #print('CE EXIT LIMIT PRICE', ce_exit_limit_price)
            #print('PE EXIT LIMIT PRICE', pe_exit_limit_price)
            #print('............................................')
            
            time.sleep(1)

    if __name__ == "__main__":
        update_thread = threading.Thread(target=check_lp_values)
        update_thread.start()
        ltp_thread = threading.Thread(target=ltp_check)
        ltp_thread.start()
        token_thread = threading.Thread(target=token)
        token_thread.start()
        sub_thread = threading.Thread(target=sub)
        sub_thread.start()
        print_thread = threading.Thread(target=all_prints)
        print_thread.start()


    # Export the values 
    def export_data():
        # Export data for LTP
        with open('data_ltp.pickle', 'wb') as file_ltp:
            data_to_export = {
                'bnf_ltp': bnf_ltp,
                'nifty_lp': nifty_lp,
                'finnifty_lp': finnifty_lp,
                'midcap_lp': midcap_lp,
                'exit_lp_ce': exit_lp_ce,
                }
            pickle.dump(data_to_export, file_ltp)
            

    
    # Call the export_data function to save the data
    export_data()
    
     


      
