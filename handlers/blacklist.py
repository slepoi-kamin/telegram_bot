
from aiogram import types
from base import dp

blacklist = []


@dp.message_handler(lambda msg: msg.chat.id in blacklist)
async def echo(message: types.Message):
    await message.answer('Sorry, you are baned.')
