from aiogram import types

buttons = {
    'binance': types.KeyboardButton('BINANCE'),
    'bitmex': types.KeyboardButton('BITMEX'),
    'session': types.KeyboardButton('/session'),
    'start_trading': types.KeyboardButton('/start_trade'),
    'stop_trading': types.KeyboardButton('/stop_trade'),
    'test_trading': types.KeyboardButton('/test_trade'),
    'help': types.KeyboardButton('/help'),
    'gen': types.KeyboardButton('/gen'),
}

api_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
api_keyboard.row(buttons['binance'], buttons['bitmex'])

common_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
common_keyboard.row(buttons['help'], buttons['session'], buttons['gen'])
common_keyboard.row(buttons['start_trading'], buttons['test_trading'], buttons['stop_trading'])


def request_keyboard(id, name):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(f'/add_user {id} {name}'),
                 types.KeyboardButton(f'/decline {id}'))
    return keyboard


keyboards = {
    'api_keyboard': api_keyboard,
    'common_keyboard': common_keyboard,
}
