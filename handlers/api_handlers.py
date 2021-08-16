import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from base import dp, user_db, bot
from conf import ADMIN_ID
from keyboards import keyboards, request_keyboard


class API(StatesGroup):
    api = State()
    api_key = State()
    s_key = State()


@dp.message_handler(commands='session', state='*')
async def api_step_1(message: types.Message):
    if await user_db.is_new_user():
        user = types.User.get_current()
        await bot.send_message(ADMIN_ID, 'New request:', reply_markup=request_keyboard(user.id, user.username))
        await message.answer('Your request has been sent to the administrator.\n'
                             'Please wait for approval.')
    else:
        await message.answer("Выберите API:", reply_markup=keyboards['api_keyboard'])
        await API.next()


@dp.message_handler(state=API.api)
async def api_step_2(message: types.Message, state: FSMContext):

    await state.update_data(api=message.text, msg1=message.message_id)
    await message.answer("Ключ API:", reply_markup=types.ReplyKeyboardRemove())
    await API.next()


@dp.message_handler(state=API.api_key)
async def api_step_3(message: types.Message, state: FSMContext):

    await state.update_data(api_key=message.text, msg2=message.message_id)
    await message.answer("C_Ключ:")
    await API.next()


@dp.message_handler(state=API.s_key)
async def api_step_4(message: types.Message, state: FSMContext):

    await state.update_data(s_key=message.text, msg3=message.message_id)
    api_data = await state.get_data()
    await user_db.create_session(api_data['api'],
                                 api_data['api_key'],
                                 api_data['s_key'])
    await state.finish()
    await message.answer('Messages with your API data will be deleted.', reply_markup=keyboards['common_keyboard'])
    for message_id in [api_data['msg1'], api_data['msg2'], api_data['msg3']]:
        await bot.delete_message(message.chat.id, message_id)
