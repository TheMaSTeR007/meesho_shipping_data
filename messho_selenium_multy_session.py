import time
from datetime import datetime
from evpn import ExpressVpnApi
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, os
import pymysql
import zipfile
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import random
import hashlib

random_time_list = [1, 2, 3]


def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


connect = pymysql.connect(
    host='localhost',
    user='root',
    password='actowiz',
    database='meesho_page_save'
)
cursor = connect.cursor()

local_connect = pymysql.connect(
    host='localhost',
    user='root',
    password='actowiz',
    database='meesho_page_save'
)
local_cursor = local_connect.cursor()

today_date = datetime.now().strftime("%Y%m%d")
pages_tablename = f'pages_{today_date}'

local_cursor.execute(f'''CREATE TABLE IF NOT EXISTS {pages_tablename} (id int AUTO_INCREMENT PRIMARY KEY,
url varchar(1000),
pincode varchar(50),
page_hash varchar(1000),
status varchar(100))''')
local_connect.commit()

main_url = 'https://www.meesho.com/?srsltid=AfmBOopbEEo_Uie8c9cnbQQQRlxyQuK0r9EjrTI2ac0aDz6RkOmwZX81&source=profile&entry=header&screen=HP'

# working for some request


# path = 1


pincode = '560001'
scraped_data_count = 1
starting_position = 0
pos = 1


def create_session(file_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    driver.get(main_url)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    with open(file_name, 'r') as f:
        cookies = json.loads(f.read())

    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    return driver


def scrapping(link, driver):
    global scraped_data_count
    try:
        print('\n')

        local_cursor.execute(f"SELECT * FROM {pages_tablename} WHERE url = %s AND status = %s", (link, 'done'))
        local_connect.commit()
        print(link)
        if local_cursor.fetchone():
            print('url already scraped...', '\n')
            return

        driver.execute_script(f'''window.open("{link}","_self");''')

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[contains(text(), "This product is out of stock")]')))
            return
        except Exception as e:
            pass

        try:
            review = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//h1[contains(text(), "Access Denied")]')))
            if 'access denied' in review.text.lower():
                print('access denied')
                return
        except:
            pass

        review = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
        ActionChains(driver).scroll_to_element(review).perform()
        driver.execute_script("arguments[0].scrollIntoView();", review)

        try:
            pin_input = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, '//input[@id="pin"]')))

            if pincode == pin_input.get_attribute('value'):
                print(pin_input.get_attribute('value'))
            else:
                for _ in range(int(pin_input.get_attribute('maxlength'))):
                    pin_input.send_keys(Keys.BACKSPACE)
                    small_random_waite()
                pin_input.send_keys(pincode)
        except Exception as e:
            print('Input is not available')
            return

        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pin"]//button')))
        ActionChains(driver).click_and_hold(element).click(element).perform()

        time.sleep(2)
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[2]')))
            print("error alert visible")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return
        except Exception as e:
            print('No error alert')

        review = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
        ActionChains(driver).scroll_to_element(review).perform()
        driver.execute_script("arguments[0].scrollIntoView();", review)

        # ActionChains(driver).click_and_hold(review).perform()
        try:
            text_data = WebDriverWait(driver, 2).until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]')))
            print(text_data.text)
            if 'Enter Pincode for Estimated Delivery Date' in text_data.text:
                # change_vpn(api, locations)
                # page_id = hashlib.sha256((str(driver.current_url).split('/')[-1] + f'_{pincode}').encode()).hexdigest()
                # local_cursor.execute(f"SELECT * FROM pages WHERE url = %s AND status = %s", (link, 'pending'))
                # local_connect.commit()
                # if local_cursor.fetchone():
                #     pass
                # else:
                #     insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
                #     local_cursor.execute(insert_query, (driver.current_url, pincode, page_id, 'done'))
                #     local_connect.commit()
                return
        except:
            pass

        page_id = link.split('/')[-1] + f'_{pincode}'

        with zipfile.ZipFile(fr'../meesho/shipping_page/{page_id}' + '.zip', 'w',
                             zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'HTML_{page_id}.html', driver.page_source)
        insert_query = f"""INSERT INTO {pages_tablename}(url, pincode, page_hash, status) VALUES (%s, %s, %s, %s)"""
        local_cursor.execute(insert_query, (link, pincode, page_id, 'done'))
        local_connect.commit()
        update_query = f"""UPDATE template_20241017_distinct SET status_560001 = 'done' WHERE Product_Url_MEESHO = %s"""
        cursor.execute(update_query, (link,))
        connect.commit()

        scraped_data_count += 1


    except Exception as e:
        print("Main Exp", e)


api = ExpressVpnApi()
api.connect(9)  # Connect to Chicago VPN (USA)
time.sleep(5)
print('VPN Connected...!' if api.is_connected else 'VPN not Connected!!')

#
# while links_available:
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     last_length = len(product_list)
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
    'sim1': '9316308731',
    'sim2': '6351426664',
    'sim3': '6354618122',
    'sim4': '9316824823',

}

mobile_number1 = mobile_num_dict['sim1']
mobile_number2 = mobile_num_dict['sim2']
mobile_number3 = mobile_num_dict['sim3']
mobile_number4 = mobile_num_dict['sim4']

session_storage_filename1 = fr"../cookies/{mobile_number1}_{today_date}_session_storage.json"
session_storage_filename2 = fr"../cookies/{mobile_number2}_{today_date}_session_storage.json"
session_storage_filename3 = fr"../cookies/{mobile_number3}_{today_date}_session_storage.json"
session_storage_filename4 = fr"../cookies/{mobile_number4}_{today_date}_session_storage.json"

driver1 = create_session(session_storage_filename1)
driver2 = create_session(session_storage_filename2)
driver3 = create_session(session_storage_filename3)
driver4 = create_session(session_storage_filename4)

query = f"SELECT Product_Url_MEESHO FROM template_20241017_distinct WHERE `status` != 'Done' AND status_{pincode} != 'Done' AND id BETWEEN 1 AND 16000"
cursor.execute(query)
rows = cursor.fetchall()
co_p = 1
for pos, link_ in enumerate(rows):
    link = link_[0]

    if co_p == 1:
        scrapping(link, driver1)
    if co_p == 2:
        scrapping(link, driver2)
    if co_p == 3:
        scrapping(link, driver3)
    if co_p == 4:
        scrapping(link, driver4)
        co_p = 0
    co_p += 1

if api.is_connected:
    api.close()
    # random_waite()
    # driver.execute_script("arguments[0].scrollIntoView();", product_list[-1])
    # random_waite()
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # driver.execute_script("window.scrollTo(0, 400);")
    # random_waite()
    # product_list = WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located(
    #         (By.XPATH, f'//*[@id="__next"]/div[3]/div[2]/div/div/div[2]/div/div[2]/div[1]/div/div/a')))
    # new_length = len(product_list)
    # print(last_length, '-', new_length)
    # starting_position = last_length + 1
    # if last_length == new_length:
    #     break
