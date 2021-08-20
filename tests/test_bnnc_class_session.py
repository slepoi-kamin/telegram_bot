import asyncio
import time
import pytest
from bnnc import Session
from mock_binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from aiogram import Bot, types
from unittest.mock import MagicMock, AsyncMock


class MockClient:
    def __init__(self, api_key, s_key):
        self.s_key = s_key
        self.api_key = api_key


class MockBot:
    def __init__(self):
        self.current = 'test_current'


class MockUser:
    def __init__(self):
        self.id = 'test_id'


@pytest.fixture
def mocked_bot(monkeypatch):
    monkeypatch.setattr(Bot, "__init__", MockBot.__init__)
    # noinspection PyArgumentList
    mocked_bot = Bot()
    monkeypatch.setattr(Bot, "get_current", MagicMock(return_value=mocked_bot))
    monkeypatch.setattr(Bot, "send_message", AsyncMock())
    return mocked_bot


@pytest.fixture
def mocked_client(monkeypatch):
    monkeypatch.setattr(Client, "__init__", MockClient.__init__)
    mocked_client = Client('test_api_key', 'test_s_key')
    return mocked_client


@pytest.fixture
def mocked_exceptions(monkeypatch):
    monkeypatch.setattr(BinanceAPIException, "__init__", lambda self: None)
    monkeypatch.setattr(
        BinanceAPIException, "__str__", lambda self: 'TestBinanceAPIException')
    monkeypatch.setattr(BinanceOrderException, "__init__", lambda self: None)
    monkeypatch.setattr(
        BinanceOrderException, "__str__", lambda self: 'TestBinanceOrderException')


@pytest.fixture
def mocked_session(mocked_client):
    return Session('test_api', 'test_api_key', 'test_s_key')


@pytest.fixture
def mocked_user(monkeypatch):
    monkeypatch.setattr(types.User, "__init__", MockUser.__init__)
    mocked_user = types.User()
    monkeypatch.setattr(types.User, "get_current", MagicMock(return_value=mocked_user))
    return mocked_user


class TestSessionInit:

    def test_init(self, mocked_session):
        assert mocked_session.s_key == 'test_s_key'
        assert mocked_session.api == 'test_api'
        assert mocked_session.api_key == 'test_api_key'
        assert isinstance(mocked_session.client, Client)
        assert mocked_session.client.api_key == 'test_api_key'
        assert mocked_session.client.s_key == 'test_s_key'
        assert 'API_URL' in mocked_session.client.__dict__


class TestSessionIsApiCorrect:

    @pytest.mark.asyncio
    async def test_normal(self, mocked_session, mocked_bot):
        mocked_session.client.get_account = MagicMock(return_value='something')
        assert await mocked_session.is_api_correct() is True
        mocked_session.client.get_account.assert_called_once()

    @pytest.mark.asyncio
    async def test_binance_exception(
            self,
            mocked_session,
            mocked_bot,
            mocked_user,
            mocked_exceptions,
    ):
        # noinspection PyArgumentList
        mocked_session.client.get_account = MagicMock(side_effect=BinanceAPIException())
        # tests:
        assert await mocked_session.is_api_correct() is False
        mocked_session.client.get_account.assert_called_once()
        mocked_bot.get_current.assert_called_once()
        mocked_bot.send_message.assert_awaited_once_with(
            mocked_user.id, 'ERROR: Your API data is incorrect')


class TestSessionIsTested:

    @pytest.mark.parametrize('exception, error_msg', [
        ('BinanceAPIException', 'ERROR: Your API data is incorrect: '),
        ('BinanceOrderException', 'ERROR: Your ORDER data is incorrect: '),
        ('Exception', 'ERROR: Unknown error: '),
    ])
    @pytest.mark.asyncio
    async def test_exceptions(
            self,
            mocked_session,
            mocked_bot,
            mocked_exceptions,
            mocked_user,
            exception,
            error_msg
    ):
        # noinspection PyArgumentList
        exceptions = {
            'BinanceAPIException': BinanceAPIException(),
            'BinanceOrderException': BinanceOrderException(),
            'Exception': Exception(),
        }
        mocked_session.client.create_test_order = MagicMock(side_effect=exceptions[exception])
        kwargs = {'test_key': 'test_val'}
        assert await mocked_session._is_tested(mocked_user.id, **kwargs) is False
        mocked_bot.get_current.assert_called_once()
        mocked_bot.send_message.assert_awaited_once_with(mocked_user.id,
                                                         error_msg + f'{exceptions[exception]}')

    @pytest.mark.asyncio
    async def test_normal(self, mocked_session, mocked_user):
        mocked_session.client.create_test_order = MagicMock()
        kwargs = {'test_key': 'test_val'}
        assert await mocked_session._is_tested(mocked_user.id, **kwargs) is True
        mocked_session.client.create_test_order.assert_called_once_with(**kwargs)


