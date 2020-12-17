from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from base import dp, user_db
from keyboards import keyboards


class API(StatesGroup):
    api = State()
    api_key = State()
    s_key = State()


@dp.message_handler(commands='session', state='*')
async def api_step_1(message: types.Message):
    await message.answer("Выберите API:", reply_markup=keyboards['api_keyboard'])
    await API.next()


@dp.message_handler(state=API.api)
async def api_step_2(message: types.Message, state: FSMContext):

    await state.update_data(api=message.text.lower())
    await message.answer("Ключ API:", reply_markup=types.ReplyKeyboardRemove())
    await API.next()


@dp.message_handler(state=API.api_key)
async def api_step_3(message: types.Message, state: FSMContext):

    await state.update_data(api_key=message.text.lower())
    await message.answer("C_Ключ:")
    await API.next()


@dp.message_handler(state=API.s_key)
async def api_step_4(message: types.Message, state: FSMContext):

    await state.update_data(s_key=message.text.lower())
    api_data = await state.get_data()
    await user_db.create_session(api_data['api'],
                           api_data['api_key'],
                           api_data['s_key'])
    await state.finish()
    await message.answer('⌨', reply_markup=keyboards['common_keyboard'])