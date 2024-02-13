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
    bnf_ltp = 0
    nifty_lp = 0
    finnifty_lp = 0
    midcap_lp = 0
    sensex_lp = 0


    stop_event = threading.Event()

    def event_handler_feed_update(tick_data): 
        global bnf_ltp, nifty_lp, finnifty_lp, midcap_lp, sensex_lp

        try:
            token = tick_data['tk']
            lp = tick_data['lp']
        
            
            if token == '26009':
                bnf_ltp = float(lp)
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
            
            elif token == '1':  
                sensex_lp = float(lp)
                export_data()
        
        except KeyError:
            pass
    
    def open_callback():
        global feed_opened
        feed_opened = True
        
    api.start_websocket(subscribe_callback=event_handler_feed_update, socket_open_callback=open_callback)
    
    while not feed_opened:
        pass
    
    api.subscribe(
        ['NSE|26000', 'NSE|26009', 'NSE|26037', 'NSE|26074', 'BSE|1'])
    
    
    def all_prints():
        global bnf_ltp, midcap_lp, nifty_lp, finnifty_lp, sensex_lp
        while True:        
            print('NIFTY LTP', nifty_lp)
            print('BANKNIFTY LTP', bnf_ltp)
            print('FINNNIFTY LTP', finnifty_lp)
            print('MIDCAP LTP', midcap_lp)
            print('SENSEX LTP', sensex_lp)
            print('............................................')
            
            time.sleep(1)

    if __name__ == "__main__":
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
                'sensex_lp': sensex_lp,
                }
            pickle.dump(data_to_export, file_ltp)
            

    
    # Call the export_data function to save the data
    export_data()
    
     


      
