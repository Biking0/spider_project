# coding=utf-8

from selenium import webdriver
import traceback

import requests, time

url = 'https://book.evaair.com/iframe.html'
url_test = 'https://www.baidu.com'

try:
    chrome_options = webdriver.ChromeOptions()
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--proxy-server=127.0.0.1:1080')
    # chrome_options.add_argument("--ignore-certificate-errors")
    # # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome()
    # driver.set_window_position(0, 0)
    # driver.set_window_size(100, 100)
    # 70s超时处理
    # driver.set_page_load_timeout(100)
    # logging.info('try to get new cookie')

    # driver.get('https://www.jetstar.com/au/en/home')
    # driver.get('https://www.jetstar.com/au/en/home?origin=SYD&destination=NRT&flight-type=1&selected-departure-date=01-02-2019&adult=1&flexible=1&currency=AUD')
    # start_time = time.time()
    driver.get(url)
    time.sleep(20)
    cookies=driver.get_cookies()
    print(driver.get_cookies())

    for i in cookies:
        print(i)


except Exception as e:
    print(traceback.print_exc())
    print(e)
    print(123)
