# coding=utf-8
import time, logging, json, traceback
from selenium import webdriver
import random
from selenium.webdriver.common.proxy import *

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# logging基本配置


logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def gen_cookies():  # 没有代理

    try:
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--proxy-server=127.0.0.1:8080')
        chrome_options.add_argument("--ignore-certificate-errors")
        # chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver.set_window_position(0, 0)
        # driver.set_window_size(100, 100)
        # 70s超时处理
        driver.set_page_load_timeout(100)
        logging.info('try to get new cookie')

        # driver.get('https://www.jetstar.com/au/en/home')
        # driver.get('https://www.jetstar.com/au/en/home?origin=SYD&destination=NRT&flight-type=1&selected-departure-date=01-02-2019&adult=1&flexible=1&currency=AUD')
        start_time = time.time()
        driver.get(
            'https://www.jetstar.com/au/en/home?origin=SYD&destination=BNK&flight-type=1&selected-departure-date=01-04-2019&adult=1&flexible=1&currency=AUD')

        try:
            # 模拟用户行为，随机休息，随机点击
            move = driver.find_element_by_class_name('cal-instructional-text__headline')
            move1 = driver.find_element_by_class_name('cal-summary__disclaimer')
            move2 = driver.find_element_by_class_name('cal-summary')

            move_list = [move, move1, move2]
            webdriver.ActionChains(driver).move_by_offset(random.randint(200, 600), random.randint(200, 600)).perform()
            webdriver.ActionChains(driver).move_by_offset(random.randint(200, 600), random.randint(200, 600)).perform()
            webdriver.ActionChains(driver).move_to_element(move_list[random.randint(0, 2)]).perform()
            time.sleep(random.randint(0, 5))
            webdriver.ActionChains(driver).move_by_offset(random.randint(200, 600), random.randint(200, 600)).perform()
            webdriver.ActionChains(driver).move_to_element(move_list[random.randint(0, 2)]).perform()
            webdriver.ActionChains(driver).move_by_offset(random.randint(200, 600), random.randint(200, 600)).perform()

            # time.sleep(random.randint(0, 5))
            # webdriver.ActionChains(driver).move_to_element(random.randint(0,2)).perform()
            # webdriver.ActionChains(driver).move_to_element(move1).perform()

        except Exception as e:
            print(e)
            driver.quit()
            time.sleep(5)
            return get_cookies()

        # time.sleep(1000)

        # # 显性等待，定位器
        # locator = (By.XPATH, '//button[contains(@type,"submit")]')
        # WebDriverWait(driver, 100, 0.1).until(EC.presence_of_element_located(locator))
        # result_locator = (By.XPATH, '//a[@class="page-header__link js-sks-redirect"]')
        # WebDriverWait(driver, 100, 0.1).until(EC.presence_of_element_located(result_locator))

        driver.find_element_by_xpath("//button[contains(@type,'submit')]").click()

        cookies = driver.get_cookies()
        if not cookies:
            driver.quit()
            time.sleep(5)
            return get_cookies()
        driver.quit()
        print('######### use time: ', time.time() - start_time)
        # logging.info('got new cookies')
        # return (cookies, ip_port)
        return cookies
    except Exception as e:
        logging.error("%s\n exception, try to get again cookie " % e)
        print(traceback.print_exc())
        try:
            driver.quit()
            time.sleep(5)
        except Exception as e:
            print(e)
            pass
        time.sleep(5)
        return get_cookies()


def get_cookies():
    cookies = gen_cookies()
    dict_cookies = {}
    # print(cookies)
    try:
        for cookie in cookies:
            # dict_cookies[cookie.get('name').encode('ascii')] = cookie.get('value').encode('ascii')
            dict_cookies[cookie.get('name')] = cookie.get('value')
        content = json.dumps(dict_cookies)
        return content
    except:
        return get_cookies()

if __name__ == '__main__':
    print(get_cookies())
