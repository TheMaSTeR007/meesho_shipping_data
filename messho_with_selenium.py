import time
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
import pickle
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import random
import hashlib
import zipfile
from evpn import ExpressVpnApi

random_time_list = [1, 2, 3]


def random_waite():
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


# ua = UserAgent()

# ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
# options = uc.ChromeOptions()
# options.add_argument('--disable-popup-blocking')
# options = webdriver.ChromeOptions()
# options.add_argument(f"user-agent={ua.random}")
# driver = webdriver.Chrome(options=options)

# options = webdriver.ChromeOptions()

# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
# options.add_argument(f"user-agent={user_agent}")
# options.add_argument(fr"user-data-dir=C:\Users\Admin\AppData\Local\Google\Chrome\User Data\Profile 1")
# options.add_argument("--remote-debugging-port=9222")
# driver = webdriver.Chrome(options=options)

# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
# options.add_argument(f"user-agent={user_agent}")
# options = uc.ChromeOptions()
# driver = uc.Chrome(options=options)

# driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# options = uc.ChromeOptions()
# driver = uc.Chrome()

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

local_cursor.execute('''CREATE TABLE IF NOT EXISTS pages (id int AUTO_INCREMENT PRIMARY KEY,
                    url varchar(1000),
                    pincode varchar(10),
                    page_hash varchar(1000),
                    status varchar(100))''')
local_connect.commit()


def change_vpn(api, locations):
    # get available locations
    loc = random.choice(locations)
    api.connect(loc["id"])
    time.sleep(5)


