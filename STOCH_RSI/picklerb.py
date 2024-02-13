import pickle
import time

while True:
    # Read data from the pickle file
    with open('data_test03.pickle', 'rb') as file_test03:
        loaded_data = pickle.load(file_test03)

    # Access the values of tcs_lp_value and tcs_quantity
    tcs_lp_value = loaded_data['tcs_lp_value']
    tcs_quantity = loaded_data['tcs_quantity']

    # Display the values
    print('tcs_lp_value:', tcs_lp_value)
    print('tcs_quantity:', tcs_quantity)

    # Add a delay before the next iteration
    time.sleep(0.01)  # Sleep for 5 seconds (adjust the interval as needed)



