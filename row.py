from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from evpn import ExpressVpnApi
from selenium import webdriver
import pymysql
import datetime
import zipfile
import hashlib
import random
import json
import time
import os


def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


def check_seler():
    try:
        review = WebDriverWait(driver=driver, timeout=3).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
        ActionChains(driver).scroll_to_element(review).perform()
        driver.execute_script("arguments[0].scrollIntoView();", review)
        return driver
    except InvalidSessionIdException as e:
        print("Session expired. Please restart the driver.", e)
        driver = create_session()
        return driver
    except Exception:
        pass


def create_session():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option(name="excludeSwitches", value=["enable-automation"])
    options.add_experimental_option(name='useAutomationExtension', value=False)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    main_url = 'https://www.meesho.com'
    driver.get(main_url)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    with open('session_storage.json', 'r') as f:
        cookies = json.loads(f.read())

    for cookie in cookies['cookies']:
        driver.add_cookie(cookie)
    driver.refresh()
    return driver


# ua = UserAgent()
if __name__ == '__main__':
    api = ExpressVpnApi()
    api.connect(9)  # Connect to Chicago VPN (USA)
    time.sleep(5)
    print('VPN Connected...!' if api.is_connected else 'VPN not Connected!!')

    # options = webdriver.ChromeOptions()
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option(name="excludeSwitches", value=["enable-automation"])
    # options.add_experimental_option(name='useAutomationExtension', value=False)
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    # options.add_argument(f"user-agent={user_agent}")
    # driver = webdriver.Chrome(options=options)
    # driver.maximize_window()
    # main_url = 'https://www.meesho.com'
    # driver.get(main_url)
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver = create_session()

    local_connect = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='meesho_page_save'
    )
    local_cursor = local_connect.cursor()
    today_date = datetime.datetime.now().strftime("%d%m%Y")
    pages_tablename = f'pages_{today_date}'
    local_cursor.execute(f'''CREATE TABLE IF NOT EXISTS {pages_tablename} (id int AUTO_INCREMENT PRIMARY KEY,
    url varchar(1000),
    pincode varchar(50),
    page_hash varchar(1000),
    status varchar(100))''')
    local_connect.commit()

    # main_url = 'https://www.meesho.com/?srsltid=AfmBOopbEEo_Uie8c9cnbQQQRlxyQuK0r9EjrTI2ac0aDz6RkOmwZX81&source=profile&entry=header&screen=HP'

    # with open('session_storage.json', 'r') as f:
    #     cookies = json.loads(f.read())
    #
    # for cookie in cookies['cookies']:
    #     driver.add_cookie(cookie)
    # driver.refresh()

    path = 1

    links_available = True

    pincode = '560001'
    scraped_data_count = 1
    starting_position = 0
    pos = 1

    # while links_available:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # last_length = len(product_list)
    # for link in product_list[starting_position:]:
    query = f"SELECT Product_Url_MEESHO FROM template_20241017_distinct WHERE `status` != 'Done' AND status_{pincode}_ != 'Done' AND id BETWEEN 1 AND 16000"
    local_cursor.execute(query)
    rows = local_cursor.fetchall()
    print(f'{len(rows)} urls fetched...')
    co_p = 1
    # for pos, link_ in enumerate(rows):
    for pos, link_ in enumerate(reversed(rows)):
        link = link_[0]
        # while True:
        # try:
        print('\n')
        local_cursor.execute(query=f"SELECT * FROM {pages_tablename} WHERE url = %s AND status = %s", args=(link, 'done'))

        local_connect.commit()
        print(link)
        pos += 1
        if local_cursor.fetchone():
            print('url already scraped...', '\n')
            continue

        # driver.execute_script(f'''window.open("{link}","_self");''')
        #
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            driver.execute_script(f'''window.open("{link}","_self");''')

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver=driver, timeout=1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[contains(text(), "This product is out of stock")]')))
            continue
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except Exception as e:
            pass

        try:
            review = WebDriverWait(driver=driver, timeout=1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//h1[contains(text(), "Access Denied")]')))
            if 'access denied' in review.text.lower():
                print('access denied')
                continue
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except:
            pass

        # try:
        #     review = WebDriverWait(driver=driver, timeout=3).until(
        #         EC.presence_of_element_located(
        #             (By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
        #     ActionChains(driver).scroll_to_element(review).perform()
        #     driver.execute_script("arguments[0].scrollIntoView();", review)
        # except InvalidSessionIdException as e:
        #     print("Session expired. Please restart the driver.", e)
        #     driver = create_session()
        #     continue
        # except Exception:
        #     pass
        driver = check_seler()

        try:
            pin_input = WebDriverWait(driver=driver, timeout=1).until(
                EC.visibility_of_element_located((By.XPATH, '//input[@id="pin"]')))

            if pincode == pin_input.get_attribute('value'):
                print(pin_input.get_attribute('value'))
            else:
                for _ in range(int(pin_input.get_attribute('maxlength'))):
                    pin_input.send_keys(Keys.BACKSPACE)
                    small_random_waite()
                pin_input.send_keys(pincode)
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except Exception as e:
            print('Input is not available')
            continue

        try:
            element = WebDriverWait(driver=driver, timeout=2).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="pin"]//button')))
            ActionChains(driver).click_and_hold(element).click(element).perform()
            time.sleep(2)
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except Exception as e:
            print('Error in pincode button...', e)
        try:
            WebDriverWait(driver=driver, timeout=1).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[2]')))
            print("error alert visible")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except Exception as e:
            print('No error alert')

        try:
            review = WebDriverWait(driver=driver, timeout=5).until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "ShopCardstyled__ShopName")]')))
            ActionChains(driver).scroll_to_element(review).perform()
            driver.execute_script("arguments[0].scrollIntoView();", review)
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except Exception as e:
            print('Error while scrolliung review', e)

        try:
            text_data = WebDriverWait(driver=driver, timeout=2).until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@class,"sc-eDvSVe dCivsU") and not(contains(text(), "Dispatch"))]')))
            print(text_data.text)
            if 'Enter Pincode for Estimated Delivery Date' in text_data.text:
                driver.refresh()
                driver = create_session()

                # print('Enter Pincode for Estimated Delivery Date in text_data.text')
                # page_id = f'{link.split('/')[-1]}_{pincode}'

                # insert_query = """
                #     INSERT INTO pages (url, pincode, page_hash, status)
                #     VALUES (%s, %s, %s, %s)
                # """
                # local_cursor.execute(query=insert_query, args=(link, pincode, page_id, 'pending'))
                #
                # local_connect.commit()
                continue
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except:
            pass
        try:
            page_id = f'{link.split('/')[-1]}_{pincode}'
            with zipfile.ZipFile(fr'../shipping_page/{page_id}' + '.zip', 'w',
                                 zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(zinfo_or_arcname=f'HTML_{page_id}.html', data=driver.page_source)
            insert_query = f"""
                            INSERT INTO {pages_tablename} (url, pincode, page_hash, status)
                            VALUES (%s, %s, %s, %s)
                            """
            local_cursor.execute(query=insert_query, args=(link, pincode, page_id, 'done'))

            # insert_query = f"""INSERT INTO pages(url, pincode, page_hash, status) VALUES ('{link}', '{pincode}', '{page_id}', 'done')"""
            # local_cursor.execute(insert_query)
            local_connect.commit()

            update_query = f"""UPDATE template_20241017_distinct SET status_560001_ = 'done' WHERE product_url_meesho = %s"""
            local_cursor.execute(update_query, args=link)
            local_connect.commit()
            scraped_data_count += 1
            # except Exception as e:
            #     print("Main Exp", e)
        except InvalidSessionIdException as e:
            print("Session expired. Please restart the driver.", e)
            driver = create_session()
            continue
        except Exception as e:
            print('Error while scraping', e)
    if api.is_connected:
        api.close()
