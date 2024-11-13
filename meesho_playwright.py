from browserforge.fingerprints import FingerprintGenerator
from browserforge.injectors.playwright import NewContext
from playwright.sync_api import sync_playwright
from evpn import ExpressVpnApi
from datetime import datetime
import pymysql
import random
import time
import json
import os


# VPN Switching
def change_vpn(api, locations):
    loc = random.choice(locations)
    api.connect(loc["id"])
    time.sleep(5)
    print('VPN Connected...!' if api.is_connected else 'VPN not Connected!!')


# Login function using Playwright
def login():
    fingerprint = FingerprintGenerator().generate()
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=False)
        # context = NewContext(browser=browser, fingerprint=fingerprint)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

        context = NewContext(browser, fingerprint=fingerprint, user_agent=user_agent)

        # Create a new page and apply fingerprint
        page = context.new_page()

        login_successful = False

        def handle_login_response(response):
            if 'verify.json' in response.url:
                print(f"Login verification response received from: {response.url}")
                nonlocal login_successful
                login_successful = True

        page.on('response', handle_login_response)  # Listen to network responses

        page.goto('https://www.meesho.com/auth')  # Navigate to login page

        page.locator('//input[@type="tel"]').fill(mobile_number)  # Fill the mobile number

        page.locator('//button[@type="submit"]').click()  # Submit login form

        otp = input('Enter OTP: ')  # Wait for the user to input the OTP
        for i, digit in enumerate(otp):
            page.locator(f'//input[@type="tel"][{i + 1}]').fill(digit)  # Fill OTP digits into corresponding input fields

        time.sleep(3)  # Wait for login to complete

        if login_successful:
            context.storage_state(path=session_storage_filename)  # Save session cookies if login was successful
            print("Session cookies saved successfully.")

        # Close the page
        page.close()
        # Close the context
        context.close()
        # Close the browser
        browser.close()

        return login_successful


# Function to send requests to a URL
def send_request(page, url, pincode, api, locations, session_data):
    # Set cookies for the current page's context
    page.context.add_cookies(session_data['cookies'])

    page.goto(url)

    # Handle "Access Denied" scenarios
    if page.locator('//h1[contains(text(), "Access Denied")]').count() > 0:
        review = page.locator('//h1[contains(text(), "Access Denied")]').first
        if 'access denied' in review.text_content().lower():
            change_vpn(api, locations)
            return None  # Skip this page

    # Try to fill in the pincode if the input field exists
    if page.locator('//input[@id="pin"]').count() > 0:
        page.locator('//input[@id="pin"]').fill(pincode)
        print(f"Pincode {pincode} inserted.")

        if page.locator('//span[text()="CHECK"]').count() > 0:
            page.locator('//span[text()="CHECK"]').click()
            print(f"Checking delivery for {url}...")
    else:
        print(f"Unable to insert pincode for {url}.")
        # Update product link status
        update_query = f"UPDATE product_links_20241017 SET status_{pincode} = 'no option' WHERE meesho_pid = %s"
        local_cursor.execute(update_query, (url.replace("https://www.meesho.com/s/p/", '').strip(),))
        local_connect.commit()
        return None

    time.sleep(2)  # Wait for the response to load

    # Check for specific messages and trigger VPN change if needed
    try:
        text_data = page.locator('//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]').first
        if 'Enter Pincode for Estimated Delivery Date' in text_data.text_content():
            change_vpn(api, locations)
            print("Changing VPN...")
            return None
    except Exception as e:
        print(e)

    return page.content()  # Return the page content for further processing


# Scraper function using Playwright
def scraper(pincode, start_id, end_id):
    # Load cookies from the saved session file
    with open(session_storage_filename, 'r', encoding='utf-8') as file:
        session_data = json.loads(file.read())
        print(session_data)

    query = f"""
        SELECT meesho_pid FROM product_links_20241017 
        WHERE status='pending' AND status_{pincode} != 'Done' AND status_{pincode} != 'no option'
        AND id BETWEEN {start_id} AND {end_id}
        """
    query = f"""SELECT Product_Url_MEESHO FROM template_20241017 WHERE `status` != 'Done' AND status_{pincode} != 'Done' AND id BETWEEN {start_id} AND {end_id}"""
    local_cursor.execute(query)
    rows = local_cursor.fetchall()
    print(len(rows), "total links found.")

    # Iterate over all product links
    for pid in rows:
        link = f'https://www.meesho.com/s/p/{pid[0]}'
        print('Working on', link)

        fingerprint = FingerprintGenerator().generate()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False, )
            # context = NewContext(browser, fingerprint=fingerprint)
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

            context = NewContext(browser, fingerprint=fingerprint, user_agent=user_agent)
            # Tarnished.apply_stealth(context)

            page = context.new_page()

            # Set the viewport size to match the screen size (fullscreen effect)
            page.set_viewport_size({"width": 1920, "height": 1080})

            # # Set cookies for the current page's context
            # page.context.add_cookies(session_data['cookies'])

            # Navigate to the main website or another page to confirm login session is active
            # page.goto('https://www.meesho.com/best-quality-super-fine-100-percent-soft-cotton-vests-pack-of-4/p/6fptlv')

            # # Print the title of the current page
            # print("Page title after setting cookies:", page.title())
            # time.sleep(5)

            # Add your scraping logic here, e.g., navigating to product pages and scraping content.
            print('sending req')
            page_content = send_request(url=link, page=page, pincode=pincode, locations=locations, api=api, session_data=session_data)
            print(page_content)

            if page_content:
                # Generate unique hash ID for the page
                # page_id = hashlib.sha256((link + f'_{pincode}').encode()).hexdigest()
                page_save_name = f'{pid[0]}_{pincode}'
                save_path = fr'../pagesave_meesho/{page_save_name}.html'

                # Save the page content to a file
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(page_content)
                    print("page saved...")

                # Insert data into the database
                insert_query = f"""
                INSERT INTO mesho_pages (url, pincode, page_hash) 
                VALUES (%s, %s, %s)
                """
                local_cursor.execute(insert_query, (link, pincode, page_save_name))
                local_connect.commit()
                print("inerted data to meesho page")

                # Update product link status
                update_query = f"UPDATE product_links_20241017 SET status_{pincode} = 'Done' WHERE meesho_pid = %s"
                local_cursor.execute(update_query, (pid[0],))
                local_connect.commit()

            # Close the browser after processing each product
            browser.close()
            playwright.stop()


