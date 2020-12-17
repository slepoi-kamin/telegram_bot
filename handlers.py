from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from base import bot, dp, user_db
from buttons import buttons


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
    # zero = State(state='zeros')
    api = State()
    api_key = State()
    s_key = State()


class TradeState(StatesGroup):
    trade = State()


class RunningSessions(StatesGroup):
    sessions = State()


@dp.message_handler(commands='session', state='*')
async def api_step_1(message: types.Message, state: FSMContext):
    print(API.api)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.row(buttons['binance'], buttons['bitmex'])
    await message.answer("Выберите API:", reply_markup=keyboard)
    # await API.api.set()
    await API.next()
    await state.storage.save()
    keyboard.clean()


@dp.message_handler(state=API.api)
async def api_step_2(message: types.Message, state: FSMContext):

    await state.update_data(api=message.text.lower())
    await message.answer("Ключ API:")
    # await API.api_key.set()
    await API.next()
    await state.storage.save()


@dp.message_handler(state=API.api_key)
async def api_step_3(message: types.Message, state: FSMContext):

    await state.update_data(api_key=message.text.lower())
    await message.answer("C_Ключ:")
    # await API.s_key.set()
    await API.next()
    await state.storage.save()


@dp.message_handler(state=API.s_key)
async def api_step_4(message: types.Message, state: FSMContext):

    await state.update_data(s_key=message.text.lower())
    api_data = await state.get_data()
    user_db.create_session(message.chat.id,
                           message.chat.username,
                           api_data['api'],
                           api_data['api_key'],
                           api_data['s_key'])
    user_db.save()
    # TODO: создать метод фззутв для UserDB и перенести в него три последние команды, добавить сохранение
    await message.answer("Готово")
    await state.finish()

    # await RunningSessions.sessions.set()
    # await state.update_data(sessions='session')
    # print(await state.get_data())

    await state.storage.save()


@dp.message_handler(commands='start_trade', state='*')
async def start_trading(message: types.Message, state: FSMContext):

    if await state.get_state():
        message_text = 'Уже торгуется...'
    else:
        message_text = 'Начинаю торговлю...'
        await TradeState.trade.set()
        user_db.set_state(message.chat.id, True)
        user_db.save()
        await state.storage.save()
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(commands='stop_trade', state=TradeState.trade)
async def stop_trading(message: types.Message, state: FSMContext):

    message_text = 'Заканчиваю торговлю...'
    await state.finish()
    user_db.set_state(message.chat.id, False)
    user_db.save()
    await state.storage.save()
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)

    # or reply INTO webhook
    # return SendMessage(message.chat.id, message.text)

    await bot.send_message(message.chat.id, 'Ты  полный лох',
                           reply_markup=types.ReplyKeyboardRemove())
    # return SendMessage(message.chat.id, 'Ты лох')