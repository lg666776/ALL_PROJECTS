from NorenRestApiPy.NorenApi import NorenApi
import pyotp
import logging
import time
import threading
import pickle


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
        global api
        api = self


# Enable debug to see request and responses
logging.basicConfig(level=logging.DEBUG)

# Start of our program
Qr_code = '4M4I4T6A63G22WRV64W2X546M44OK656'
api = ShoonyaApiPy()
otp = pyotp.TOTP(Qr_code).now()

# Credentials
user = 'FA87766'
pwd = 'Lg666776@500'
factor2 = otp
vc = 'FA87766_U'
app_key = 'ed5b4b44cf139d74b2a5b4ff7480ad48'
imei = 'abc1234'

# Make the API call
ret = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)

# Disable debug logs from the websocket module
logging.getLogger('websocket').setLevel(logging.WARNING)

api.searchscrip('NSE', 'ITC')

feed_opened = False
tata_motors_lp_value = None
tata_motors_quantity = None
tcs_lp_value = None
tcs_quantity = None
sbin_lp_value = None
sbin_quantity = None
infy_lp_value = None
infy_quantity = None
wipro_lp_value = None
wipro_quantity = None
indusindbk_lp_value = None
indusindbk_quantity = None
bajfinance_lp_value = None
bajfinance_quantity = None
itc_lp_value = None
itc_quantity = None
stop_event = threading.Event()


def event_handler_feed_update(tick_data):
    global tata_motors_lp_value, tata_motors_quantity, tcs_lp_value, tcs_quantity, sbin_lp_value, sbin_quantity, infy_lp_value, infy_quantity, wipro_lp_value, wipro_quantity, indusindbk_lp_value, indusindbk_quantity, bajfinance_lp_value, bajfinance_quantity, itc_lp_value, itc_quantity
    try:
        token = tick_data['tk']
        lp = tick_data['lp']

        if token == '3456':
            tata_motors_lp_value = float(lp)
            update_tata_motors_quantity()
            export_data()
        elif token == '31415':
            tcs_lp_value = float(lp)
            update_tcs_quantity()
            export_data()
        elif token == '3045':  # SBIN token
            sbin_lp_value = float(lp)
            update_sbin_quantity()
            export_data()
        elif token == '1594':  # INFY token
            infy_lp_value = float(lp)
            update_infy_quantity()
            export_data()
        elif token == '3787':  # WIPRO token
            wipro_lp_value = float(lp)
            update_wipro_quantity()
            export_data()
        elif token == '5258':  # INDUSINDBK token
            indusindbk_lp_value = float(lp)
            update_indusindbk_quantity()
            export_data()
        elif token == '317':  # BAJFINANCE token
            bajfinance_lp_value = float(lp)
            update_bajfinance_quantity()
            export_data()
        elif token == '1660':  # ITC token
            itc_lp_value = float(lp)
            update_itc_quantity()
            export_data()
    except KeyError:
        pass


def open_callback():
    global feed_opened
    feed_opened = True


api.start_websocket(subscribe_callback=event_handler_feed_update, socket_open_callback=open_callback)

while not feed_opened:
    pass

# Subscribe to all the tokens
api.subscribe(['NSE|3456', 'NSE|11536', 'NSE|3787', 'NSE|3045', 'NSE|1594', 'NSE|5258', 'NSE|317', 'NSE|1660'])

tata_motors_balance = 630
tcs_balance = 3500
sbin_balance = 600
infy_balance = 1450
wipro_balance = 450
indusindbk_balance = 1450
bajfinance_balance = 7500
itc_balance = 500



def update_tata_motors_quantity():
    global tata_motors_lp_value, tata_motors_balance, tata_motors_quantity
    if tata_motors_lp_value is not None:
        tata_motors_quantity = int(tata_motors_balance / tata_motors_lp_value)


def update_tcs_quantity():
    global tcs_lp_value, tcs_balance, tcs_quantity
    if tcs_lp_value is not None:
        tcs_quantity = int(tcs_balance / tcs_lp_value)


def update_sbin_quantity():
    global sbin_lp_value, sbin_balance, sbin_quantity
    if sbin_lp_value is not None:
        sbin_quantity = int(sbin_balance / sbin_lp_value)


