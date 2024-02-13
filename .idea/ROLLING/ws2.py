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
        

        print(f"feed update {tick_data}")

    
    def open_callback():
        global feed_opened
        feed_opened = True

    api.start_websocket(subscribe_callback=event_handler_feed_update, socket_open_callback=open_callback)

    while not feed_opened:
        pass
    # NIFTY = 26000, BANKNIFTY = 26009, SENSEX = 1, FINNIFTY = 26037, MIDCAPNIFTY = 26074,
    api.subscribe(
        ['NSE|26000', 'NSE|26009', 'BFO|854849', 'NSE|26037', 'NSE|26074'])
   

    def check_lp_values():
        global sensex_lp
        while not stop_event.is_set():
          
            time.sleep(0.01)


    update_thread = threading.Thread(target=check_lp_values)
    update_thread.start()


    
     


      
