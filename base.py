from pathlib import Path
import logging
from aiogram import Bot, Dispatcher

import UserDB
from conf import API_TOKEN
from filestorage import PickleStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


# logging.basicConfig(level=logging.INFO)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


bot = Bot(token=API_TOKEN)

storage = PickleStorage(Path('states.txt'))
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# database
user_db = UserDB.UserDB()