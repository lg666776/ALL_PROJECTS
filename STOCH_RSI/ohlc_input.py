remove_date = "2023-10-05 15:25:00"
adding_next = "2023-10-05 15:20:00"

# Define your values
tcs_high = 3548.00
tcs_low = 3535.85
tcs_close = 3545.00
# ....................
itc_high = 437.00
itc_low = 436.00
itc_close = 436.50
# ....................
sbin_high = 592.00
sbin_low = 591.20
sbin_close = 592.00
# ....................
tatam_high = 619.70
tatam_low = 619.40
tatam_close = 619.40
# ....................
bajfsv_high = 1545.95
bajfsv_low = 1540.90
bajfsv_close = 1544.00
# ....................
titan_high = 3218.85
titan_low = 3213.30
titan_close = 3218.65
# ....................
hindalco_high = 3517.40
hindalco_low = 3502.25
hindalco_close = 3507.10
# ....................
jsw_high = 3517.40
jsw_low = 3502.25
jsw_close = 3507.10
# ....................
tatastl_high = 758.75
tatastl_low = 755.15
tatastl_close = 757.10
# ....................
axisbk_high = 1004.75
axisbk_low = 1002.75
axisbk_close = 1003.75
# ....................
indusind_high = 1403.95
indusind_low = 1401.05
indusind_close = 1402.70
# ....................
kotakbk_high = 1734.95
kotakbk_low = 1731.00
kotakbk_close = 1733.30
# ....................
dlf_high = 525.90
dlf_low = 524.65
dlf_close = 525.00
# ....................
mm_high = 1550.80
mm_low = 1541.45
mm_close = 1548.85
# ....................
infy_high = 1550.80
infy_low = 1541.45
infy_close = 1548.85
# ....................
bajfin_high = 1550.80
bajfin_low = 1541.45
bajfin_close = 1548.85
# ....................

# Create a dictionary to store these values
ohlc = {
    'remove_date': remove_date,
    'adding_next': adding_next,
    'tcs_high': tcs_high,
    'tcs_low': tcs_low,
    'tcs_close': tcs_close,
    'itc_high': itc_high,
    'itc_low': itc_low,
    'itc_close': itc_close,
    'sbin_high': sbin_high,
    'sbin_low': sbin_low,
    'sbin_close': sbin_close,
    'tatam_high': tatam_high,
    'tatam_low': tatam_low,
    'tatam_close': tatam_close,
    'bajfsv_high': bajfsv_high,
    'bajfsv_low': bajfsv_low,
    'bajfsv_close': bajfsv_close,
    'titan_high': titan_high,
    'titan_low': titan_low,
    'titan_close': titan_close,
    'hindalco_high': hindalco_high,
    'hindalco_low': hindalco_low,
    'hindalco_close': hindalco_close,
    'jsw_high': jsw_high,
    'jsw_low': jsw_low,
    'jsw_close': jsw_close,
    'tatastl_high': tatastl_high,
    'tatastl_low': tatastl_low,
    'tatastl_close': tatastl_close,
    'axisbk_high': axisbk_high,
    'axisbk_low': axisbk_low,
    'axisbk_close': axisbk_close,
    'indusind_high': indusind_high,
    'indusind_low': indusind_low,
    'indusind_close': indusind_close,
    'kotakbk_high': kotakbk_high,
    'kotakbk_low': kotakbk_low,
    'kotakbk_close': kotakbk_close,
    'dlf_high': dlf_high,
    'dlf_low': dlf_low,
    'dlf_close': dlf_close,
    'mm_high': mm_high,
    'mm_low': mm_low,
    'mm_close': mm_close,
    'infy_high': infy_high,
    'infy_low': infy_low,
    'infy_close': infy_close,
    'bajfin_high': bajfin_high,
    'bajfin_low': bajfin_low,
    'bajfin_close': bajfin_close,
}

# Specify the file path where you want to save the text file
file_path = 'ohlc.txt'

# Open the file in write mode and write the data
with open(file_path, 'w') as file:
    for key, value in ohlc.items():
        file.write(f"{key}: {value}\n")
