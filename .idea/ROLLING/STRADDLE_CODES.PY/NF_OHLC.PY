remove_date = "2024-2-5 15:25:00"
adding_next = "2024-2-5 15:20:00"
exp_remove_date = "2024-2-2 15:25:00"
exp_adding_next = "2024-2-2 15:20:00"



nifty_high = 21700.00
nifty_low = 21680.10
nifty_close = 21690.30
#.............................
exp_high = 20430.80
exp_low = 20408.30
exp_close = 20430.80


# Create a dictionary to store these values
ohlc = {
    'nifty_remove_date': remove_date,
    'nifty_adding_next': adding_next,
    'nifty_high': nifty_high,
    'nifty_low': nifty_low,
    'nifty_close': nifty_close,
    'exp_remove_date': exp_remove_date,
    'exp_adding_next': exp_adding_next,
    'exp_high': exp_high,
    'exp_low': exp_low,
    'exp_close': exp_close,

}

# Specify the file path where you want to save the text file
file_path = 'nifty_ohlc.txt'

# Open the file in write mode and write the data
with open(file_path, 'w') as file:
    for key, value in ohlc.items():
        file.write(f"{key}: {value}\n")