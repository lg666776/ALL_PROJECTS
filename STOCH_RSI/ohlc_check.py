# Specify the file path where the data is stored
file_path = 'ohlc.txt'

# Create a dictionary to store the values
ohlc = {}

# Open the file in read mode
with open(file_path, 'r') as file:
    # Read each line in the file
    for line in file:
        # Split each line by ':' to separate the key and value
        key, value = line.strip().split(': ')
        # Remove double quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]  # Remove double quotes
        # Check if the value is numeric (float)
        if '.' in value:
            ohlc[key] = float(value)
        else:
            ohlc[key] = value  # Store as a string

# Access and print individual values
tcs_high = ohlc['tcs_high']
tcs_low = ohlc['tcs_low']
tcs_close = ohlc['tcs_close']

remove_date = ohlc['remove_date']
adding_next = ohlc['adding_next']

# Extract the string '2023-10-03 15:25:00' from the dictionary and add single quotes
remove_date_string = "'" + ohlc['remove_date'] + "'"
added_date_string = "'" + ohlc['adding_next'] + "'"

# Print the modified string with single quotes
print(remove_date_string)
print(added_date_string)

# Specify the file path where you want to save the text file
file_path = 'ohlc.txt'

# Open the file in read mode and print its contents
with open(file_path, 'r') as file:
    file_contents = file.read()

# Print the contents of the file
print(file_contents)

