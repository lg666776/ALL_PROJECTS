remove_date = "2024-2-5 15:25:00"
adding_next = "2024-2-5 15:20:00"
#.............................
midcap_remove_date = "2024-2-2 15:25:00"
midcap_adding_next = "2024-2-2 15:20:00"
#.............................
finnifty_remove_date = "2024-2-2 15:25:00"
finnifty_adding_next = "2024-2-2 15:20:00"
#.............................
banknifty_remove_date = "2024-2-2 15:25:00"
banknifty_adding_next = "2024-2-2 15:20:00"
#.............................

nifty_high = 21700.00
nifty_low = 21680.10
nifty_close = 21690.30
#.............................
midcap_high = 20430.80
midcap_low = 20408.30
midcap_close = 20430.80
#.............................
finnifty_high = 20430.80
finnifty_low = 20408.30
finnifty_close = 20430.80
#........................
banknifty_high = 20430.80
banknifty_low = 20408.30
banknifty_close = 20430.80
#........................


# Create a dictionary to store these values
ohlc = {
    'nifty_remove_date': remove_date,
    'nifty_adding_next': adding_next,
    'nifty_high': nifty_high,
    'nifty_low': nifty_low,
    'nifty_close': nifty_close,
    'midcap_remove_date': midcap_remove_date,
    'midcap_adding_next': midcap_adding_next,
    'midcap_high': midcap_high,
    'midcap_low': midcap_low,
    'midcap_close': midcap_close,
    'finnifty_remove_date': finnifty_remove_date,
    'finnifty_adding_next': finnifty_adding_next,
    'finnifty_high': finnifty_high,
    'finnifty_low': finnifty_low,
    'finnifty_close': finnifty_close,
    'banknifty_remove_date': banknifty_remove_date,
    'banknifty_adding_next': banknifty_adding_next,
    'banknifty_high': banknifty_high,
    'banknifty_low': banknifty_low,
    'banknifty_close': banknifty_close,

}

# Specify the file path where you want to save the text file
file_path = 'ohlc.txt'

# Open the file in write mode and write the data
with open(file_path, 'w') as file:
    for key, value in ohlc.items():
        file.write(f"{key}: {value}\n")