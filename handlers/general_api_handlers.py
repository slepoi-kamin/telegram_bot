from aiogram import types

from base import dp, user_db


@dp.message_handler(commands=['del_session'])
async def del_session(message: types.Message):
    params = message.get_args().split()
    if len(params) > 0:
        [api, *_] = params
        await user_db.del_session(api)
    else:
        await message.answer("You should specify API name as first parameter of the command.")


@dp.message_handler(commands=['sessions_list'])
async def sessions_list(message: types.Message):
    await user_db.get_sessions_list()
