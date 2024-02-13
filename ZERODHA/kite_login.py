from selenium import webdriver
from kiteconnect import KiteConnect
import pyotp
import time


# API credentials and user details
api_key = "58954202154230154"
api_secret = "2548521548451254"
username = "ZLD220"
password = "KJHGUGHV"
totp_secret = "GFVHYFHV"


# Auto Log In and Get Access Token
def get_access_token(username, password, api_key, api_secret, totp_secret):
    driver = webdriver.Chrome()
    driver.get("https://kite.zerodha.com/login")

    # Fill in the login form
    driver.find_element_by_id("userid").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)

    # Generate TOTP code
    totp = pyotp.TOTP(totp_secret)
    totp_code = totp.now()

    driver.find_element_by_id("twofa").send_keys(totp_code)

    # Submit the login form
    driver.find_element_by_class_name("button-orange").click()

    # Wait for the redirect and retrieve the request token from the redirected URL
    time.sleep(5)  # Wait for the page to load
    redirected_url = driver.current_url
    request_token = redirected_url.split("request_token=")[1].split("&action=")[0]

    # Close the browser window
    driver.quit()

    # Initialize KiteConnect instance


    # Generate session and obtain access token
    kite = KiteConnect(api_key=api_key)
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    kite.set_access_token(access_token)
    print("Access token set successfully.")

    return access_token


# Main entry point
if __name__ == "__main__":
    access_token = get_access_token(username, password, api_key, api_secret, totp_secret)

    # Initialize KiteConnect instance
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
