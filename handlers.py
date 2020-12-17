from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from base import bot, dp, user_db
from buttons import buttons
from aiogram import Bot

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


@dp.errors_handler()
async def echo8(a1, a2):
    await bot.send_message(564514817, a1.message.text)


@dp.message_handler(commands=['gen'])
async def generate(message: types.Message):
    message_text = '{"channel_post": {' \
                   '"type": ' \
                   '"tr_view",' \
                   '"chat": {"id": "' + f'{message.chat.id}' + '"},' \
                                                               '"text": "{{strategy.order.action}} @ {{strategy.order.contracts}} исполнилась по {{ticker}}. Новая позиция стратегии {{strategy.position_size}}",' \
                                                               '"trade": {' \
                                                               '"side": "{{strategy.order.action}}",' \
                                                               '"symbol": "{{ticker}}",' \
                                                               '"quantity": "{{strategy.order.contracts}}",' \
                                                               '"price": "{{strategy.order.price}}",' \
                                                               '"type": "{{strategy.order.comment}}"}}}'

    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(commands=['start', 'help'])
async def starthelp(message: types.Message):
    message_text = '/gen - Генерация выражения для создания оповещения в TW\n' \
                   '/help - Справка по командам бота\n' \
                   '/session - Создание сесии для API'

    await bot.send_message(message.chat.id, message_text)


class API(StatesGroup):
    api = State()
    api_key = State()
    s_key = State()


class TradeState(StatesGroup):
    trade = State()


class RunningSessions(StatesGroup):
    sessions = State()


@dp.message_handler(commands='session', state='*')
async def api_step_1(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.row(buttons['binance'], buttons['bitmex'])
    await message.answer("Выберите API:", reply_markup=keyboard)
    # await API.api.set()
    await API.next()
    keyboard.clean()


@dp.message_handler(state=API.api)
async def api_step_2(message: types.Message, state: FSMContext):

    await state.update_data(api=message.text.lower())
    await message.answer("Ключ API:")
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


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)

    # or reply INTO webhook
    # return SendMessage(message.chat.id, message.text)

    await bot.send_message(message.chat.id, 'Ты  полный лох',
                           reply_markup=types.ReplyKeyboardRemove())
    # return SendMessage(message.chat.id, 'Ты лох')