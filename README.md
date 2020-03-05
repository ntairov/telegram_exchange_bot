# Telegram Exchange Bot
This bot shows exchange rates, converts one currency into another and draws time series chart for the last 7 days.
This bot already has been deployed on heroku. It's available for testing and using for personal purposes.
## Link to bot

https://t.me/route4me_exchange_bot

@route4me_exchange_bot


## List of used technologies and libraries :wrench:
- [x] Python 3.7.4
- [x] aiogram
- [x] emoji-country-flag
- [x] SQLAlchemy
- [x] matplotlib

## How to run locally
 `python3 -m venv env`

 `source env/bin/activate`

 `python pip install -r requirements.txt` 

 `python3 bot.py`

## Database Schema (One to Many-Relationship)

![Imgur Image](https://imgur.com/DbG3vSb.jpg)
