from aiogram import types

from base import dp, user_db


@dp.message_handler(commands='start_trade')
async def start_trading(message: types.Message):
    state = user_db.get_state()
    if state:
        await message.answer('Already trading')
    elif state is None:
        await message.answer('At first you should add API')
    else:
        await user_db.set_state()


@dp.message_handler(commands='stop_trade')
async def stop_trading(message: types.Message):
    await user_db.reset_state()