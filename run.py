import requests
import time
import json
from selenium import webdriver


# bypass captcha using 2captcha
def bypass_2captcha(captcha2_key, browser):
    iframe = browser.find_element_by_tag_name('iframe')
    if iframe:
        try:
            k_value = iframe.get_attribute('src').split('&')[1].split('=')[1].encode()
        except:
            k_value = iframe.get_attribute('src').split('?')[1].split('=')[1].encode()

    captcha_request_url = "http://2captcha.com/in.php"

    captcha_request_querystring = {
        "key": captcha2_key,
        "method": "userrecaptcha",
        "googlekey": k_value,
        "pageurl": url
    }

    captcha_request_headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "7d3dac64-102f-90ca-32f0-72d6cc73509a"
    }

    captcha_init_response = requests.request("GET", captcha_request_url, headers=captcha_request_headers,
                                             params=captcha_request_querystring)

    captcha_id = captcha_init_response.text.split('|')[1].encode()

    # Wait to GET response from 2 captcha
    time.sleep(20)
    captcha_response_url = "http://2captcha.com/res.php"

    captcha_response_payload = (
        ('key', captcha2_key),
        ('action', 'get'),
        ('id', captcha_id),
    )
    captcha_response_headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "46403502-4cc5-f3b6-252e-4386f11a4fa4"
    }

    captcha_post_response = requests.request("GET", captcha_response_url, headers=captcha_response_headers,
                                             params=captcha_response_payload)
    while (True):
        if captcha_post_response.text.encode() == 'CAPCHA_NOT_READY':
            time.sleep(20)
            captcha_post_response = requests.request("GET", captcha_response_url, headers=captcha_response_headers,
                                                     params=captcha_response_payload)
        else:
            break
    captcha_solution = captcha_post_response.text.split('|')[1].encode()
    print(captcha_post_response.text)
    try:
        captcha_solution_input = browser.find_element_by_id('g-recaptcha-response')
    except:
        captcha_solution_input = browser.find_element_by_id('manual_recaptcha_challenge_field')

    try:
        captcha_submit_button = browser.find_element_by_id('recaptcha_submit')
    except:
        captcha_submit_button = browser.find_element_by_class_name('cf-btn-accept')

    browser.execute_script("arguments[0].style.display = 'block';", captcha_solution_input)
    browser.execute_script("arguments[0].style.display = 'block';", captcha_submit_button)
    captcha_solution_input.click()
    time.sleep(2)
    captcha_solution_input.clear()
    captcha_solution_input.send_keys(captcha_solution)
    captcha_submit_button.click()
    time.sleep(5)
    return browser


def load_website(captcha2_key, url):
    firefoxOptions = webdriver.FirefoxOptions()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("dom.webnotifications.enabled", False)
    profile.update_preferences()

    browser = webdriver.Firefox(firefox_profile=profile, firefox_options=firefoxOptions)
    browser.set_page_load_timeout(300)
    browser.get(url)
    time.sleep(10)

    # keep bypasssing captcha until actual page is loaded
    while (True):
        try:
            browser = bypass_2captcha(captcha2_key, browser)
            browser.find_element_by_xpath("//*[contains(text(), 'Human Test')]")
        except:
            break

    return browser.page_source


def read_config_file(file_path='config.json'):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data['captcha2_api_key'], data['target_url']


if __name__ == "__main__":
    read_config_file()
    captcha2_key, url = read_config_file('config.json')
    print "Using following key and url: ", captcha2_key, url
    page_source = load_website(captcha2_key, url)
    print page_source
