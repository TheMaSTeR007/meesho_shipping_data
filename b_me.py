import os
import json
import random
import time
import pymysql
import hashlib
from playwright.sync_api import sync_playwright
from browserforge.fingerprints import FingerprintGenerator
from browserforge.injectors.playwright import NewContext
from undetected_playwright import Tarnished
from evpn import ExpressVpnApi


# Random wait functions
def random_wait():
    time.sleep(random.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0]))


def small_random_wait():
    time.sleep(random.choice([0.2, 0.3, 0.4, 0.5]))


# Function to initialize Playwright, browser context, and page
def create_browser_page():

    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)

    fingerprints = FingerprintGenerator()
    fingerprint = fingerprints.generate()
    context = NewContext(browser, fingerprint=fingerprint)

    Tarnished.apply_stealth(context)  # Apply stealth mode to avoid detection
    page = context.new_page()

    page.set_viewport_size({"width": 1920, "height": 1080})

    return playwright, browser, context, page


# Function to load session cookies
def load_session_cookies(context, session_file='session_storage.json'):
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    context.add_cookies(session_data['cookies'])


# Function to change VPN location
def change_vpn(api, locations):
    loc = random.choice(locations)  # Pick a random location
    api.connect(loc["id"])
    time.sleep(5)  # Allow time for the VPN to connect


# Function to send requests to a URL
def send_request(page, url, pincode, api, locations):
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
        update_query = f"UPDATE product_links SET status_{pincode} = 'no option' WHERE meesho_pid = %s"
        local_cursor.execute(update_query, (url.replace("https://www.meesho.com/s/p/",'').strip(),))
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
    except:
        pass

    return page.content()  # Return the page content for further processing


# Scraper function
def scraper(pincode, start_id, end_id, api, locations):
    query = f"""
    SELECT meesho_pid FROM product_links 
    WHERE status='pending' AND status_{pincode} != 'Done' AND status_{pincode} != 'no option'
    AND id BETWEEN {start_id} AND {end_id}
    """
    local_cursor.execute(query)
    rows = local_cursor.fetchall()
    print(len(rows), "total links found.")

    # Iterate over all product links
    for pid in rows:
        link = f'https://www.meesho.com/s/p/{pid[0]}'

        # Create browser, context, and page
        playwright, browser, context, page = create_browser_page()

        # Load session cookies
        load_session_cookies(context)

        # Send request and process the response
        content = send_request(page, link, pincode, api, locations)

        if content:
            # Generate unique hash ID for the page
            page_id = hashlib.sha256((link + f'_{pincode}').encode()).hexdigest()
            save_path = fr'C:\KARAN\mesho\pagesave_meesho\{page_id}.html'

            # Save the page content to a file
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(content)
                print("page saved...")

            # Insert data into the database
            insert_query = f"""
            INSERT INTO mesho_pages (url, pincode, page_hash) 
            VALUES (%s, %s, %s)
            """
            local_cursor.execute(insert_query, (link, pincode, page_id))
            local_connect.commit()
            print("inerted data to meesho page")

            # Update product link status
            update_query = f"UPDATE product_links SET status_{pincode} = 'Done' WHERE meesho_pid = %s"
            local_cursor.execute(update_query, (pid[0],))
            local_connect.commit()

        # Close the browser after processing each product
        browser.close()
        playwright.stop()
        # break


# Main function
def main(pincode, start_id, end_id):
    if not os.path.exists('session_storage.json'):
        print("Session storage file is missing.")
        return

    with ExpressVpnApi() as api:
        locations = api.locations
        scraper(pincode, start_id, end_id, api, locations)


if __name__ == "__main__":
    # Database connection setup
    local_connect = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='meesho_page_save'
    )
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
    local_connect.commit()

    # Track the execution time
    start_time = time.time()

    # Start the main function
    main("560001", 1, 2000)

    # Print total execution time
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