def update_infy_quantity():
    global infy_lp_value, infy_balance, infy_quantity
    if infy_lp_value is not None:
        infy_quantity = int(infy_balance / infy_lp_value)


def update_wipro_quantity():
    global wipro_lp_value, wipro_balance, wipro_quantity
    if wipro_lp_value is not None:
        wipro_quantity = int(wipro_balance / wipro_lp_value)


def update_indusindbk_quantity():
    global indusindbk_lp_value, indusindbk_balance, indusindbk_quantity
    if indusindbk_lp_value is not None:
        indusindbk_quantity = int(indusindbk_balance / indusindbk_lp_value)


def update_bajfinance_quantity():
    global bajfinance_lp_value, bajfinance_balance, bajfinance_quantity
    if bajfinance_lp_value is not None:
        bajfinance_quantity = int(bajfinance_balance / bajfinance_lp_value)


def update_itc_quantity():
    global itc_lp_value, itc_balance, itc_quantity
    if itc_lp_value is not None:
        itc_quantity = int(itc_balance / itc_lp_value)


def check_lp_values():
    while not stop_event.is_set():
        time.sleep(1)


update_thread = threading.Thread(target=check_lp_values)
update_thread.start()


# Export the values to TEST02.py and TEST03.py
def export_data():
    data_to_export = {
        'tata_motors_lp_value': tata_motors_lp_value,
        'tata_motors_quantity': tata_motors_quantity,

    }

    with open('data.pickle', 'wb') as file:
        pickle.dump(data_to_export, file)

    # Export data specifically for TEST03.py
    with open('data_test03.pickle', 'wb') as file_test03:
        data_to_export_test03 = {
            'tcs_lp_value': tcs_lp_value,
            'tcs_quantity': tcs_quantity,
        }
        pickle.dump(data_to_export_test03, file_test03)

        # Export data for TEST02.py
    with open('data_test02.pickle', 'wb') as file_test02:
        data_to_export_test02 = {
            'sbin_lp_value': sbin_lp_value,
            'sbin_quantity': sbin_quantity,
        }
        pickle.dump(data_to_export_test02, file_test02)

        # Export data for INFY
    with open('data_infy.pickle', 'wb') as file_infy:
        data_to_export_infy = {
            'infy_lp_value': infy_lp_value,
            'infy_quantity': infy_quantity,
        }
        pickle.dump(data_to_export_infy, file_infy)

        # Export data for WIPRO
        with open('data_wipro.pickle', 'wb') as file_wipro:
            data_to_export_wipro = {
                'wipro_lp_value': wipro_lp_value,
                'wipro_quantity': wipro_quantity,
            }
            pickle.dump(data_to_export_wipro, file_wipro)

        # Export data for INDUSINDBK
        with open('data_indusindbk.pickle', 'wb') as file_indusindbk:
            data_to_export_indusindbk = {
                'indusindbk_lp_value': indusindbk_lp_value,
                'indusindbk_quantity': indusindbk_quantity,
            }
            pickle.dump(data_to_export_indusindbk, file_indusindbk)

        # Export data for BAJFINANCE
        with open('data_bajfinance.pickle', 'wb') as file_bajfinance:
            data_to_export_bajfinance = {
                'bajfinance_lp_value': bajfinance_lp_value,
                'bajfinance_quantity': bajfinance_quantity,
            }
            pickle.dump(data_to_export_bajfinance, file_bajfinance)

        # Export data for ITC
        with open('data_itc.pickle', 'wb') as file_itc:
            data_to_export_itc = {
                'itc_lp_value': itc_lp_value,
                'itc_quantity': itc_quantity,
            }
            pickle.dump(data_to_export_itc, file_itc)

        # Common data export
    with open('data.pickle', 'wb') as file:
        pickle.dump(data_to_export, file)


# Call the export_data function to save the data
export_data()

# TCS = 11536, TATAM = 3456, WIPRO = 3787, SBIN = 3045, INFY = 1594, INDUSINDBK = 5258, BAJFINANCE = 317, ITC = 1660
