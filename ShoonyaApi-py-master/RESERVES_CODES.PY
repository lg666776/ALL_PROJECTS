def sell_condition_check():
    global tata_motors_lp_value, store_low_sell, sell_order_details, order_status_counts, total_count, executed_low_values

    sell_order_executed = False
    max_retries = 2
    retries = 0

    while not sell_order_executed and retries < max_retries:
        # Check if the current time is after 15:00
        current_time = datetime.datetime.now().time()
        if current_time >= datetime.time(15, 0):
            print("Current time is after 15:00. Clearing executed_low_values and sell_order_details dictionaries...")
            executed_low_values.clear()  # Clear the executed_low_values set
            sell_order_details.clear()  # Clear the sell_order_details dictionary
            # Save the cleared sell_order_details dictionary to a pickle file
            with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                pickle.dump(sell_order_details, file)
            # Save the updated executed_low_values set to a file after removing the item
            with open(EXECUTED_LOW_VALUES_FILE, 'wb') as file:
                pickle.dump(executed_low_values, file)

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    pass
                else:
                    # Check if the current time is before 14:20
                    current_time = datetime.datetime.now().time()
                    if current_time < datetime.time(14, 20):
                        # Check your sell conditions and place sell orders here
                        if tata_motors_lp_value is not None and store_low_sell is not None:
                            if isinstance(tata_motors_lp_value, (int, float)) and isinstance(store_low_sell,
                                                                                             (int, float)):
                                entry_price = store_low_sell
                                if tata_motors_lp_value < entry_price and tata_motors_lp_value > (entry_price - 2):
                                    if store_low_sell not in executed_low_values:
                                        # Check if the current time is before 14:20
                                        current_time = datetime.datetime.now().time()
                                        if current_time < datetime.time(14, 20):
                                            time.sleep(3)  # Add a 5-second delay
                                            print("Sell condition for TATAMOTORS is TRUE! Order placed...")
                                            sell_order_details = execute_sell_trade()
                                            print("Order Details:", sell_order_details)
                                            if any(isinstance(order_info, dict) and order_info.get(
                                                    'Status') == 'COMPLETE' for orderno, order_info in
                                                   sell_order_details.items()):
                                                sell_order_executed = True
                                                executed_low_values.add(store_low_sell)
                                                # Save the updated executed_low_values set to a file after removing
                                                # the item
                                                with open(EXECUTED_LOW_VALUES_FILE, 'wb') as file:
                                                    pickle.dump(executed_low_values, file)

                                                print("Sell order executed successfully.")
                                            else:
                                                print('Sell Order not Executed')
                                                retries += 1

                                            # Check if either of the conditions is reached and stop taking trades if
                                            # true
                                            if len(executed_low_values) >= 2 or total_count >= 6:
                                                print("Either condition reached. Stopping further sell trades.")
                                                break

        # Sleep statement outside the for loop
        time.sleep(1)  # Adjust the interval as needed


