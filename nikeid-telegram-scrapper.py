from _config import *
import time
import bs4
import telegram
import datetime
import gspread
import pytz
import json
import os
import pandas as pd
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located, invisibility_of_element_located
from selenium.webdriver.chrome.options import Options

# SET LOCAL DATETIME
my_date = datetime.datetime.now(pytz.timezone('{}'.format(TZ_NAME)))

# _CONFIG.PY
selenium_server = SELENIUM_SERVER
url_search = URL_SEARCH
shoe_type = SHOE_TYPE
token = TELEGRAM_TOKEN
chat_id = TELEGRAM_CHAT_ID
sheet_id = SHEET_ID
cwd = os.getcwd()

# HELPER FUNCTION
def _get_gc(cwd):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    gc = gspread.authorize(creds)
    return gc


def _get_product_card(menu):
    product_card_tag = [
        "product-card css-1y22mjo css-z5nr6i css-11ziap1 css-zk7jxt css-dpr2cn product-grid__card",
        "product-card css-ucpg4q ncss-col-sm-6 ncss-col-lg-4 va-sm-t product-grid__card",
        "product-card css-pm7x6j css-z5nr6i css-11ziap1 css-zk7jxt css-dpr2cn product-grid__card"
    ]
    check = []
    for tag in product_card_tag:
        product_card = menu.find_all("div", class_=tag)
        if len(product_card) > 0:
            check.append(product_card)
    return check[0]


def _filtering_result(result):
    if result != 0:
        filtered_result = []
        for i in result:
            if i[2] in shoe_type:
                if i[3] == 'Available':
                    filtered_result.append(i)
            else:
                pass
        return filtered_result


def _scroll(driver, timeout):
    # From: https://dev.to/hellomrspaceman/python-selenium-infinite-scrolling-3o12
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


# MAIN FUNCTION
def parsing_result(driver_page_source):
    tanggal = my_date.strftime("%d-%m-%Y")

    menu = bs4.BeautifulSoup(driver_page_source, 'html.parser')
    result = menu.find_all("div", class_="product-grid__items css-yj4gxb css-r6is66 css-1tvazw1 css-1oud6ob")
    if len(result) == 1:
        result_shoes = _get_product_card(menu)
        if len(result) > 0:
            shoes_item = []
            for tag in result_shoes:
                item_name = tag.find('div', class_='product-card__title').text
                item_kind = tag.find('div', class_='product-card__subtitle').text
                available_color = tag.find('div', class_='product-card__product-count').text

                # Price
                if tag.find('div', class_='css-s56yt7'):
                    product_price_after = tag.find('div', class_='css-s56yt7').text
                else:
                    product_price_after = tag.find('div', class_='css-11s12ax').text
                if '\xa0' in product_price_after:
                    product_price_after = product_price_after.replace('\xa0', '')

                # Sale Price
                if tag.find('div', class_='css-31z3ik css-ndethb'):
                    product_price_before = tag.find('div', class_='css-31z3ik css-ndethb').text
                else:
                    product_price_before = '-'
                if '\xa0' in product_price_before:
                    product_price_before = product_price_before.replace('\xa0', '')
    
                # Product URL
                if len(tag.find_all('a', class_='product-card__link-overlay')) == 1:
                    for link in tag.find_all('a', class_='product-card__link-overlay'):
                        url_location = link.get('href')
                else:
                    url_location = None
                url_link = url_location

                # Sold Out Status
                if tag.find('div', class_='product-card__messaging has--message accent--color'):
                    soldout_status = tag.find('div', class_='product-card__messaging has--message accent--color').text
                else:
                    soldout_status = 'Available'
                if soldout_status == '':
                    soldout_status = 'Available'

                details = (tanggal, item_name, item_kind, soldout_status, available_color, product_price_after, product_price_before, url_link )
                shoes_item.append(details)
        else:
            shoes_item = []
    
        return shoes_item


def get_shoes(url):
    options = Options()
    options.page_load_strategy = 'normal'

    if RUN_IN_REMOTE == 'yes':
        driver = webdriver.Remote(
            command_executor=selenium_server,
            desired_capabilities=DesiredCapabilities.FIREFOX,
            options=options
        )
    else:
        # https://github.com/mozilla/geckodriver/releases
        if os.name == 'nt':
            wd = os.getcwd() + '\\geckodriver.exe'
        elif os.name == 'posix':
            wd = os.getcwd() + './geckodriver'
        driver = webdriver.Firefox(
            executable_path=wd,
            desired_capabilities=DesiredCapabilities.FIREFOX,
            options=options
        )

    wait = WebDriverWait(driver, 10)

    driver.get(url)

    _scroll(driver, 5)

    result = parsing_result(driver.page_source)
    result = _filtering_result(result)

    driver.quit()

    return result


def send_channel(shoe, result):
    print(f'[i] Sending {shoe} result to Telegram Channel...')
    bot = telegram.Bot(token=token)
    tanggal_skrg = my_date.strftime("%A, %d-%m-%Y")

    if result != 0:
        bot.sendMessage(chat_id=chat_id, text=f'`{tanggal_skrg} \nSearch Result For {shoe}`', parse_mode=telegram.ParseMode.MARKDOWN)
        for idx, item in enumerate(result):
            text = f'{idx+1}. `{item[1]}` *[{item[3]}]*\n   {item[2]} - {item[4]}\n   Price: *{item[5]}* // *{item[6]}* \n{item[7]}'
            bot.sendMessage(chat_id=chat_id, text=text, disable_notification=True, parse_mode=telegram.ParseMode.MARKDOWN)
            time.sleep(5)
        print("\tTelegram: done")
    else:
        print("\tTelegram: nothing to send")



def save_sheet(shoe, result):
    print(f"[i] Saving {shoe} result to sheet...")
    gc = _get_gc(cwd)
    
    data = pd.DataFrame(result, columns=['date', 'product_name','category', 'status', 'color', 'price', 'price_before', 'link'])
    try:
        ws = gc.open_by_key(sheet_id).worksheet('Sheet1')
        end_flag = ws.find('--END--')
        sr, sc = end_flag.row, end_flag.col
        gd.set_with_dataframe(worksheet=ws, dataframe=data, row=sr, col=sc, include_index=False, include_column_header=False, allow_formulas=False)
        ws.append_row(['--END--'])
        print('\tSheet: Success, {} row(s)'.format(len(data)))
    except:
        print('\tSheet: Failed')
        pass


def main():
    print('>> {}\n[i] Running Nike@Telegram...'.format(my_date.strftime("%A, %d-%m-%Y")))
    
    for shoe, link in url_search.items():
        print(f'[i] Fetching {shoe} products...')
        try:    
            result = get_shoes(link)
            print(f'\t{shoe}: {len(result)} item(s)')
            if len(result) != 0:
                send_channel(shoe, result)
                save_sheet(shoe, result)
                
                print('Done!')
            else:
                print("[i] No item available, skip...")
                pass
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
