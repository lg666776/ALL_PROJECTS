import pickle
import time

def axisbk_ltp_quantity_loop():
    global axisbk_lp_value, axisbk_quantity

    while True:
        try:
            # Read data from data_axisbk.pickle
            with open('data_axisbk.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        axisbk_lp_value = data.get('axisbk_lp_value')
                        axisbk_quantity = data.get('axisbk_quantity')

                except EOFError:
                    axisbk_lp_value = 0

        except FileNotFoundError:
            axisbk_lp_value = 0

        except Exception as e:
            axisbk_lp_value = 0

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for Axis Bank data
axisbk_ltp_quantity_loop()

def hcltech_ltp_quantity_loop():
    global hcltech_lp_value, hcltech_quantity

    while True:
        try:
            # Read data from data_hcltech.pickle
            with open('data_hcltech.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        hcltech_lp_value = data.get('hcltech_lp_value')
                        hcltech_quantity = data.get('hcltech_quantity')

                except EOFError:
                    hcltech_lp_value = 0

        except FileNotFoundError:
            hcltech_lp_value = 0

        except Exception as e:
            hcltech_lp_value = 0

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for HCLTECH data
hcltech_ltp_quantity_loop()

def mm_eq_ltp_quantity_loop():
    global mm_eq_lp_value, mm_eq_quantity

    while True:
        try:
            # Read data from data_mm_eq.pickle
            with open('data_mm_eq.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        mm_eq_lp_value = data.get('mm_eq_lp_value')
                        mm_eq_quantity = data.get('mm_eq_quantity')

                except EOFError:
                    mm_eq_lp_value = 0

        except FileNotFoundError:
            mm_eq_lp_value = 0

        except Exception as e:
            mm_eq_lp_value = 0

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for mm_eq_lp_value data
mm_eq_ltp_quantity_loop()


def jswsteel_eq_ltp_quantity_loop():
    global jswsteel_eq_lp_value, jswsteel_eq_quantity

    while True:
        try:
            # Read data from data_jswsteel_eq.pickle
            with open('data_jswsteel_eq.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        jswsteel_eq_lp_value = data.get('jswsteel_eq_lp_value')
                        jswsteel_eq_quantity = data.get('jswsteel_eq_quantity')

                except EOFError:
                    jswsteel_eq_lp_value = 0

        except FileNotFoundError:
            jswsteel_eq_lp_value = 0

        except Exception as e:
            jswsteel_eq_lp_value = 0

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for jswsteel_eq_lp_value data
jswsteel_eq_ltp_quantity_loop()

def techm_eq_ltp_quantity_loop():
    global techm_eq_lp_value, techm_eq_quantity

    while True:
        try:
            # Read data from data_techm_eq.pickle
            with open('data_techm_eq.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        techm_eq_lp_value = data.get('techm_eq_lp_value')
                        techm_eq_quantity = data.get('techm_eq_quantity')

                except EOFError:
                    techm_eq_lp_value = 0

        except FileNotFoundError:
            techm_eq_lp_value = 0

        except Exception as e:
            techm_eq_lp_value = 0

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for techm_eq_lp_value data
techm_eq_ltp_quantity_loop()

def bajajfinsv_eq_ltp_quantity_loop():
    global bajajfinsv_eq_lp_value, bajajfinsv_eq_quantity

    while True:
        try:
            # Read data from data_bajajfinsv_eq.pickle
            with open('data_bajajfinsv_eq.pickle', 'rb') as file:
                try:
                    data = pickle.load(file)
                    if isinstance(data, dict):
                        bajajfinsv_eq_lp_value = data.get('bajajfinsv_eq_lp_value')
                        bajajfinsv_eq_quantity = data.get('bajajfinsv_eq_quantity')

                except EOFError:
                    bajajfinsv_eq_lp_value = 0

        except FileNotFoundError:
            bajajfinsv_eq_lp_value = 0

        except Exception as e:
            bajajfinsv_eq_lp_value = 0

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for bajajfinsv_eq_lp_value data
bajajfinsv_eq_ltp_quantity_loop()

def bajaj_auto_eq_ltp_quantity_loop():
    global bajaj_auto_eq_lp_value, bajaj_auto_eq_quantity

    while True:
        try:
            # Create a dictionary with the data to export
            data_to_export_bajaj_auto_eq = {
                'bajaj_auto_eq_lp_value': bajaj_auto_eq_lp_value,
                'bajaj_auto_eq_quantity': bajaj_auto_eq_quantity,
            }

            # Export data for bajaj_auto_eq_lp_value
            with open('data_bajaj_auto_eq.pickle', 'wb') as file_bajaj_auto_eq:
                pickle.dump(data_to_export_bajaj_auto_eq, file_bajaj_auto_eq)

        except Exception as e:
            # Handle exceptions here if needed
            pass

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for exporting bajaj_auto_eq data
bajaj_auto_eq_ltp_quantity_loop()

def icicibank_eq_ltp_quantity_loop():
    global icicibank_eq_lp_value, icicibank_eq_quantity

    while True:
        try:
            # Create a dictionary with the data to export
            data_to_export_icicibank_eq = {
                'icicibank_eq_lp_value': icicibank_eq_lp_value,
                'icicibank_eq_quantity': icicibank_eq_quantity,
            }

            # Export data for icicibank_eq_lp_value
            with open('data_icicibank_eq.pickle', 'wb') as file_icicibank_eq:
                pickle.dump(data_to_export_icicibank_eq, file_icicibank_eq)

        except Exception as e:
            # Handle exceptions here if needed
            pass

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for exporting icicibank_eq data
icicibank_eq_ltp_quantity_loop()

def hindunilvr_eq_ltp_quantity_loop():
    global hindunilvr_eq_lp_value, hindunilvr_eq_quantity

    while True:
        try:
            # Create a dictionary with the data to export
            data_to_export_hindunilvr_eq = {
                'hindunilvr_eq_lp_value': hindunilvr_eq_lp_value,
                'hindunilvr_eq_quantity': hindunilvr_eq_quantity,
            }

            # Export data for hindunilvr_eq_lp_value
            with open('data_hindunilvr_eq.pickle', 'wb') as file_hindunilvr_eq:
                pickle.dump(data_to_export_hindunilvr_eq, file_hindunilvr_eq)

        except Exception as e:
            # Handle exceptions here if needed
            pass

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for exporting hindunilvr_eq data
hindunilvr_eq_ltp_quantity_loop()

def lt_eq_ltp_quantity_loop():
    global lt_eq_lp_value, lt_eq_quantity

    while True:
        try:
            # Create a dictionary with the data to export
            data_to_export_lt_eq = {
                'lt_eq_lp_value': lt_eq_lp_value,
                'lt_eq_quantity': lt_eq_quantity,
            }

            # Export data for lt_eq_lp_value
            with open('data_lt_eq.pickle', 'wb') as file_lt_eq:
                pickle.dump(data_to_export_lt_eq, file_lt_eq)

        except Exception as e:
            # Handle exceptions here if needed
            pass

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for exporting lt_eq data
lt_eq_ltp_quantity_loop()

def kotakbank_eq_ltp_quantity_loop():
    global kotakbank_eq_lp_value, kotakbank_eq_quantity

    while True:
        try:
            # Create a dictionary with the data to export
            data_to_export_kotakbank_eq = {
                'kotakbank_eq_lp_value': kotakbank_eq_lp_value,
                'kotakbank_eq_quantity': kotakbank_eq_quantity,
            }

            # Export data for kotakbank_eq_lp_value
            with open('data_kotakbank_eq.pickle', 'wb') as file_kotakbank_eq:
                pickle.dump(data_to_export_kotakbank_eq, file_kotakbank_eq)

        except Exception as e:
            # Handle exceptions here if needed
            pass

        time.sleep(0.1)  # Adjust the interval as needed for the loop to run periodically

# You can then call this function to start the loop for exporting kotakbank_eq data
kotakbank_eq_ltp_quantity_loop()



