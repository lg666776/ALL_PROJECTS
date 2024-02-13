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

    api = ShoonyaApiPy()
    # Make the API call
    # res = api.login(userid=user, password=pwd, twoFA=otp, vendor_code=vc, api_secret=app_key, imei=imei)
    session_token = open('session_token.txt', 'r').read()
    api.set_session(user, pwd, session_token)
    print('WEBSOCKET LOGIN SUCESSFULL')

    return api


if __name__ == '__main__':
    api = login()

output = api.get_limits()
cash_value = float(output['cash']) - 500  # Convert to a float for calculation
print("Account Balance:", cash_value)

script = api.searchscrip(exchange='NSE', searchtext='TITAN')
print(script)

Total_amount = cash_value * 4.75
print('Total Mergin:', Total_amount)

global available_mergin  # Declare calculation_result as a global variable
available_mergin = cash_value * 4.75 / 20
print("Available Mergin for Each Stocks :", available_mergin)

feed_opened = False
tata_motors_lp_value = None
tata_motors_quantity = None
tcs_lp_value = None
tcs_quantity = None
infy_lp_value = None
infy_quantity = None
sbin_lp_value = None
sbin_quantity = None
tata_steel_lp = None
tata_steel_quantity = None
hindalco_lp_value = None
hindalco_quantity = None
indusindbk_lp_value = None
indusindbk_quantity = None
itc_lp_value = None
itc_quantity = None
axisbk_lp_value = None
axisbk_quantity = None
titan_lp_value = None
titan_quantity = None
mm_eq_lp_value = None
mm_eq_quantity = None
jswsteel_eq_lp_value = None
jswsteel_eq_quantity = None
bajajfinsv_eq_lp_value = None
bajajfinsv_eq_quantity = None
kotakbank_eq_lp_value = None
kotakbank_eq_quantity = None
dlf_lp_value = None
dlf_quantity = None
bajfinance_lp_value = None
bajfinance_quantity = None
wipro_lp_value = None
wipro_quantity = None
icicibank_eq_lp_value = None
icicibank_eq_quantity = None
lt_eq_lp_value = None
lt_eq_quantity = None
techm_eq_lp_value = None
techm_eq_quantity = None


stop_event = threading.Event()


def event_handler_feed_update(tick_data):
    global tata_motors_lp_value, tata_motors_quantity, tcs_lp_value, tcs_quantity, sbin_lp_value, sbin_quantity, tata_steel_lp, tata_steel_quantity, hindalco_lp_value, hindalco_quantity, indusindbk_lp_value, indusindbk_quantity, itc_lp_value, itc_quantity, axisbk_lp_value, axisbk_quantity, titan_quantity, titan_lp_value, mm_eq_lp_value, jswsteel_eq_lp_value, bajajfinsv_eq_lp_value, kotakbank_eq_lp_value, mm_eq_quantity, jswsteel_eq_quantity, bajajfinsv_eq_quantity, kotakbank_eq_quantity, dlf_lp_value, dlf_quantity, infy_lp_value, infy_quantity, bajfinance_lp_value, bajfinance_quantity, wipro_quantity, wipro_lp_value, icicibank_eq_quantity, icicibank_eq_lp_value, lt_eq_lp_value, lt_eq_quantity, techm_eq_lp_value, techm_eq_quantity
    try:
        token = tick_data['tk']
        lp = tick_data['lp']

        if token == '3456':
            tata_motors_lp_value = float(lp)
            update_tata_motors_quantity()
            export_data()
        elif token == '11536':
            tcs_lp_value = float(lp)
            update_tcs_quantity()
            export_data()
        elif token == '3045':  # SBIN token
            sbin_lp_value = float(lp)
            update_sbin_quantity()
            export_data()
        elif token == '3499':  # tata steel token
            tata_steel_lp = float(lp)
            update_tata_steel_quantity()
            export_data()
        elif token == '1363':  # HINDALCO token
            hindalco_lp_value = float(lp)
            update_hindalco_quantity()
            export_data()
        elif token == '5258':  # INDUSINDBK token
            indusindbk_lp_value = float(lp)
            update_indusindbk_quantity()
            export_data()
        elif token == '1660':  # ITC token
            itc_lp_value = float(lp)
            update_itc_quantity()
            export_data()
        elif token == '5900':  # AXISBANK token
            axisbk_lp_value = float(lp)
            update_axisbk_quantity()
            export_data()

        elif token == '3506':  # TITAN token
            titan_lp_value = float(lp)
            update_titan_quantity()
            export_data()
            # Add more token-specific handling for the additional tokens
        elif token == '2031':  # M&M-EQ token
            mm_eq_lp_value = float(lp)
            update_mm_eq_quantity()
            export_data()

        elif token == '11723':  # JSWSTEEL-EQ token
            jswsteel_eq_lp_value = float(lp)
            update_jswsteel_eq_quantity()
            export_data()

        elif token == '16675':  # BAJAJFINSV-EQ token
            bajajfinsv_eq_lp_value = float(lp)
            update_bajajfinsv_eq_quantity()
            export_data()

        elif token == '14732':  # LT-EQ token
            dlf_lp_value = float(lp)
            update_dlf_quantity()
            export_data()

        elif token == '1922':  # KOTAKBANK-EQ token
            kotakbank_eq_lp_value = float(lp)
            update_kotakbank_eq_quantity()
            export_data()
        elif token == '1594':  # INFY token
            infy_lp_value = float(lp)
            update_infy_quantity()
            export_data()
        elif token == '317':  # BAJFINANCE token
            bajfinance_lp_value = float(lp)
            update_bajfinance_quantity()
            export_data()
        elif token == '3787':  # WIPRO token
            wipro_lp_value = float(lp)
            update_wipro_quantity()
            export_data()
        elif token == '4963':  # ICICIBANK-EQ token
            icicibank_eq_lp_value = float(lp)
            update_icicibank_eq_quantity()
            export_data()
        elif token == '11483':  # LT-EQ token
            lt_eq_lp_value = float(lp)
            update_lt_eq_quantity()
            export_data()
        elif token == '13538':  # TECHM-EQ token
            techm_eq_lp_value = float(lp)
            update_techm_eq_quantity()
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
# TATAM = 3456, TCS = 11536, HINDALCO-EQ = 1363, SBIN = 3045, TATASTEEL-EQ = 3499, INDUSINDBK = 5258, ITC = 1660,
# AXISBANK-EQ = 5900, 'TITAN-EQ' = 3506, M&M-EQ = 2031, JSWSTEEL-EQ = 11723,# BAJAJFINSV-EQ = 16675,
# KOTAKBANK-EQ = 1922, DLF-EQ = 14732, INFY = 1594, BAJFINANCE = 317,  WIPRO = 3787, ICICIBANK-EQ = 4963,  LT-EQ = 11483,
#TECHM-EQ = 13538

