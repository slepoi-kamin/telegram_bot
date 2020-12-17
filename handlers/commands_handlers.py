from aiogram import types

from base import dp, bot
from keyboards import keyboards


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
                   '/session - Создание сесии для API\n' \
                   '/start_trade - Начать торговлю\n' \
                   '/stop_trade - Закончить торговлю\n' \
                   '/session - Поключить/добавить API'
    await bot.send_message(message.chat.id, message_text, reply_markup=keyboards['common_keyboard'])