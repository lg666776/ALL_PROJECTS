remove_date = "2023-12-21 15:25:00"
adding_next = "2023-12-21 15:20:00"


nifty_high = 21288.5
nifty_low = 21260.00
nifty_close = 21283.00


# Create a dictionary to store these values
ohlc = {
    'nifty_remove_date': remove_date,
    'nifty_adding_next': adding_next,
    'nifty_high': nifty_high,
    'nifty_low': nifty_low,
    'nifty_close': nifty_close,
}


# Specify the file path where you want to save the text file
file_path = 'nifty_ohlc.txt'

# Open the file in write mode and write the data
with open(file_path, 'w') as file:
    for key, value in ohlc.items():
        file.write(f"{key}: {value}\n")