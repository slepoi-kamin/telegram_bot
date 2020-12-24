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
    await message.answer('The user banned.')


@dp.message_handler(user_id=admin_id, commands=['clear_db'])
async def clear_db(message: types.Message):
    await user_db.clear()


@dp.message_handler(user_id=admin_id, commands=['clear_blacklist'])
async def clear_blacklist(message: types.Message):
    blacklist.clear()


@dp.message_handler(user_id=admin_id, commands=['backup_db'])
async def backup_db(message: types.Message):
    await user_db.backup()


@dp.message_handler(user_id=admin_id, commands=['start', 'help'])
async def starthelp(message: types.Message):
    message_text = '/gen - Генерация выражения для создания оповещения в TW\n' \
                   '/help - Справка по командам бота\n' \
                   '/start_trade - Начать торговлю\n' \
                   '/stop_trade - Закончить торговлю\n' \
                   '/test_trade - Тестовый режим\n' \
                   '/del_session API_name - Удалить сессию API\n' \
                   '/sessions_list - Список сессий\n' \
                   '/session - Поключить/добавить API\n' \
                   '/clear_db - Отчистить базу пользователей\n' \
                   '/clear_blacklist - Отчистить черный список\n' \
                   '/backup_db - Бекап базы данных\n' \
                   '/add_user user_id username - Добавить пользователя'
    await message.answer(message_text, reply_markup=keyboards['common_keyboard'])
