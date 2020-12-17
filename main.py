import logging

from aiogram.utils.executor import start_webhook

import base
from base import bot
from base import dp
from conf import admin_id, WEBHOOK_PATH, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT

import handlers


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    await bot.send_message(admin_id, "Я запущен!")
    # await bot.send_message(message.chat.id, 'Ты  полный лох', reply_markup=types.ReplyKeyboardRemove())
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await base.storage.close()
    await base.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