class TestSessionGetOrder:

    @pytest.mark.asyncio
    async def test_normal(self, mocked_session):
        mocked_session.client.get_order = MagicMock(return_value='test_order')
        assert await mocked_session._get_order('test_symbol', 'test_order_id') == 'test_order'
        mocked_session.client.get_order.assert_called_once_with(
            symbol='test_symbol', orderId='test_order_id'
        )


class TestSessionCheckOrder:

    @pytest.mark.parametrize('status', [
        'FILLED',
        'CANCELED',
        'PENDING_CANCEL',
        'REJECTED',
        'EXPIRED',
    ])
    @pytest.mark.asyncio
    async def test_failed_status(self, mocked_session, mocked_bot, mocked_user, status):
        await self.all_tests(mocked_bot, mocked_session, mocked_user, status)

    @pytest.mark.asyncio
    async def test_time_out(self, mocked_session, mocked_bot, mocked_user):
        time.time = MagicMock(side_effect=[0, 4])
        status = 'NOT_FILLED'
        await self.all_tests(mocked_bot, mocked_session, mocked_user, status)

    async def all_tests(self, mocked_bot, mocked_session, mocked_user, status):
        order = await self.run__check_order(mocked_session, mocked_user, status)
        mocked_bot.send_message.assert_awaited()
        assert mocked_bot.send_message.await_count == 2
        call_args_list = mocked_bot.send_message.await_args_list
        assert call_args_list[0].args == (mocked_user.id, f'The order status is: {status}.')
        assert call_args_list[1].args == (mocked_user.id, str(order).replace(', ', '\n'))

    @staticmethod
    async def run__check_order(mocked_session, mocked_user, status):
        order = {'status': status}
        mocked_session._get_order = AsyncMock(return_value=order)
        await mocked_session._check_order(mocked_user.id, 'test_symbol', 'test_order_id')
        return order

    @pytest.mark.parametrize('time_stamps, awaits_count', [
        ([0, 1, *list(range(4, 10))], 1),
        ([0, 1, 2, *list(range(4, 10))], 2),
        ([0, 1, 2, 3, *list(range(4, 10))], 3),
    ])
    @pytest.mark.asyncio
    async def test_loop(self, mocked_session, mocked_bot, mocked_user, time_stamps, awaits_count):
        time.time = MagicMock(side_effect=time_stamps)
        asyncio.sleep = AsyncMock()
        status = 'NOT_FILLED'
        await self.run__check_order(mocked_session, mocked_user, status)
        assert asyncio.sleep.await_count == awaits_count


class TestSessionTestOrder:

    @pytest.mark.asyncio
    async def test_passed(self, mocked_session, mocked_bot, mocked_user):
        mocked_session._is_tested = AsyncMock(return_value=True)
        await self.run_test_order(mocked_session, mocked_user)
        mocked_bot.send_message.assert_awaited_once_with(mocked_user.id,
                                                         'The order has been verified.')

    @pytest.mark.asyncio
    async def test_failed(self, mocked_session, mocked_bot, mocked_user):
        mocked_session._is_tested = AsyncMock(return_value=None)
        await self.run_test_order(mocked_session, mocked_user)
        mocked_bot.send_message.assert_not_awaited()

    @staticmethod
    async def run_test_order(mocked_session, mocked_user):
        kwargs = {'test_key1': 'test_val1', 'test_key2': 'test_val2'}
        assert await mocked_session.test_order(mocked_user.id, **kwargs) is None
        mocked_session._is_tested.assert_awaited_once_with(mocked_user.id, **kwargs)


class TestSessionCreateOrder:

    @pytest.mark.asyncio
    async def test_created(self, mocked_session, mocked_bot, mocked_user):
        order = {'symbol': 'test_symbol', 'orderId': 'test_orderId'}
        kwargs = {'test_key1': 'test_val1', 'test_key2': 'test_val2'}
        mocked_session._is_tested = AsyncMock(return_value=True)
        mocked_session._check_order = AsyncMock(return_value=None)
        mocked_session.client.create_order = MagicMock(return_value=order)
        assert await mocked_session.create_order(mocked_user.id, **kwargs) is None
        mocked_session.client.create_order.assert_called_once_with(**kwargs)
        mocked_bot.send_message.assert_awaited_once_with(
            mocked_user.id, 'The order has been created.')
        mocked_session._check_order.assert_awaited_once_with(
            mocked_user.id, order['symbol'], order['orderId'])

    @pytest.mark.asyncio
    async def test_not_created(self, mocked_session, mocked_bot, mocked_user):
        kwargs = {'test_key1': 'test_val1', 'test_key2': 'test_val2'}
        mocked_session._is_tested = AsyncMock(return_value=None)
        assert await mocked_session.create_order(mocked_user.id, **kwargs) is None
        mocked_session._is_tested.assert_called_once_with(mocked_user.id, **kwargs)
        mocked_bot.send_message.assert_not_awaited()


if __name__ == '__main__':
    pass