def scraper(pincode, start_id, end_id):
    cookies_dic = {}
    scraped_data_count = 1
    for file in os.listdir(os.getcwd()):
        if file.endswith('.json'):
            # print(file)
            with open(file, 'r') as f:
                data = f.read()
                file_name = file.split('.')[0]
                cookie = json.loads(data)
                cookies_dic[file_name] = cookie

    # print(cookies_dic)
    # for i in range(1, 21):
    #     key, value = random.choice(list(cookies_dic.items()))
    #     print(f"Random key-value pair: {key}: {value}")

    query = f"SELECT Product_Url_MEESHO FROM template_20241017 WHERE `status` != 'Done' AND status_{pincode} != 'Done' AND id BETWEEN {start_id} AND {end_id}"
    cursor.execute(query)
    rows = cursor.fetchall()

    options = webdriver.ChromeOptions()

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.maximize_window()

    # driver.delete_all_cookies()
    # driver.get(link)
    co_p = 0
    key, value = list(cookies_dic.items())[co_p]
    co_p += 1



    for pos, pid in enumerate(rows):

        # link = f'https://www.meesho.com/s/p/{pid[0]}'
        link = pid[0]
        local_cursor.execute(f"SELECT * FROM pages WHERE url = '{link}' and status = 'done'")
        local_connect.commit()

        # key, value = random.choice(list(cookies_dic.items()))

        print(f'\n{pos} --- {key} --- {link}')
        if local_cursor.fetchone():
            print('URL already scraped')
            continue

        # driver.delete_all_cookies()
        driver.get(link)
        if co_p == 1:
            for cookie in value['cookies']:
                driver.add_cookie(cookie)
            driver.refresh()
            co_p += 1
        # for cookie in value['cookies']:
        #     driver.add_cookie(cookie)
        #
        # driver.refresh()

        try:
            review = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//h1[contains(text(), "Access Denied")]')))
            if 'access denied' in review.text.lower():
                print('access denied')
                change_vpn(api, locations)
                page_id = hashlib.sha256((driver.current_url + f'_{pincode}').encode()).hexdigest()
                insert_query = f"""INSERT INTO meesho_table(url, pincode, page_hash, status) VALUES ('{driver.current_url}', '{pincode}', '{page_id}', 'pending')"""
                local_cursor.execute(insert_query)
                local_connect.commit()
                # driver.quit()
                continue
        except:
            pass

        # random_waite()
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        review = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
        driver.execute_script("arguments[0].scrollIntoView();", review)

        # random_waite()
        try:
            pin_input = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//input[@id="pin"]')))

            if pincode == pin_input.get_attribute('value'):
                print(pin_input.get_attribute('value'))
            else:
                # driver.execute_script("arguments[0].value = '';", pin_input)
                # pin_input.clear()
                # pin_input.send_keys('')
                for _ in range(int(pin_input.get_attribute('maxlength'))):
                    pin_input.send_keys(Keys.BACKSPACE)
                    small_random_waite()
                pin_input.send_keys(pincode)
        except Exception as e:
            print('Input is not available')
            page_id = hashlib.sha256((driver.current_url + f'_{pincode}').encode()).hexdigest()
            insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES ('{driver.current_url}', '{pincode}', '{page_id}', 'pending')"""
            local_cursor.execute(insert_query)
            local_connect.commit()
            continue

        time.sleep(2)
        element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="pin"]//button')))
        # ActionChains(driver).click_and_hold(element).click(element).perform()
        element.click()

        # try:
        #     WebDriverWait(driver, 2).until(
        #         EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div/div')))
        #     print("alert visible")
        # except Exception as e:
        #     print('No alert', e)

        review = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
        # ActionChains(driver).scroll_to_element(review).perform()
        driver.execute_script("arguments[0].scrollIntoView();", review)

        # ActionChains(driver).click_and_hold(review).perform()
        try:
            text_data = WebDriverWait(driver, 2).until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]')))
            print(text_data.text)
            if 'Enter Pincode for Estimated Delivery Date' in text_data.text:
                change_vpn(api, locations)
                page_id = hashlib.sha256((driver.current_url + f'_{pincode}').encode()).hexdigest()
                insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES ('{driver.current_url}', '{pincode}', '{page_id}', 'pending')"""
                local_cursor.execute(insert_query)
                local_connect.commit()
                # driver.quit()
                continue
        except:
            pass

        page_id = hashlib.sha256((driver.current_url + f'_{pincode}').encode()).hexdigest()

        with zipfile.ZipFile(fr'../shipping_page/{page_id}' + '.zip', 'w',
                             zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'HTML_{page_id}.html', driver.page_source)

        insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES ('{driver.current_url}', '{pincode}', '{page_id}', 'done')"""
        local_cursor.execute(insert_query)
        local_connect.commit()
        random_waite()
        scraped_data_count += 1
        # driver.quit()


def login():
    main_url = 'https://www.meesho.com/auth/'

    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.get(main_url)

    # driver.start_client()
    # hover_to_profile = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div[1]/div/div[3]/div[7]')))
    # ActionChains(driver).click_and_hold(hover_to_profile).perform()
    #
    # random_waite()
    #
    # try:
    #     click_on_signup = WebDriverWait(driver, 1).until(
    #         EC.presence_of_element_located(
    #             (By.XPATH, '//*[@id="__next"]/div[2]/div[1]/div/div[3]/div[7]/div/div/button')))
    #     ActionChains(driver).click(click_on_signup).perform()
    # except:
    #     pass
    #

    random_waite()

    try:
        set_number_in_input = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div/div[2]/div/div/div[2]/input')))
        # no = '7405494246'
        # no = '6354786744'
        no = '9879361219'
        for i in no:
            set_number_in_input.send_keys(i)
            small_random_waite()
    except:
        pass

    random_waite()

    try:
        send_otp = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div/div[2]/div/button')))
        ActionChains(driver).click(send_otp).perform()
    except:
        pass

    try:
        otp = input("Enter OTP : ")
        print(otp)
    except:
        otp = ''

    try:
        for pos, input_tag in enumerate(WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/div[3]/div/div[2]/div/div/input')))):
            input_tag.send_keys(str(otp)[pos])
            random_waite()
    except:
        pass

    try:
        verify_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div[2]/div/button')
        ActionChains(driver).move_to_element(verify_btn).click(verify_btn).perform()

    except:
        pass


def main(pincode, start_id, end_id):
    if os.path.exists('session_storage.json'):
        scraper(pincode, start_id, end_id)
    else:
        login()


if __name__ == "__main__":
    start_time = time.time()
    with ExpressVpnApi() as api:
        locations = api.locations
        main("560001", 1, 15000)

    end_time = time.time()

    print("Time :", end_time - start_time)
