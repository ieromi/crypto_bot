import requests
import asyncio
import logging
import sys
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

# Telegram bot setup
telegram_token = os.getenv('TG_TOKEN')
chat_id = os.getenv('CHAT_ID')

# Initialize Bot and Dispatcher
bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# CoinMarketCap API setup
api_key = os.getenv('CMC_API_KEY')
base_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

# Set to store references to ongoing tracking tasks
background_tasks = set()


def get_crypto_price(crypto_symbol):
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    params = {
        'symbol': crypto_symbol,
        'convert': 'USD'
    }
    try:
        response = requests.get(base_url, headers=headers, params=params)
        data = response.json()
        price = data['data'][crypto_symbol]['quote']['USD']['price']
        return price
    except Exception as e:
        print(e)


def send_notification(message):
    try:
        asyncio.get_running_loop().create_task(bot.send_message(chat_id, message))
    except Exception as e:
        print(e)


async def track_crypto_price(crypto_symbol, threshold_min, threshold_max):
    while True:
        try:
            price = get_crypto_price(crypto_symbol)
            if price >= threshold_max:
                message = (f"{crypto_symbol} has reached {price} USD,"
                           f" which is above the threshold of {threshold_max} USD"
                           f" at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
                send_notification(message)
                break
            elif price <= threshold_min:
                message = (f"{crypto_symbol} has reached {price} USD,"
                           f" which is below the threshold of {threshold_min} USD"
                           f" at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
                send_notification(message)
                break
        except TypeError:
            send_notification(f"Error: cryptocurrency {crypto_symbol} not found in list."
                              f"Tracking task cancelled.")
            break
        await asyncio.sleep(5)  # Check every 5 seconds asynchronously


# Function to start a bot
@dp.message(CommandStart())
async def handle_start(message: types.Message):
    await message.reply(
        "Welcome! Send me the cryptocurrency symbol you want to track,"
        " min and max threshold values separated by a space."
    )


# Function to cancel all tracking tasks
async def clear_tracking_tasks():
    global background_tasks
    for task in list(background_tasks):
        task.cancel()
    background_tasks = set([])


# Define a command to clear all tracking tasks
@dp.message(Command('clear'))
async def clear_tracks(message: types.Message):
    await clear_tracking_tasks()
    await message.reply("All tracking tasks have been cleared.")


# Function to list all active tasks
async def list_active_tasks(message: types.Message):
    if not background_tasks:
        await message.reply("There are no active tracking tasks at the moment.")
    else:
        active_tasks_info = "\n".join([f"- {task.get_name()}" for task in list(background_tasks)])
        await message.reply(f"Active tracking tasks:\n{active_tasks_info}")


# Add a command to list all active tasks
@dp.message(Command('list'))
async def list_active(message: types.Message):
    await list_active_tasks(message)


# Function to get a list of currencies and thresholds
@dp.message()
async def handle_crypto_threshold(message: types.Message):
    try:
        args = message.text.split()
        if len(args) % 3 != 0:
            await message.reply("Please provide cryptocurrency symbols and their thresholds in sets of three.")
            return

        for i in range(0, len(args), 3):
            crypto_symbol = args[i].upper()
            threshold_min = float(args[i+1])
            threshold_max = float(args[i+2])
            task = asyncio.create_task(track_crypto_price(crypto_symbol, threshold_min, threshold_max))
            task.set_name(f"Currency - {crypto_symbol}; "
                          f"min threshold: {threshold_min}; max threshold: {threshold_max}")
            background_tasks.add(task)
            await message.reply(f"Tracking {crypto_symbol} with a minimum threshold of {threshold_min} USD"
                                f" and maximum threshold of {threshold_max} USD.")
            task.add_done_callback(background_tasks.discard)
    except ValueError:
        await message.reply("Please provide cryptocurrency symbols and their thresholds separated by spaces.")


async def main() -> None:
    # run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
