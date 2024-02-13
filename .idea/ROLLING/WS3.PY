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
    exit_lp = 0
    exit_lp_pe = 0
   
           


    def token():
        global ce_token, pe_token, ce_exit_token, pe_exit_token
        while True:
            with open('ce_ws_token.txt', 'r') as file:
                ce_token = file.read()
    
            with open('pe_ws_token.txt', 'r') as file:
                pe_token = file.read()
            
            with open('ce_token.txt', 'r') as file:
                ce_exit_token = file.read()
                
            with open('ce_token.txt', 'r') as file:
                pe_exit_token = file.read()
                
            
            time.sleep(0.001)

    stop_event = threading.Event()

    def event_handler_feed_update(tick_data): 
        global bnf_ltp, nifty_lp, finnifty_lp, midcap_lp, exit_lp, ce_token, ce_ltp, pe_token, pe_ltp, ce_exit_token, exit_lp_pe, pe_exit_token

        try:
            token = tick_data['tk']
            lp = tick_data['lp']
            
            if token == '26009':
                bnf_ltp = float(lp)
                export_data()
            
            elif token == ce_exit_token:  
                exit_lp = float(lp)
                export_data()
            
            elif token == pe_exit_token:  
                exit_lp_pe = float(lp)
                export_data()
            
            elif token == ce_token:  
                ce_ltp = float(lp)
                export_data()
            
            elif token == pe_token:  
                pe_ltp = float(lp)
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
           
            banknify = '26074'
            ce_tkn = str(ce_token)
            pe_tkn = str(pe_token)
            ce_tkn_exit = str(ce_exit_token)
            pe_tkn_exit = str(pe_exit_token)

          
            
            token_bnf = 'NSE|' + banknify
            token_ce = 'NFO|' + ce_tkn
            token_pe = 'NFO|' + pe_tkn
            token_cee = 'NFO|' + ce_tkn_exit
            token_pee = 'NFO|' + pe_tkn_exit
        
            
            api.subscribe([token_bnf, token_ce, token_pe, token_cee, token_pee])

            time.sleep(1)

    def check_lp_values():
        global exit_lp_pe

        
        while not stop_event.is_set():
            print(exit_lp_pe)
          
            time.sleep(1)
    
    def ltp_check():
        global finnifty_lp, midcap_lp, pe_ltp, ce_ltp, pe_token
       
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

            with open('formatted_ce_trigger.txt', 'r') as file:
                ce_limit_price = file.read()
            
            with open('formatted_pe_trigger.txt', 'r') as file:
                pe_limit_price = file.read()
            
    
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


    # Export the values 
    def export_data():
        # Export data for LTP
        with open('data_ltp.pickle', 'wb') as file_ltp:
            data_to_export = {
                'bnf_ltp': bnf_ltp,
                'nifty_lp': nifty_lp,
                'finnifty_lp': finnifty_lp,
                'midcap_lp': midcap_lp,
                'exit_lp': exit_lp,
                }
            pickle.dump(data_to_export, file_ltp)
            

    
    # Call the export_data function to save the data
    export_data()
    
     