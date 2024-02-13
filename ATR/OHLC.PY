remove_date = "2023-12-21 15:25:00"
adding_next = "2023-12-21 15:20:00"

# Define your values
tcs_high = 3509.00
tcs_low = 3506.20
tcs_close = 3508.10
# ....................
itc_high = 448.40
itc_low = 447.20
itc_close = 448.00
# ....................
sbin_high = 576.25
sbin_low = 575.70
sbin_close = 576.20
# ....................
tatam_high = 668.00
tatam_low = 666.50
tatam_close = 666.50
# ....................
bajfsv_high = 1648.00
bajfsv_low = 1641.10
bajfsv_close = 1641.10
# ....................
titan_high = 3289.00
titan_low = 3280.00
titan_close = 3284.00
# ....................
hindalco_high = 480.80
hindalco_low = 479.00
hindalco_close = 479.20
# ....................
jsw_high = 777.00
jsw_low = 773.30
jsw_close = 775.00
# ....................
tatastl_high = 125.45
tatastl_low = 125.00
tatastl_close = 125.00
# ....................
axisbk_high = 21288.5
axisbk_low = 21260.00
axisbk_close = 21283.00
# ....................
indusind_high = 1465.30
indusind_low = 1459.05
indusind_close = 1459.05
# ....................
kotakbk_high = 1759.00
kotakbk_low = 1753.25
kotakbk_close = 1754.00
# ....................
dlf_high = 569.00
dlf_low = 566.80
dlf_close = 569.00
# ....................
mm_high = 1564.90
mm_low = 1562.20
mm_close = 1564.50
# ....................
infy_high = 1428.00
infy_low = 1425.95
infy_close = 1426.45
# ....................
bajfin_high = 8054.60
bajfin_low = 8040.05
bajfin_close = 8043.00
# ....................
wipro_high = 411.35
wipro_low = 410.30
wipro_close = 411.00
# ....................
icicibk_high = 952.35
icicibk_low = 949.30
icicibk_close = 949.50
# ....................
lt_high = 3092.75
lt_low = 3086.20
lt_close = 3090.00
# ....................
techm_high = 1194.25
techm_low = 1192.35
techm_close = 1193.10
# ....................
bajauto_high = 000.00
bajauto_low = 000.00
bajauto_close = 000.00
# ....................
hal_high = 000.00
hal_low = 000.00
hal_close = 000.00
# ....................
hcltech_high = 000.00
hcltech_low = 000.00
hcltech_close = 000.00
# ....................
ntpc_high = 000.00
ntpc_low = 000.00
ntpc_close = 000.00
# ....................
ltim_high = 000.00
ltim_low = 000.00
ltim_close = 000.00


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
    'wipro_high': wipro_high,
    'wipro_low': wipro_low,
    'wipro_close': wipro_close,
    'icicibk_high': icicibk_high,
    'icicibk_low': icicibk_low,
    'icicibk_close': icicibk_close,
    'lt_high': lt_high,
    'lt_low': lt_low,
    'lt_close': lt_close,
    'techm_high': techm_high,
    'techm_low': techm_low,
    'techm_close': techm_close,
    'bajauto_high': bajauto_high,
    'bajauto_low': bajauto_low,
    'bajauto_close': bajauto_close,
    'hal_high': hal_high,
    'hal_low': hal_low,
    'hal_close': hal_close,
    'ntpc_high': ntpc_high,
    'ntpc_low': ntpc_low,
    'ntpc_close': ntpc_close,
    'ltim_high': ltim_high,
    'ltim_low': ltim_low,
    'ltim_close': ltim_close,
    'hcltech_high': hcltech_high,
    'hcltech_low': hcltech_low,
    'hcltech_close': hcltech_close,

}

# Specify the file path where you want to save the text file
file_path = 'ohlc.txt'

# Open the file in write mode and write the data
with open(file_path, 'w') as file:
    for key, value in ohlc.items():
        file.write(f"{key}: {value}\n")
