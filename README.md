# nikeid-telegram-scrapper
Get daily reminder about certain Nike shoes stock on [Nike ID Store](https://www.nike.com/id/w?q=&vst=) via Telegram Channel

## What to Prepare First?
1. Install Python => 3.6
2. Install dependencies `pip install -r  requirements.txt`
3. Create Telegram bot to get token. [How?](https://core.telegram.org/bots#6-botfather).
4. Make new Telegram channel and add your bot to channel. [How?](https://telegram.org/faq_channels#q-what-39s-a-channel)
5. Get your Telegram channel Chat ID. [How?](https://github.com/GabrielRF/telegram-id)
6. Get Service Account on GCP and save it as `client_secret.json` in this repo folder. [How?](https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount)
7. Enable Google Drive API and Sheet API for your project account on GCP. [How?](https://support.google.com/googleapi/answer/6158841?hl=en)
8. Create [New Google Spreadsheet](https://docs.google.com/spreadsheets/u/0/) and delete all row except first one and then add `--END--` in cell A1.
9. Get `sheet_id` from spreadsheet that you already made before. [How?](https://developers.google.com/sheets/api/guides/concepts#spreadsheet_id)
10. Create `config.json` and put in this repo folder. Use this template:
  ```
  {
	"CWD":"YOUR_REPO_FILEPATH",
	"URL_SEARCH":"https://www.nike.com/id/w/jordan-1-lifestyle-high-top-shoes-13jrmz4fokyz6lqy0zy7ok",
	"TELEGRAM":{
		"TOKEN":"YOUR_TELEGRAM_BOT_TOKEN",
		"CHAT_ID":YOUR_TELEGRAM_CHAT_ID
	},
	"SHEET":{
		"ID":"YOUR_SHEET_ID"
	}
  }
  ```
  Edit this file with:
  * `CWD` : Current Working Directory. Change it with this repo [absolute file path](https://en.wikipedia.org/wiki/Path_(computing)#Absolute_and_relative_paths) folder in your computer after cloning this repo (see [here](https://github.com/alionar/nikeid-telegram-scrapper/blob/master/README.md#so-whats-next) how to clone).
  * `URL_SEARCH` : URL Search for any Nike shoes available on Nike Store Indonesia. You can change it with another shoes.
  * `TELEGRAM_TOKEN` : Your Telegram Bot Token
  * `TELEGRAM_CHAT_ID` : Your Telegram Channel Chat ID
  * `SHEET_ID`: Your Spreadsheet ID

## So What's Next?
1. Download this script using Terminal/Command Line.
  ```
  # Clone
  git clone https://github.com/alionar/nikeid-telegram-scrapper.git
  cd nikeid-telegram-scrapper
  
  # Get File Path
  # for Linux/MacOS
  pwd
  # for Windows
  cd 
  ```
2. Use cron job on your Linux server or another job scheduller to run this command once a day.
  ```
  python nikeid-telegram-scrapper.py
  ```
3. Profit.
