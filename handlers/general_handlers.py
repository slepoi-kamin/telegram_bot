from aiogram import types
from base import dp, bot, user_db


@dp.channel_post_handler()
async def echo3(text):

    if 'type' in text.values.keys() and text.values['type'] == 'tr_view':
        if not await user_db.is_new_user(user_id=int(text.chat.id)):
            await bot.send_message(text.chat.id, f'{text.text}',
                                   parse_mode=types.ParseMode.HTML)

            if 'trade' in text.values.keys():
                exchange = text.values['exchange']
                side = str(text.values['trade']['side']).upper()
                symbol = text.values['trade']['symbol']
                quantity = float(text.values['trade']['quantity'])
                price = float(text.values['trade']['price'])
                type = text.values['trade']['type']

                ord_kwargs = {}
                for key in ('exchange', 'side', 'symbol', 'quantity', 'price', 'type'):
                    ord_kwargs[key] = locals()[key]
                await user_db.create_order(int(text.chat.id), **ord_kwargs)
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


# @dp.errors_handler()
# async def echo8(a1, a2):
#     await bot.send_message(564514817, a1.message.text)