api.subscribe(
    ['NSE|3456', 'NSE|11536', 'NSE|1363', 'NSE|3045', 'NSE|3499', 'NSE|5258', 'NSE|1660', 'NSE|5900',
     'NSE|3506', 'NSE|2031', 'NSE|11723', 'NSE|16675', 'NSE|1922', 'NSE|14732', 'NSE|1594', 'NSE|317', 'NSE|3787', 'NSE|4963', 'NSE|11483', 'NSE|13538'])

tata_motors_balance = available_mergin
tcs_balance = available_mergin
sbin_balance = available_mergin
tata_steel_balance = available_mergin
indusindbk_balance = available_mergin
itc_balance = available_mergin
hindalco_balance = available_mergin
axisbk_balance = available_mergin
titan_balance = available_mergin
mm_eq_balance = available_mergin
jswsteel_eq_balance = available_mergin
bajajfinsv_eq_balance = available_mergin
kotakbank_eq_balance = available_mergin
dlf_balance = available_mergin
infy_balance = 400
bajfinance_balance = available_mergin
wipro_balance = available_mergin
icicibank_eq_balance = available_mergin
lt_eq_balance = available_mergin
techm_eq_balance = available_mergin


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


def update_tata_steel_quantity():
    global tata_steel_lp, tata_steel_balance, tata_steel_quantity
    if tata_steel_lp is not None:
        tata_steel_quantity = int(tata_steel_balance / tata_steel_lp)


def update_hindalco_quantity():
    global hindalco_lp_value, hindalco_balance, hindalco_quantity
    if hindalco_lp_value is not None:
        hindalco_quantity = int(hindalco_balance / hindalco_lp_value)


def update_indusindbk_quantity():
    global indusindbk_lp_value, indusindbk_balance, indusindbk_quantity
    if indusindbk_lp_value is not None:
        indusindbk_quantity = int(indusindbk_balance / indusindbk_lp_value)


def update_itc_quantity():
    global itc_lp_value, itc_balance, itc_quantity
    if itc_lp_value is not None:
        itc_quantity = int(itc_balance / itc_lp_value)


def update_axisbk_quantity():
    global axisbk_lp_value, axisbk_balance, axisbk_quantity
    if axisbk_lp_value is not None:
        axisbk_quantity = int(axisbk_balance / axisbk_lp_value)


