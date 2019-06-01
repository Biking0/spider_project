# coding=utf-8
import logging, zlib, time, base64
import os, json, requests, traceback
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PUSH_URL = 'http://dx.proxy.jiaoan100.com/buddha/addcookie'
GET_URL = 'http://dx.proxy.jiaoan100.com/buddha/getcookie?'


def get_chrome():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def get_firefox():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('-headless')
    # 不加载图片
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    # 禁用webRTC
    firefox_profile.set_preference("media.peerconnection.enabled", False)
    driver = webdriver.Firefox(
        # firefox_options=firefox_options,
        firefox_profile=firefox_profile,
        log_path=os.devnull
    )
    return driver


def get_cookies_by_redis():
    params = {'carrier': 'U2'}
    try:
        res = requests.get(GET_URL, params=params, timeout=30)
        data = json.loads(res.text)
        status = data.get('status')
        if status:
            print(data)
            time.sleep(10)
            return False
        cookies_lib = data.get('cookies')
        cookies = zlib.decompress(base64.b64decode(cookies_lib))
        return json.loads(cookies)
    except:
        time.sleep(10)
        traceback.print_exc()
        return False


def get_cookies(spider=None):
    countries = ['cn', 'fr', 'en', 'cs', 'es', 'ca', 'da', 'de', 'el', 'hu', 'nl', 'pl', 'pt', 'ru', 'it']
    while True:
        if spider and hasattr(spider, 'usechrome') and spider.usechrome:
            flag = int(spider.usechrome)
            if not flag:
                spider.log('get cookies from redis', 20)
                return get_cookies_by_redis()
            driver = get_chrome()
        else:
            driver = get_firefox()
        driver.set_window_position(800, 0)
        driver.set_window_size(100, 100)
        index = randint(0, len(countries) - 1)
        try:
            logging.info('try to get new cookie')
            url = 'https://www.easyjet.com/' + countries[index]
            logging.info(url)
            driver.get(url)
            driver.implicitly_wait(10)  # seconds
            try:
                button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//button[@class="ej-button rounded-corners"]')
                ))
                if button:
                    button.click()
            except Exception as e:
                print(e)
                print('button no find.')
            cookies = driver.get_cookies()
            # print(cookies)
            driver.quit()
            logging.info('Closing Browser')
            if not cookies:
                continue
            return cookies
        except Exception as e:
            logging.error("%s\n exception, try to get again cookie " % e)
            try:
                driver.quit()
            except:
                pass


def add_cookie():
    cookies = get_cookies()
    lib_cookies = zlib.compress(json.dumps(cookies))
    data = {'carrier': 'U2', 'cookies': [base64.b64encode(lib_cookies)]}
    while True:
        try:
            res = requests.post(PUSH_URL, data=json.dumps(data), timeout=30)
            print(res.text)
            status = json.loads(res.text).get('status')
            if not status:
                return
        except:
            time.sleep(3)
            traceback.print_exc()


if __name__ == '__main__':
    while True:
        try:
            add_cookie()
        except Exception as e:
            print(e)

        time.sleep(2)
