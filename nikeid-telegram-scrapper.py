from _config import *
import bs4
import requests
import telegram
import datetime
import gspread
import pytz
import json
import os
import pandas as pd
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials
from requests.auth import HTTPProxyAuth

# SET LOCAL DATETIME: GMT +7
my_date = datetime.datetime.now(pytz.timezone('{}'.format(TZ_NAME)))

# _CONFIG.PY
url_search = URL_SEARCH
token = TELEGRAM_TOKEN
chat_id = TELEGRAM_CHAT_ID
sheet_id = SHEET_ID
cwd = os.getcwd()

# FUNCTION
def parsingSearchResult_v1(getResultPage):
    #now = datetime.date.today()# - datetime.timedelta(days=1)
    tanggal = my_date.strftime("%d-%m-%Y")
    
    menu = bs4.BeautifulSoup(getResultPage.text, 'html.parser')
    result = menu.find_all("div", class_="product-grid__items ta-lg-l pb9-sm pb0-lg css-1oud6ob")
    if len(result) == 1:
        result_shoes = menu.find_all("div", class_="product-card css-ucpg4q ncss-col-sm-6 ncss-col-lg-4 va-sm-t product-grid__card")
        if len(result) > 0:
            shoes_item = []
            for tag in result_shoes:
                item_name = tag.find('div', class_='product-card__title').text
                item_kind = tag.find('div', class_='product-card__subtitle').text
                available_color = tag.find('div', class_='product-card__product-count').text
    
                # Price
                if tag.find('div', class_='css-i260wg'):
                    product_price_after = tag.find('div', class_='css-i260wg').text
                else:
                    product_price_after = tag.find('div', class_='css-b9fpep').text
    
                # Product URL
                if len(tag.find_all('a', class_='product-card__link-overlay')) == 1:
                    for link in tag.find_all('a', class_='product-card__link-overlay'):
                        url_location = link.get('href')
                else:
                    url_location = None
                nike_site = 'https://www.nike.com'
                url_link = '{0}{1}'.format(nike_site, url_location)
    
                # Sale Price
                if tag.find('div', class_='css-31z3ik css-ndethb'):
                    product_price_before = tag.find('div', class_='css-31z3ik css-ndethb').text
                else:
                    product_price_before = '-'
    
                # Sold Out Status
                if tag.find('div', class_='product-card__messaging has--message accent--color'):
                    soldout_status = tag.find('div', class_='product-card__messaging has--message accent--color').text
                else:
                    soldout_status = 'Available'
    
                details = (tanggal, item_name, item_kind, soldout_status, available_color, product_price_after, product_price_before, url_link )
                shoes_item.append(details)
        else:
            shoes_item = []
    
    return shoes_item
    

def get_detail_jordan1h():
    #getResultPage = requests.get('https://www.nike.com/id/w?q=air%20jordan%20high&vst=air%20jordan%20high')
    s = requests.Session()

    if PROXY_HTTP is not None and PROXY_HTTP != '':
        s.trust_env=False
        s.proxies = {"http": PROXY_HTTP,"https": PROXY_HTTPS}
        if PROXY_USER is not None and PROXY_USER !='':
            s.auth = HTTPProxyAuth(PROXY_USER, PROXY_PWD)
    #getResultPage = requests.get(url_search, proxies=proxies)
    getResultPage = s.get(url_search)
    getResultPage.raise_for_status()
    
    try:
        hasil = parsingSearchResult_v1(getResultPage)
        return hasil
    except Exception as e:
        print(f"\tJordan 1 High: {e}")


def filtering_result(list_of_result):
    if list_of_result != 0:
        fil_result = []
        for i in list_of_result:
            if i[2] == 'Women\'s Shoe' or i[2] == 'Men\'s Shoe':
                if i[3] == 'Available':
                    fil_result.append(i)
            else:
                pass
        return fil_result


def get_gc(cwd):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('{}/client_secret.json'.format(cwd), scope)
    gc = gspread.authorize(creds)
    return gc


# def anti_join(list_of_result):


def send_channel(list_of_result):
    bot = telegram.Bot(token=token)
    #now = datetime.date.today()
    tanggal_skrg = my_date.strftime("%A, %d-%m-%Y")

    if list_of_result != 0:
        #print("{}\nSearch Result For Air Jordan 1 High".format(tanggal_skrg))
        bot.sendMessage(chat_id=chat_id, text='`{} \nSearch Result For Air Jordan 1 High`'.format(tanggal_skrg), parse_mode=telegram.ParseMode.MARKDOWN)
        for idx, item in enumerate(list_of_result):
            text = '{7}. `{0}` *[{1}]*\n   {2} - {3}\n   Price: *{4}* // _{5}_\n{6}'.format(item[1], item[3], item[2], item[4], item[5], item[6], item[7], idx+1)
            bot.sendMessage(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        print("\tTelegram: done")
    else:
        print("\tTelegram: nothing to send")



def save_sheet(list_of_result):
    print("Saving to sheet...")
    gc = get_gc(cwd)
    
    data = pd.DataFrame(list_of_result, columns=['date', 'product_name','category', 'status', 'color', 'price', 'price_before', 'link'])
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
    print('{}\nRunning Nike@Telegram...'.format(my_date.strftime("%A, %d-%m-%Y")))
    kirim_telegram = get_detail_jordan1h()
    kirim_telegram = filtering_result(kirim_telegram)
    # tambahin untuk compare sheet dengan list_of_result

    print('\tResult: {} item(s)'.format(len(kirim_telegram)))
    if len(kirim_telegram) != 0:
        send_channel(kirim_telegram)
        save_sheet(kirim_telegram)
        print('DONE!')
    else:
        print("No item available, exiting...")
        quit()

if __name__ == '__main__':
    main()