def update_titan_quantity():
    global titan_lp_value, titan_balance, titan_quantity
    if titan_lp_value is not None:
        titan_quantity = int(titan_balance / titan_lp_value)


def update_mm_eq_quantity():
    global mm_eq_lp_value, mm_eq_balance, mm_eq_quantity
    if mm_eq_lp_value is not None:
        mm_eq_quantity = int(mm_eq_balance / mm_eq_lp_value)


def update_jswsteel_eq_quantity():
    global jswsteel_eq_lp_value, jswsteel_eq_balance, jswsteel_eq_quantity
    if jswsteel_eq_lp_value is not None:
        jswsteel_eq_quantity = int(jswsteel_eq_balance / jswsteel_eq_lp_value)


def update_bajajfinsv_eq_quantity():
    global bajajfinsv_eq_lp_value, bajajfinsv_eq_balance, bajajfinsv_eq_quantity
    if bajajfinsv_eq_lp_value is not None:
        bajajfinsv_eq_quantity = int(bajajfinsv_eq_balance / bajajfinsv_eq_lp_value)


def update_dlf_quantity():
    global dlf_lp_value, dlf_balance, dlf_quantity
    if dlf_lp_value is not None:
        dlf_quantity = int(dlf_balance / dlf_lp_value)


def update_kotakbank_eq_quantity():
    global kotakbank_eq_lp_value, kotakbank_eq_balance, kotakbank_eq_quantity
    if kotakbank_eq_lp_value is not None:
        kotakbank_eq_quantity = int(kotakbank_eq_balance / kotakbank_eq_lp_value)


def update_infy_quantity():
    global infy_lp_value, infy_balance, infy_quantity
    if infy_lp_value is not None:
        infy_quantity = int(infy_balance / infy_lp_value)


def update_bajfinance_quantity():
    global bajfinance_lp_value, bajfinance_balance, bajfinance_quantity
    if bajfinance_lp_value is not None:
        bajfinance_quantity = int(bajfinance_balance / bajfinance_lp_value)

def update_wipro_quantity():
    global wipro_lp_value, wipro_balance, wipro_quantity
    if wipro_lp_value is not None:
        wipro_quantity = int(wipro_balance / wipro_lp_value)


def update_icicibank_eq_quantity():
    global icicibank_eq_lp_value, icicibank_eq_balance, icicibank_eq_quantity
    if icicibank_eq_lp_value is not None:
        icicibank_eq_quantity = int(icicibank_eq_balance / icicibank_eq_lp_value)

def update_lt_eq_quantity():
    global lt_eq_lp_value, lt_eq_balance, lt_eq_quantity
    if lt_eq_lp_value is not None:
        lt_eq_quantity = int(lt_eq_balance / lt_eq_lp_value)

