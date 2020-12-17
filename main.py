import logging
from pathlib import Path

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook

import UserDB
from filestorage import PickleStorage

API_TOKEN = '1269323050:AAHP67_k4tHobu0g5_69NUayfjwp3tY6wxw'

# webhook settings
# WEBHOOK_HOST = 'https://your.domain'
# WEBHOOK_PATH = '/path/to/api'
# WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBHOOK_HOST = 'https://1881f9b98c4e.ngrok.io'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '127.0.0.1'  # or ip
WEBAPP_PORT = 5000

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

storage = PickleStorage(Path('states.txt'))
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# dp.current_state()

user_db = UserDB.UserDB()

buttons = {'binance': types.KeyboardButton('binance'),
           'bitmex': types.KeyboardButton('bitmex')}


# class UserDB():
#
#     def __init__(self):
#         self.db_file = Path('user_db.txt')
#         if self.db_file.exists():
#             self.load()
#         else:
#             self.__create_new()
#
#     def __create_new(self):
#         user_dict = {'user_id': [],
#                      'user_name': [],
#                      'sessions': []}
#         self.db = pd.DataFrame(user_dict)
#
#     def save(self):
#         file = open(self.db_file, 'wb')
#         pickle.dump(self.db, file)
#         file.close()
#
#     def load(self):
#         file = open(self.db_file, 'rb')
#         self.db = pickle.load(file)
#         file.close()
#
#     def my_append(self, api, api_key, s_key, user_id, username, ready_status):
#         session = bnnc.Session(api, api_key, s_key)
#         dict = {'user_id': user_id,
#                 'user_name': username,
#                 'sessions': session,
#                 'ready_status': ready_status}
#         user_db.db.loc[len(user_db.db.index)] = dict


# class UserDB(pd.DataFrame):
#
#     def __init__(self):
#         self.db_file = Path('user_db.txt')
#         if self.db_file.exists():
#             self.load()
#         else:
#             self.__create_new()
#
#     def __create_new(self):
#         user_dict = {'user_id': [],
#                      'user_name': [],
#                      'sessions': []}
#         pd.DataFrame.__init__(user_dict)
#
#     def save(self):
#         file = open(self.db_file, 'wb')
#         pickle.dump(self.db, file)
#         file.close()
#
#     def load(self):
#         file = open(self.db_file, 'rb')
#         self.db = pickle.load(file)
#         file.close()
#
#     def my_append(self, api, api_key, s_key, user_id, username, ready_status):
#         session = bnnc.Session(api, api_key, s_key)
#         dict = {'user_id': user_id,
#                 'user_name': username,
#                 'sessions': session,
#                 'ready_status': ready_status}
#         user_db.db.loc[len(user_db.db.index)] = dict


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


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # await bot.send_message(message.chat.id, 'Ты  полный лох', reply_markup=types.ReplyKeyboardRemove())
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
