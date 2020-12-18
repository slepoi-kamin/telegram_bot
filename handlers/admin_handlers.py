from aiogram import types

from base import dp, user_db, bot
from conf import admin_id
from handlers.blacklist import blacklist
from keyboards import keyboards


@dp.message_handler(user_id=admin_id, commands=['add_user'])
async def add_user(message: types.Message):
    [user_id, user_name, *_] = message.get_args().split()
    await user_db.add_user(int(user_id), user_name)
    await bot.send_message(int(user_id), 'Your request approved.', reply_markup=keyboards['common_keyboard'])


@dp.message_handler(user_id=admin_id, commands=['decline'])
async def decline_user(message: types.Message):
    [user_id, *_] = message.get_args().split()
    await bot.send_message(int(user_id), 'Your request was rejected.\n'
                                         'You will be baned for some time.',
                           reply_markup=keyboards['common_keyboard'])
    blacklist.append(int(user_id))
    print(blacklist)
    await message.answer('The user banned.')