# Main function to handle login and scraping
def main(pincode, start_id, end_id):
    if os.path.exists(session_storage_filename):
        print('Cookies already present...')
        scraper(pincode, start_id, end_id)
    else:
        print('Cookies not present...')
        # Attempt login if session storage is not found
        logged_in = login()
        if logged_in:
            print("Login successful!")
            scraper(pincode, start_id, end_id)
        else:
            print("Login failed!")


if __name__ == "__main__":
    # Database connection setup
    local_connect = pymysql.connect(host='localhost', user='root', password='actowiz', database='meesho_page_save', autocommit=True)
    local_cursor = local_connect.cursor()

    # Create table if it doesn't exist
    local_cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesho_pages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(500),
        pincode VARCHAR(10),
        page_hash VARCHAR(500)
    )
    ''')

    mobile_num_dict = {
        'bhargav': '9824818225',
        'deekshant': '6204387213',
        'jaimin': '6354521692',
        'hritik': '9879361219',
        'karan': '6359015644',
        'nirmal': '6352290451',
        'pritesh': '9586653146',
        'siraj': '8758356372',
        'smitesh': '9574945690',
        'surya': '9737090010',
    }

    mobile_number = mobile_num_dict['hritik']
    # mobile_number = '9099071762'
    today_date = datetime.now().strftime("%Y%m%d")
    start_time = time.time()
    session_storage_filename = fr"../cookies/{mobile_number}_{today_date}_session_storage.json"
    with ExpressVpnApi() as api:
        locations = [{'id': 26, 'name': 'USA - New Jersey - 1', 'country_code': 'US'}, {'id': 168, 'name': 'USA - New Jersey - 3', 'country_code': 'US'},
                     {'id': 75, 'name': 'USA - New York', 'country_code': 'US'}, {'id': 166, 'name': 'USA - Tampa - 1', 'country_code': 'US'},
                     {'id': 165, 'name': 'USA - Houston', 'country_code': 'US'}, {'id': 19, 'name': 'USA - Atlanta', 'country_code': 'US'},
                     {'id': 202, 'name': 'USA - Miami - 2', 'country_code': 'US'}, {'id': 54, 'name': 'USA - Miami', 'country_code': 'US'},
                     {'id': 25, 'name': 'USA - Washington DC', 'country_code': 'US'}, {'id': 18, 'name': 'USA - Dallas', 'country_code': 'US'},
                     {'id': 172, 'name': 'USA - Denver', 'country_code': 'US'}, {'id': 9, 'name': 'USA - Chicago', 'country_code': 'US'},
                     {'id': 161, 'name': 'USA - Lincoln Park', 'country_code': 'US'}, {'id': 95, 'name': 'USA - Albuquerque', 'country_code': 'US'},
                     {'id': 1, 'name': 'USA - San Francisco', 'country_code': 'US'}, {'id': 74, 'name': 'USA - Los Angeles - 3', 'country_code': 'US'},
                     {'id': 70, 'name': 'USA - Los Angeles - 2', 'country_code': 'US'}, {'id': 2, 'name': 'USA - Seattle', 'country_code': 'US'},
                     {'id': 94, 'name': 'USA - Phoenix', 'country_code': 'US'}, {'id': 155, 'name': 'USA - New Jersey - 2', 'country_code': 'US'},
                     {'id': 6, 'name': 'USA - Los Angeles - 1', 'country_code': 'US'}, {'id': 71, 'name': 'USA - Los Angeles - 5', 'country_code': 'US'},
                     {'id': 207, 'name': 'USA - Santa Monica', 'country_code': 'US'}]
        change_vpn(api=api, locations=locations)
        main(pincode="560001", start_id=31, end_id=10000)
    end_time = time.time()

    print("Time :", end_time - start_time)

"""
siraj: 8758356372
karan: 6359015644
smitesh :9574945690
pritesh: 9586653146
bhargav: 9824818225
deekshant: 6204387213
nirmal: 6352290451
jaimin: 6354521692
hritik: 9879361219
surya: 9737090010
"""