def sell_condition_check():
    global tata_motors_lp_value, store_low_sell, sell_order_details, order_status_counts, total_count, executed_low_values

    sell_order_executed = False
    max_retries = 0
    retries = 0

    while not sell_order_executed and retries < max_retries:
        # Check if the current time is after 15:00
        current_time = datetime.datetime.now().time()
        if current_time >= datetime.time(15, 0):
            print("Current time is after 15:00. Clearing executed_low_values and sell_order_details dictionaries...")
            executed_low_values.clear()  # Clear the executed_low_values set
            sell_order_details.clear()  # Clear the sell_order_details dictionary
            # Save the cleared sell_order_details dictionary to a pickle file
            with open(SELL_ORDER_DETAILS_FILE, 'wb') as file:
                pickle.dump(sell_order_details, file)
            # Save the updated executed_low_values set to a file after removing the item
            with open(EXECUTED_LOW_VALUES_FILE, 'wb') as file:
                pickle.dump(executed_low_values, file)

        for orderno, order_info in buy_order_details.items():
            if isinstance(order_info, dict):  # Check if order_info is a dictionary
                if order_info.get('Status') == 'COMPLETE' and order_info.get('trantype') == 'B' and order_info.get(
                        'remarks') == 'my_order_001':
                    pass
                else:
                    if any(isinstance(order_info, dict) and order_info.get('trantype') == 'S' for
                           orderno, order_info in sell_order_details.items()):
                        pass  # Do nothing if the sell order is already present
                    else:
                        # Check if the current time is before 14:20
                        current_time = datetime.datetime.now().time()
                        if current_time < datetime.time(14, 20):
                            # Check your sell conditions and place sell orders here
                            if tata_motors_lp_value is not None and store_low_sell is not None:
                                if isinstance(tata_motors_lp_value, (int, float)) and isinstance(store_low_sell,
                                                                                                 (int, float)):
                                    entry_price = store_low_sell
                                    if tata_motors_lp_value < entry_price and tata_motors_lp_value > (entry_price - 2):
                                        if store_low_sell not in executed_low_values:
                                            # Check if the current time is before 14:20
                                            current_time = datetime.datetime.now().time()
                                            if current_time < datetime.time(14, 20):
                                                time.sleep(3)  # Add a 5-second delay
                                                print("Sell condition for TATAMOTORS is TRUE! Order placed...")
                                                sell_order_details = execute_sell_trade()
                                                print("Order Details:", sell_order_details)
                                                if any(isinstance(order_info, dict) and order_info.get(
                                                        'Status') == 'COMPLETE' for orderno, order_info in
                                                       sell_order_details.items()):
                                                    sell_order_executed = True
                                                    executed_low_values.add(store_low_sell)
                                                    # Save the updated executed_low_values set to a file after removing
                                                    # the item
                                                    with open(EXECUTED_LOW_VALUES_FILE, 'wb') as file:
                                                        pickle.dump(executed_low_values, file)

                                                    print("Sell order executed successfully.")
                                                else:
                                                    print('Sell Order not Executed')
                                                    retries += 0

                                                # Check if either of the conditions is reached and stop taking trades if
                                                # true
                                                if len(executed_low_values) >= 2 or total_count >= 6:
                                                    print("Either condition reached. Stopping further sell trades.")
                                                    break

        # Sleep statement outside the for loop
        time.sleep(1)  # Adjust the interval as needed



def buy_condition_check():
    global tata_motors_lp_value, store_high, buy_order_details, order_status_counts, total_count, executed_high_values

    buy_order_executed = False  # Flag to track if the buy order has been executed
    max_retries = 2  # Maximum number of retries for placing the buy order

    retries = 0  # Counter for retries

    executed_high_values = set()  # Set to track the high values for which trades have been executed

    while not buy_order_executed and retries < max_retries:
        print(executed_high_values)
        if tata_motors_lp_value is not None and store_high is not None:
            if isinstance(tata_motors_lp_value, (int, float)) and isinstance(store_high, (int, float)):
                entry_price = store_high
                if tata_motors_lp_value > entry_price and tata_motors_lp_value < (entry_price + 2):
                    if store_high not in executed_high_values:
                        # Check if a buy order with 'trantype': 'B' is not already present
                        if any(isinstance(order_info, dict) and order_info.get('trantype') == 'B' for
                               orderno, order_info in buy_order_details.items()):
                            pass  # Do nothing if the buy order is already present
                        else:
                            # Check if the current time is before 14:20
                            current_time = datetime.datetime.now().time()
                            if current_time < datetime.time(14, 20):
                                time.sleep(3)  # Add a 5-second delay
                                print("Buy condition for TATAMOTORS is TRUE! Order placed...")
                                buy_order_details = execute_buy_trade()
                                print("Order Details:", buy_order_details)
                                executed_high_values.add(store_high)
                                if any(isinstance(order_info, dict) and order_info.get('Status') == 'COMPLETE' for
                                       orderno, order_info in buy_order_details.items()):
                                    buy_order_executed = True  # Set the flag to True once the buy order is executed
                                    # Add the high value to the set of executed
                                    # trades
                                    print("Buy order executed successfully.")
                                else:
                                    print('Buy Order not Executed')
                                    retries += 1

                                # Check if either of the conditions is reached and stop taking trades if true
                                if len(executed_high_values) >= 2 or total_count >= 6:
                                    print("Either condition reached. Stopping further buy trades.")
                                    break
            else:
                print("Buy condition for TATAMOTORS is not met. Skipping trade...")

        time.sleep(1)  # Adjust the interval as needed

        # Save the updated executed_high_values set to a file after removing the item
        with open(EXECUTED_HIGH_VALUES_FILE, 'wb') as file:
            pickle.dump(executed_high_values, file)
