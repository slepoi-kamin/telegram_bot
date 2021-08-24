from aiogram import Bot, types
# from binance.client import Client
from mock_binance import Client
import asyncio
import time
from awaits.awaitable import awaitable
from binance.exceptions import BinanceAPIException, BinanceOrderException


class Sessions(list):
    def append(self, __object) -> None:
        if isinstance(__object, Session):
            super().append(__object)
        else:
            raise TypeError('Class Sessions have permissions to append only Session object')

    def __repr__(self):
        return f'[{len(self)} x Session]'


class Session:

    def __init__(self, api, api_key, s_key):
        self.api = api
        self.api_key = api_key
        self.s_key = s_key
        self.client = Client(api_key, s_key)
        self.client.API_URL = 'https://testnet.binance.vision/api'

    @awaitable
    def my_aping(self, id):
        # async def my_aping(client, id):
        print(f'start {id}')
        # await client.ping()
        self.client.ping()
        print(f'stop {id}')

    async def is_api_correct(self):
        try:
            self.client.get_account()
        except BinanceAPIException:
            bot = Bot.get_current()
            user_id = types.User.get_current().id
            await bot.send_message(user_id, 'ERROR: Your API data is incorrect')
            return False
        else:
            return True

    async def _is_tested(self, user_id, **kwargs):
        flag = False
        try:
            self.client.create_test_order(**kwargs)
        except BinanceAPIException as e:
            await Bot.get_current().send_message(user_id,
                                                 f'ERROR: Your API data is incorrect: {e}')
        except BinanceOrderException as e:
            await Bot.get_current().send_message(user_id,
                                                 f'ERROR: Your ORDER data is incorrect: {e}')
        except Exception as e:
            await Bot.get_current().send_message(user_id,
                                                 f'ERROR: Unknown error: {e}')
        else:
            flag = True
        return flag

    @awaitable
    def _get_order(self, symbol, order_id):
        return self.client.get_order(symbol=symbol, orderId=order_id)

    async def _check_order(self, user_id, symbol, order_id):
        flag = True
        t0 = time.time()
        while flag:
            ord = await self._get_order(symbol, order_id)
            status = ord['status']
            if status in ['FILLED', 'CANCELED', 'PENDING_CANCEL', 'REJECTED', 'EXPIRED']:
                flag = False
                await Bot.get_current().send_message(user_id,
                                                     f'The order status is: {status}.')
                await Bot.get_current().send_message(user_id,
                                                     str(ord).replace(', ', '\n'))
            elif time.time() - t0 > 3:
                flag = False
                await Bot.get_current().send_message(user_id,
                                                     f'The order status is: {status}.')
                await Bot.get_current().send_message(user_id,
                                                     str(ord).replace(', ', '\n'))
            else:
                await asyncio.sleep(1)

    async def test_order(self, user_id, **kwargs):
        if await self._is_tested(user_id, **kwargs):
            await Bot.get_current().send_message(user_id,
                                                 'The order has been verified.')

    async def create_order(self, user_id, **kwargs):
        if await self._is_tested(user_id, **kwargs):
            order = self.client.create_order(**kwargs)
            await Bot.get_current().send_message(user_id,
                                                 f'The order has been created.')
            await self._check_order(user_id, order['symbol'], order['orderId'])
        # else:
        #     order = None
        # return order


if __name__ == '__main__':
    pass

