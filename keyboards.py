from aiogram import types

buttons = {
    'binance': types.KeyboardButton('binance'),
    'bitmex': types.KeyboardButton('bitmex'),
    'session': types.KeyboardButton('/session'),
    'start_trading': types.KeyboardButton('/start_trade'),
    'stop_trading': types.KeyboardButton('/stop_trade'),
    'help': types.KeyboardButton('/help'),
    'gen': types.KeyboardButton('/gen'),
}

api_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
api_keyboard.row(buttons['binance'], buttons['bitmex'])

common_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
common_keyboard.row(buttons['help'], buttons['session'], buttons['gen'])
common_keyboard.row(buttons['start_trading'], buttons['stop_trading'])

keyboards = {
    'api_keyboard': api_keyboard,
    'common_keyboard': common_keyboard,
}
