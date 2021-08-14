from aiogram import types

from base import dp, bot
from conf import WEBHOOK_URL
from keyboards import keyboards


@dp.message_handler(commands=['gen'])
async def generate(message: types.Message):
    """

    :param message:
        {
            "message": {
                "from": {
                    "id": ADMIN_ID
                },
                "chat": {
                    "id": ADMIN_ID,
                    "type": "private"
                },
                "text": "{{strategy.order.action}} @ {{strategy.order.contracts}} исполнилась по {{ticker}}. Новая позиция стратегии {{strategy.position_size}}",
                "type": "tr_view",
                "exchange": "{{exchange}}",
                "trade": {
                    "side": "{{strategy.order.action}}",
                   "symbol": "{{ticker}}",
                   "quantity": "{{strategy.order.contracts}}",
                   "price": "{{strategy.order.price}}",
                   "type": "{{strategy.order.comment}}"
                }
            }
        }
    :return:
    """

    # message_text = '{"channel_post": {' \
    #                '"type": "tr_view", ' \
    #                '"exchange": "{{exchange}}",' \
    #                '"chat": {"id": "' + f'{message.chat.id}' + '"},' \
    #                '"text": "{{strategy.order.action}} @ {{strategy.order.contracts}} исполнилась по {{ticker}}. Новая позиция стратегии {{strategy.position_size}}",' \
    #                '"trade": {' \
    #                '"side": "{{strategy.order.action}}",' \
    #                '"symbol": "{{ticker}}",' \
    #                '"quantity": "{{strategy.order.contracts}}",' \
    #                '"price": "{{strategy.order.price}}",' \
    #                '"type": "{{strategy.order.comment}}"}}}'

    message_text = '{' \
                   '"message": {' \
                   '"from": {' \
                   '"id": ADMIN_ID' \
                   '},' \
                   '"chat": {' \
                   '"id": ADMIN_ID,' \
                   '"type": "private"' \
                   '},' \
                   '"text": "{{strategy.order.action}} @ {{strategy.order.contracts}} исполнилась по {{ticker}}. Новая позиция стратегии {{strategy.position_size}}",' \
                   '"type": "tr_view",' \
                   '"exchange": "{{exchange}}",' \
                   '"trade": {' \
                   '"side": "{{strategy.order.action}}",' \
                   '"symbol": "{{ticker}}",' \
                   '"quantity": "{{strategy.order.contracts}}",' \
                   '"price": "{{strategy.order.price}}",' \
                   '"type": "{{strategy.order.comment}}"}}}'

    await bot.send_message(message.chat.id, message_text)
    await bot.send_message(message.chat.id, f'WebHook URL: {WEBHOOK_URL}')


@dp.message_handler(commands=['start', 'help'])
async def starthelp(message: types.Message):
    message_text = '/gen - Генерация выражения для создания оповещения в TW\n' \
                   '/help - Справка по командам бота\n' \
                   '/start_trade - Начать торговлю\n' \
                   '/stop_trade - Закончить торговлю\n' \
                   '/test_trade - Тестовый режим\n' \
                   '/del_session API_name - Удалить сессию API\n'\
                   '/sessions_list - Список сессий\n' \
                   '/session - Поключить/добавить API'
    await bot.send_message(message.chat.id, message_text, reply_markup=keyboards['common_keyboard'])