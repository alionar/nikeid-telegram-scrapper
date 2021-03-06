# nikeid-telegram-scrapper
Get daily reminder about certain Nike shoes stock on [Nike ID Store](https://www.nike.com/id/w?q=&vst=) via Telegram Channel

## What to Prepare First?
1. Install Python => 3.6
2. Install dependencies `python3 -m pip install -r  requirements.txt`
3. Create Telegram bot to get token. [How?](https://core.telegram.org/bots#6-botfather).
4. Make new Telegram channel and add your bot to channel. [How?](https://telegram.org/faq_channels#q-what-39s-a-channel)
5. Get your Telegram channel Chat ID. [How?](https://github.com/GabrielRF/telegram-id)
6. Get Service Account on GCP and save it as `client_secret.json` in this repo folder. [How?](https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount)
7. Enable Google Drive API and Sheet API for your project account on GCP. [How?](https://support.google.com/googleapi/answer/6158841?hl=en)
8. Create [New Google Spreadsheet](https://docs.google.com/spreadsheets/u/0/) and delete all row except first one and then edit cell A1 and insert `--END--`.
9. Copy the `client_email` inside `client_secret.json`. Back in your spreadsheet, click the Share button in the top right, and paste the `client_email` value into the People field to give it edit rights. Hit Send.
10. Get `sheet_id` from spreadsheet that you already made before. [How?](https://developers.google.com/sheets/api/guides/concepts#spreadsheet_id)
11. Open and change variable value in `_config.py`.
  ```
 URL_SEARCH = 'https://www.nike.com/id/w/jordan-1-lifestyle-high-top-shoes-13jrmz4fokyz6lqy0zy7ok'
 TELEGRAM_TOKEN = '<YOUR_TELEGRAM_BOT_TOKEN>'
 TELEGRAM_CHAT_ID = <YOUR_TELEGRAM_CHANNEL_CHAT_ID> #integer
 SHEET_ID  = '<YOUR_SPREADSHEET_ID>'
 TZ_NAME = '<YOUR_TIMEZONE>'
 PROXY_HTTP = ''
 PROXY_HTTPS = ''
 PROXY_USER = ''
 PROXY_PWD = ''
  ```
  Edit this file with:
  * `URL_SEARCH` : URL Search for any Nike shoes available on Nike Store Indonesia. You can change it with another shoes.
  * `TELEGRAM_TOKEN` : Your Telegram Bot Token
  * `TELEGRAM_CHAT_ID` : Your Telegram Channel Chat ID
  * `SHEET_ID`: Your Spreadsheet ID
  * `TZ_NAME`:  Your Timezone based on Olson's [TZ Database Name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List)

## Run It!
1. Download this script using Terminal/Command Line.
  ```
  # Clone
  git clone https://github.com/alionar/nikeid-telegram-scrapper.git
  cd nikeid-telegram-scrapper 
  ```
2. Use cron job on your Linux server or another job scheduller to run this command once a day.
  ```
  python3 nikeid-telegram-scrapper.py
  ```
  For example, i set up my crontab to run that command with this [expression](https://crontab.guru/#0_14_*_*_*):
  ```
  0 14 * * * python3 nikeid-telegram-scrapper.py
  ```
  This command will be running everyday at 14:00 CEST (19:00 GMT+7, based on your server timezone)
  
3. Profit.
