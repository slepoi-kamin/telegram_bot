from aiogram import types
from base import dp, bot


@dp.channel_post_handler()
async def echo3(text):
    if 'type' in text.values.keys() and text.values['type'] == 'tr_view':
        await bot.send_message(text.chat.id, f'{text.text}',
                               parse_mode=types.ParseMode.HTML)

        if 'trade' in text.values.keys():
            side = text.values['trade']['side']
            symbol = text.values['trade']['symbol']
            quantity = float(text.values['trade']['quantity'])
            price = float(text.values['trade']['price'])
            type = text.values['trade']['type']
        else:
            await bot.send_message(text.chat.id,
                                   '<b>ERROR: Wrong tr_view format</b>',
                                   parse_mode=types.ParseMode.HTML)


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)

    # or reply INTO webhook
    # return SendMessage(message.chat.id, message.text)

    await bot.send_message(message.chat.id, 'Ты  полный лох')
    # return SendMessage(message.chat.id, 'Ты лох')


@dp.errors_handler()
async def echo8(a1, a2):
    await bot.send_message(564514817, a1.message.text)