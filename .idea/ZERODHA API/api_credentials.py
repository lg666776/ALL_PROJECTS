from kiteconnect import KiteConnect
import datetime

from kiteconnect import KiteConnect

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

def get_access_token():
    kite = KiteConnect(api_key=api_key)

    # Get the access token URL
    access_token_url = kite.login_url()
    access_token_url = access_token_url.replace("YOUR_API_KEY", api_key)
    print("Login URL: " + access_token_url)

    # Manually authorize and obtain the access token
    request_token = input("Enter the request token from the redirected URL: ")
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    kite.set_access_token(access_token)
    print("Access token set successfully.")
    return kite

def check_access_token_expiry(kite):
    token_expiry = datetime.datetime.fromtimestamp(kite.ltp("NIFTY:EQ")['NIFTY:EQ']['timestamp'])
    current_time = datetime.datetime.now()
    if current_time >= token_expiry:
        print("Access token has expired.")
    else:
        print("Access token is valid.")

# Main entry point
if __name__ == "__main__":
    get_access_token()


    def get_api_secret():
        return api_secret