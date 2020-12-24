import asyncio
import random
from time import sleep


class Client:

    def __init__(self, api_key, s_key):
        self.api_key = api_key
        self.s_key = s_key

    @staticmethod
    def _sleep():
        # sleep(random.random() / 5)
        pass

    def ping(self):
        self._sleep()
        return {}

    def get_account(self):
        self._sleep()
        return {}

    def create_test_order(self, **kwargs):
        self._sleep()
        return {}

    def get_order(self, symbol=None, orderId=None):
        self._sleep()
        return {'symbol': symbol, 'orderId': orderId, 'status': 'test'}

    def create_order(self, **kwargs):
        self._sleep()
        kwargs['symbol'] = 'test_symbol'
        kwargs['orderId'] = 'test_orderId'
        return kwargs