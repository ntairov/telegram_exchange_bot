import logging

import datetime

import aiohttp

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import text, bold, code

from flag import flagize

from flags import new_flags, keys

from pathlib import Path

from db import session as db_session, Currency, User, Base, engine

from draw_chart import draw_time_series

import os

API_TOKEN = os.environ['TELEGRAM_TOKEN']

URL = 'https://api.exchangeratesapi.io/'

PROXY_URL = 'http://51.158.114.177:8811'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def say_hi(message: types.Message):
    await message.reply(f"Hello,{message.from_user.full_name}. \nSend /help if you want to read my commands list ")


@dp.message_handler(commands=['help'])
async def show_available_commands(message: types.Message):
    msg = text(bold('Here you can read the list of my commands:'),
               '/list — Show all currency rates to USD\n',
               '/exchange — Convert one currency into another i.e:', code('/exchange 10 USD to CAD\n'),
               '/history — Shows selected currency image graph i.e:',
               code('/history USD/CAD'), sep='\n')

    await message.reply(msg, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['list', 'lst'])
async def show_currency(message):
    get_base_currency = URL + 'latest?base=USD'
    content = []
    await types.ChatActions.typing()

    ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)

    timestamp = db_session.query(Currency).filter(Currency.chat_id == message.chat.id).filter(
        Currency.timestamp < ten_minutes_ago).first()

    if timestamp or timestamp is None:
        async with aiohttp.ClientSession() as session:
            fetch_data = await retrieve_currency(get_base_currency, session)

        for key, value in fetch_data['rates'].items():
            if key in new_flags.keys():
                formatted_data = text("{} {} : {:.2f}\n".format(flagize(new_flags[key]), key, value), sep='\n')
            else:
                formatted_data = text("{} : {:.2f}\n".format(key, value), sep='\n')
            content.append(formatted_data)

        user = db_session.query(User.id).filter_by(id=message.chat.id).first()
        if not user:
            add_user = User(id=message.chat.id, fullname=message.chat.full_name, username=message.chat.username)
            db_session.add(add_user)

        add_currency = Currency(currencies=text(*content, sep='\n'), chat_id=message.chat.id)
        db_session.add(add_currency)
        db_session.commit()

        await bot.send_message(message.chat.id, text(*content, sep='\n'), parse_mode=types.ParseMode.MARKDOWN)

    else:
        query = db_session.query(Currency.currencies).filter(Currency.chat_id == message.chat.id).first()
        await bot.send_message(message.chat.id, text(*query, sep='\n'), parse_mode=types.ParseMode.MARKDOWN)


async def retrieve_currency(url, session):
    async with session.get(url) as response:
        return await response.json()


@dp.message_handler(commands=['exchange'])
async def convert_currency(message):
    try:
        split_text_by_to = message.text.lower().split("to")
        if len(split_text_by_to) == 1:
            raise ValueError

        split_text_by_currency = split_text_by_to[0].split(" ")
        money = split_text_by_currency[1]

        if '$' in money:
            replace_symbol = money.replace('$', 'USD ')
            first_symbol = replace_symbol.split(" ")[0]
            money = replace_symbol.split(" ")[1]
        else:
            first_symbol = split_text_by_currency[2].upper()

        if isinstance(int(money), int):
            money = int(money)
        else:
            money = int(money.split(" ")[1])

        last_symbol = split_text_by_to[-1].strip().upper()

        if first_symbol in keys and last_symbol in keys:
            get_symbols = URL + f'latest?symbols={first_symbol},{last_symbol}'

            async with aiohttp.ClientSession() as session:
                async with session.get(get_symbols) as response:
                    fetch_currencies = await response.json()
            result = fetch_currencies['rates'][last_symbol] / fetch_currencies['rates'][first_symbol] * money

            await bot.send_message(message.chat.id, text("{}{} {:.2f}\n".format(flagize(new_flags[last_symbol]),
                                                                                last_symbol, result), sep='\n'))
        else:
            raise ValueError

    except ValueError:
        await bot.send_message(message.chat.id, text(bold("Invalid format should be:"),
                                                     code("\n/exchange 10 USD to CAD \nor \n/exchange $10 to CAD"),
                                                     sep='\n'), parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['history'])
async def draw_chart(message):
    try:
        content = []
        first_currency, second_currency = message.text.upper().replace('/', ' ').split(' ')[2:]
        current_time = datetime.datetime.now().date()
        last_seven_days = datetime.datetime.now().date() - datetime.timedelta(days=7)

        if first_currency in keys and second_currency in keys:
            chart_url = f'https://api.exchangeratesapi.io/history?' \
                        f'start_at={last_seven_days}&end_at={current_time}&base={first_currency}&symbols={second_currency}'

            async with aiohttp.ClientSession() as session:
                async with session.get(chart_url) as response:
                    fetch_currencies = await response.json()
                    if not fetch_currencies['rates']:
                        await bot.send_message(message.chat.id,
                                               text(bold('No exchange rate data is available for the selected currency.')),
                                               parse_mode=types.ParseMode.MARKDOWN)
                    else:
                        get_plot = draw_time_series(fetch_currencies['rates'])
                        content.append(get_plot)
            await bot.send_photo(message.chat.id, *content)
        else:
            raise ValueError

    except ValueError:
        await bot.send_message(message.chat.id, text(bold("Invalid format should be:"),
                                                     code("/history USD/CAD\nor\n/history USD/RUB"),
                                                     sep='\n'), parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    if not Path('currencies.db').exists():
        Base.metadata.create_all(engine)
    executor.start_polling(dp, skip_updates=True)
