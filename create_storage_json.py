from datetime import datetime
from playwright.sync_api import sync_playwright
from browserforge.fingerprints import FingerprintGenerator
from browserforge.injectors.playwright import NewContext
import time


# Login function using Playwright
def login(page, context, phone):
    login_successful = False

    def handle_login_response(response):
        if 'verify.json' in response.url:
            print(f"Login verification response received from: {response.url}")
            nonlocal login_successful
            login_successful = True

    # Listen to network responses
    page.on('response', handle_login_response)

    # Navigate to login page
    page.goto('https://www.meesho.com/auth')

    # Fill mobile number
    page.locator('//input[@type="tel"]').fill(f"{phone}")  # EDIT THIS
    page.locator('//button[@type="submit"]').click()

    # Wait for the user to input the OTP
    otp = input('Enter OTP: ')
    for i, digit in enumerate(otp):
        page.locator(f'//input[@type="tel"][{i + 1}]').fill(digit)

    time.sleep(5)  # Wait for login to complete

    # Save session if login successful
    if login_successful:
        print('storing json cookie')
        context.storage_state(path=f"{phone}_{file_date}.json")
    return login_successful


phone = "6352290451"
file_date = str(datetime.now().strftime("%Y%m%d"))
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    context = NewContext(browser, fingerprint=fingerprint)
    page = context.new_page()
    logg_in = login(page=page, context=context, phone=phone)
    if logg_in:
        print("login successfully completed and file saved...")
    else:
        print("something went wrong....")
    browser.close()

"""
siraj bhai : 8758356372
karan: 6359015644
smitesh :9574945690
pritesh: 9586653146
bhargav: 9824818225
deekshant: 6204387213
nirmal: 6352290451
jaimin: 6354521692
hritik: 9879361219
"""
