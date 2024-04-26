import requests
import time
import asyncio
import logging
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Telegram bot setup
telegram_token = '6582928949:AAGu0tbh3GYwW6qpHidG2EeIM4n7Ony-Cmw'
chat_id = '-1002013517786'

# Initialize Bot and Dispatcher
bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# CoinMarketCap API setup
api_key = 'fd5eebfb-7e7c-4457-840f-bf2062b3e9be'
base_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'


def get_crypto_price(crypto_symbol):
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    params = {
        'symbol': crypto_symbol,
        'convert': 'USD'
    }
    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()
    price = data['data'][crypto_symbol]['quote']['USD']['price']
    return price


def send_notification(message):
    asyncio.get_running_loop().create_task(bot.send_message(chat_id, message))


def track_crypto_price(crypto_symbol, threshold_min, threshold_max):
    while True:
        price = get_crypto_price(crypto_symbol)
        if price >= threshold_max:
            message = (f"{crypto_symbol} has reached {price} USD,"
                       f" which is above the threshold of {threshold_max} USD at {datetime.now()}")
            send_notification(message)
            break
        elif price <= threshold_min:
            message = (f"{crypto_symbol} has reached {price} USD,"
                       f" which is below the threshold of {threshold_min} USD at {datetime.now()}")
            send_notification(message)
            break
        time.sleep(5)  # Check every 5 seconds


@dp.message(CommandStart())
async def handle_start(message: types.Message):
    await message.reply(
        "Welcome! Send me the cryptocurrency symbol you want to track,"
        " min and max threshold values separated by a space."
    )


@dp.message()
async def handle_crypto_threshold(message: types.Message):
    try:
        crypto_symbol, threshold_min, threshold_max = message.text.split()
        threshold_min = float(threshold_min)
        threshold_max = float(threshold_max)
        await message.reply(f"Tracking {crypto_symbol} with a minimum threshold of {threshold_min} USD"
                            f" and maximum threshold of {threshold_max} USD.")
        track_crypto_price(crypto_symbol.upper(), threshold_min, threshold_max)
    except ValueError:
        await message.reply("Please provide the cryptocurrency symbol and threshold value separated by a space.")


async def main() -> None:
    # run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
