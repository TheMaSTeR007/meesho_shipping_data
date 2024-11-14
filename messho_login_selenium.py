import json
import time
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from evpn import ExpressVpnApi
from selenium import webdriver


def random_waite():
    random_time_list = [1, 2, 3]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


def small_random_waite():
    random_time_list = [0.2, 0.3, 0.4, 0.5]
    ran_tim = random.choice(random_time_list)
    time.sleep(ran_tim)


def session_creation():
    main_url = 'https://www.meesho.com/auth/'

    # options = uc.ChromeOptions()
    # driver = uc.Chrome(options=options)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    driver.get(main_url)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def login(driver, phone_number, name):
    random_waite()

    try:
        set_number_in_input = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div/div[2]/div/div/div[2]/input')))
        # no = '7405494246'
        # no = '6354786744'
        for i in phone_number:
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
        otp = input(f"{name} {phone_number} Enter OTP : ")
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

    time.sleep(5)

    cookies = driver.get_cookies()
    today_date = datetime.now().strftime("%Y%m%d")
    session_storage_filename = fr"../cookies/{phone_number}_{today_date}_session_storage.json"
    with open(session_storage_filename, 'w', encoding='utf-8') as file:
        file.write(json.dumps(cookies))  # Save session cookies if login was successful
    print("Session cookies saved successfully.")


if __name__ == "__main__":
    start_time = time.time()
    with ExpressVpnApi() as api:
        locations = api.locations
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

        # mobile_number1 = mobile_num_dict['bhargav'], 'bhargav'
        # mobile_number2 = mobile_num_dict['pritesh'], 'pritesh'
        # mobile_number3 = mobile_num_dict['surya'], 'surya'
        # mobile_number4 = mobile_num_dict['deekshant'], 'deekshant'

        mobile_number1 = mobile_num_dict['sim1'], 'sim1'
        mobile_number2 = mobile_num_dict['sim2'], 'sim2'
        mobile_number3 = mobile_num_dict['sim3'], 'sim3'
        mobile_number4 = mobile_num_dict['sim4'], 'sim4'

        phone_number_list = [mobile_number1, mobile_number2, mobile_number3, mobile_number4]
        # for phone_number in phone_number_list:
        driver1 = session_creation()
        driver2 = session_creation()
        driver3 = session_creation()
        driver4 = session_creation()
        login(driver1, phone_number_list[0][0], name=phone_number_list[0][1])
        login(driver2, phone_number_list[1][0], name=phone_number_list[1][1])
        login(driver3, phone_number_list[2][0], name=phone_number_list[2][1])
        login(driver4, phone_number_list[3][0], name=phone_number_list[3][1])

    end_time = time.time()

    print("Time :", end_time - start_time)