def update_techm_eq_quantity():
    global techm_eq_lp_value, techm_eq_balance, techm_eq_quantity
    if techm_eq_lp_value is not None:
        techm_eq_quantity = int(techm_eq_balance / techm_eq_lp_value)


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

        # Export data for tata_steel
    with open('data_tata_steel.pickle', 'wb') as file_tata_steel:
        data_to_export_tata_steel = {
            'tata_steel_lp': tata_steel_lp,
            'tata_steel_quantity': tata_steel_quantity,
        }
        pickle.dump(data_to_export_tata_steel, file_tata_steel)

        # Export data for HINDALCO
        with open('data_hindalco.pickle', 'wb') as file_hindalco:
            data_to_export_hindalco = {
                'hindalco_lp_value': hindalco_lp_value,
                'hindalco_quantity': hindalco_quantity,
            }
            pickle.dump(data_to_export_hindalco, file_hindalco)

        # Export data for INDUSINDBK
        with open('data_indusindbk.pickle', 'wb') as file_indusindbk:
            data_to_export_indusindbk = {
                'indusindbk_lp_value': indusindbk_lp_value,
                'indusindbk_quantity': indusindbk_quantity,
            }
            pickle.dump(data_to_export_indusindbk, file_indusindbk)

        # Export data for ITC
        with open('data_itc.pickle', 'wb') as file_itc:
            data_to_export_itc = {
                'itc_lp_value': itc_lp_value,
                'itc_quantity': itc_quantity,
            }
            pickle.dump(data_to_export_itc, file_itc)

        # Export data for AXISBK
        with open('data_axisbk.pickle', 'wb') as file_axisbk:
            data_to_export_axisbk = {
                'axisbk_lp_value': axisbk_lp_value,
                'axisbk_quantity': axisbk_quantity,
            }
            pickle.dump(data_to_export_axisbk, file_axisbk)

        # Export data for TITAN
        with open('titan.pickle', 'wb') as file_titan:
            data_to_export_titan = {
                'titan_lp_value': titan_lp_value,  # Updated variable name
                'titan_quantity': titan_quantity,  # Updated variable name
            }
            pickle.dump(data_to_export_titan, file_titan)

        # Export data for mm_eq_lp_value
        with open('data_mm_eq.pickle', 'wb') as file_mm_eq:
            data_to_export_mm_eq = {
                'mm_eq_lp_value': mm_eq_lp_value,
                'mm_eq_quantity': mm_eq_quantity,
            }
            pickle.dump(data_to_export_mm_eq, file_mm_eq)

        # Export data for jswsteel_eq_lp_value
        with open('data_jswsteel_eq.pickle', 'wb') as file_jswsteel_eq:
            data_to_export_jswsteel_eq = {
                'jswsteel_eq_lp_value': jswsteel_eq_lp_value,
                'jswsteel_eq_quantity': jswsteel_eq_quantity,
            }
            pickle.dump(data_to_export_jswsteel_eq, file_jswsteel_eq)

        # Export data for bajajfinsv_eq_lp_value
        with open('data_bajajfinsv_eq.pickle', 'wb') as file_bajajfinsv_eq:
            data_to_export_bajajfinsv_eq = {
                'bajajfinsv_eq_lp_value': bajajfinsv_eq_lp_value,
                'bajajfinsv_eq_quantity': bajajfinsv_eq_quantity,
            }
            pickle.dump(data_to_export_bajajfinsv_eq, file_bajajfinsv_eq)

        # Export data for lt_eq_lp_value
        with open('data_dlf.pickle', 'wb') as file_dlf:
            data_to_export_dlf = {
                'dlf_lp_value': dlf_lp_value,
                'dlf_quantity': dlf_quantity,
            }
            pickle.dump(data_to_export_dlf, file_dlf)

        # Export data for kotakbank_eq_lp_value
        with open('data_kotakbank_eq.pickle', 'wb') as file_kotakbank_eq:
            data_to_export_kotakbank_eq = {
                'kotakbank_eq_lp_value': kotakbank_eq_lp_value,
                'kotakbank_eq_quantity': kotakbank_eq_quantity,
            }
            pickle.dump(data_to_export_kotakbank_eq, file_kotakbank_eq)

        # Export data for INFY
        with open('data_infy.pickle', 'wb') as file_infy:
            data_to_export_infy = {
                'infy_lp_value': infy_lp_value,
                'infy_quantity': infy_quantity,
            }
            pickle.dump(data_to_export_infy, file_infy)

        # Export data for BAJFINANCE
        with open('data_bajfinance.pickle', 'wb') as file_bajfinance:
            data_to_export_bajfinance = {
                'bajfinance_lp_value': bajfinance_lp_value,
                'bajfinance_quantity': bajfinance_quantity,
            }
            pickle.dump(data_to_export_bajfinance, file_bajfinance)

        # Export data for WIPRO
        with open('data_wipro.pickle', 'wb') as file_wipro:
            data_to_export_wipro = {
                'wipro_lp_value': wipro_lp_value,
                'wipro_quantity': wipro_quantity,
            }
            pickle.dump(data_to_export_wipro, file_wipro)

        # Export data for icicibank_eq_lp_value
        with open('data_icicibank_eq.pickle', 'wb') as file_icicibank_eq:
            data_to_export_icicibank_eq = {
                'icicibank_eq_lp_value': icicibank_eq_lp_value,
                'icicibank_eq_quantity': icicibank_eq_quantity,
            }
            pickle.dump(data_to_export_icicibank_eq, file_icicibank_eq)

        # Export data for lt_eq_lp_value
        with open('data_lt_eq.pickle', 'wb') as file_lt_eq:
            data_to_export_lt_eq = {
                'lt_eq_lp_value': lt_eq_lp_value,
                'lt_eq_quantity': lt_eq_quantity,
            }
            pickle.dump(data_to_export_lt_eq, file_lt_eq)

        # Export data for techm_eq_lp_value
        with open('data_techm_eq.pickle', 'wb') as file_techm_eq:
            data_to_export_techm_eq = {
                'techm_eq_lp_value': techm_eq_lp_value,
                'techm_eq_quantity': techm_eq_quantity,
            }
            pickle.dump(data_to_export_techm_eq, file_techm_eq)


        # Common data export
    with open('data.pickle', 'wb') as file:
        pickle.dump(data_to_export, file)


# Call the export_data function to save the data
export_data()
