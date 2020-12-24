from typing import Any, Union

import pandas as pd
from pathlib import Path
import pickle
import numpy as np
from awaits.awaitable import awaitable
import typing

import bnnc
from aiogram import types, Bot

from conf import admin_id
from keyboards import keyboards


class UserDB(pd.DataFrame):
    db_file: Union[Path, Any] = Path('user_db.txt')

    def __init__(self):
        if self.db_file.exists():
            self.load()
        else:
            self._create_new()

    def _create_new(self):
        user_dict = {'user_id': [],
                     'username': [],
                     'sessions': [],
                     'state': []}
        pd.DataFrame.__init__(self, user_dict)

    async def clear(self):
        self._create_new()
        await self.save()
        await Bot.get_current().send_message(admin_id, f'The User Database have been cleared')

    @awaitable
    def save(self, fname: Union[Path, Any] = None):
        """
        Save database to .txt
        :type fname: Union[Path, Any]
        :return:
        """
        if fname:
            file = open(fname, 'wb')
        else:
            file = open(self.db_file, 'wb')
        pickle.dump(self, file)
        file.close()

    async def backup(self):
        if self.db_file.exists():
            await self.save(Path(self.db_file.name.split('.')[0] + '.bckp'))
            await Bot.get_current().send_message(admin_id, 'User database backup has been done.')

    def load(self):
        """
        Load database from .txt
        :return:
        """
        file = open(self.db_file, 'rb')
        pd.DataFrame.__init__(self, pickle.load(file))
        file.close()

    async def add_user(self, user_id=None, username=None):
        """
        Add new user to the database
        :return:
        """
        if not user_id or not username:
            user_id, username = self._get_user()

        if self.is_userid_exists(user_id):
            await Bot.get_current().send_message(admin_id,
                                                 f'ERROR: user with user_id {user_id} already exists',
                                                 reply_markup=keyboards['common_keyboard'])
        else:
            user_dict = {'user_id': user_id,
                         'username': username,
                         'sessions': bnnc.Sessions(),
                         'state': False}
            ind = len(self.index)
            data = np.array(list(user_dict.values()), dtype=object)
            self.loc[ind] = data
            await self.save()
            await Bot.get_current().send_message(admin_id,
                                                 f'New user id: {user_id}, '
                                                 f'name:{username} added to the database',
                                                 reply_markup=keyboards['common_keyboard'])

    @staticmethod
    def _get_user():
        user = types.User.get_current()
        user_id = user.id
        username = user.username
        return user_id, username

    def _get_state(self, user_id=None):
        if not user_id:
            user_id = types.User.get_current().id

        if self.is_userid_exists(user_id):
            return self.loc[self['user_id'] == user_id, 'state'].values[0]
        else:
            return None

    def get_state(self, user_id=None):
        """
        Get user state
        :param all_users:
        :return:
        """
        if not user_id:
            user_id = types.User.get_current().id

        if user_id == 'all':
            return self.loc[:, ['user_id', 'username', 'state']]
        else:
            return self._get_state(user_id)

    async def _set_state(self, state):
        """
        Set state for the user
        :param state:
        :return:
        """
        bot = Bot.get_current()
        user_id = types.User.get_current().id
        if self.is_userid_exists() and self._is_session_exists():
            if isinstance(state, bool) or state == 'test':
                self.loc[self['user_id'] == user_id, 'state'] = state
                await self.save()
                text = ('Test trading' if state == 'test' else 'Start trading') if state else 'Stop trading'
                await bot.send_message(user_id, text)
            else:
                raise TypeError(f'state variable should be bool or \'test\', not {type(state)}')
        else:
            # print('At first you should add API')
            await bot.send_message(user_id, 'At first you should add API')
            pass

    async def test_state(self):
        await self._set_state('test')

    async def set_state(self):
        await self._set_state(True)

    async def reset_state(self):
        await self._set_state(False)

    async def _add_session(self, session):
        """
        Adds new session to sessions store
        :param session:
        :return:
        """

        user_id = types.User.get_current().id
        sessions = self.loc[self['user_id'] == user_id, 'sessions'].tolist()[0]
        sessions.append(session)
        await self.save()
        await Bot.get_current().send_message(user_id, 'New session added')

    def is_userid_exists(self, user_id=None):
        """
        Check if userid exists
        :return:
        """
        if not user_id:
            user_id, _ = self._get_user()

        users_id = self.loc[:, 'user_id'].values
        if user_id in users_id:
            return True
        return False

    def _is_username_exists(self, username=None):
        """
        Check if userid exists
        :return:
        """
        if not username:
            user_id, _ = self._get_user()

        usernames = self.loc[:, 'username'].values
        if username in usernames:
            return True
        return False

    def _is_session_exists(self, api=None, api_key=None, user_id=None):
        """
        Check if session exists
        :param api:
        :param api_key:
        :return:
        """
        if not user_id:
            user_id = types.User.get_current().id
        sessions = self.loc[self['user_id'] == user_id, 'sessions'].values[0]

        if api and api_key:
            for session in sessions:
                if session.api_key == api_key and session.api == api:
                    return True
                return False
        elif api and not api_key:
            for session in sessions:
                if session.api == api:
                    return True
                return False
        else:
            return True if len(sessions) != 0 else False

    async def is_new_user(self, user_id=None, username=None):
        """
        Check if user is new.
        :return:
        """
        if not user_id or not username:
            user_id, username = self._get_user()

        if self.index.to_list():
            if self.is_userid_exists(user_id) and self._is_username_exists(username):
                return False
            elif self.is_userid_exists(user_id) or self._is_username_exists(username):
                await Bot.get_current().send_message(user_id, 'ERROR: user_id don\'t match username')
            elif not self.is_userid_exists(user_id) and not self._is_username_exists(username):
                return True
            else:
                raise ValueError('something with user_id and username')
        else:
            return True

    async def create_session(self, api, api_key, s_key):
        """
        Creates new session
        :param api:
        :param api_key:
        :param s_key:
        :return:
        """
        if await self.is_new_user():
            await self.add_user()

        if not self._is_session_exists(api, api_key):
            session = bnnc.Session(api, api_key, s_key)
            if await session.is_api_correct():
                await self._add_session(session)
        else:
            bot = Bot.get_current()
            user_id = types.User.get_current().id
            await bot.send_message(user_id, 'Session already exists')

    def _get_sessions_list(self, user_id=None):
        if not user_id:
            user_id, _ = self._get_user()

        if self._is_session_exists(user_id=user_id):
            return self.loc[self['user_id'] == user_id, 'sessions'].values[0]
        else:
            return None

    async def del_session(self, api, user_id=None):
        if not user_id:
            user_id, _ = self._get_user()
        session = self._get_session(api, user_id=user_id)
        if session:
            sessions = self._get_sessions_list(user_id)
            sessions.pop(sessions.index(session))
            await Bot.get_current().send_message(user_id, f'API session has been deleted.')
            await self.get_sessions_list(user_id)
        else:
            await Bot.get_current().send_message(user_id, f'There are no existing API sessions.')

    async def get_sessions_list(self, user_id=None):
        if not user_id:
            user_id, _ = self._get_user()

        sessions = self._get_sessions_list(user_id)
        if sessions:
            str_sessions = ''.join(list(map(lambda ses: '\n' + str(ses.api), sessions)))
            await Bot.get_current().send_message(user_id, f'Existing API sessions list: {str_sessions}')
        else:
            await Bot.get_current().send_message(user_id, f'There are no existing API sessions.')

    def _get_session(self, api, user_id=None):
        if not user_id:
            user_id = types.User.get_current().id
        if self._is_session_exists(api=api, user_id=user_id):
            sessions = self.loc[self['user_id'] == user_id, 'sessions'].values[0]
            for session in sessions:
                if session.api == api:
                    return session
        return None

    def _check_kwargs(self, user_id, **kwargs):
        exchange = kwargs['exchange']
        session = self._get_session(exchange, user_id=user_id)

        new_kwargs = {}  # Create dict with kwargs for order
        if 'PERP' in kwargs['symbol']:
            new_kwargs['symbol'] = kwargs['symbol'].replace('PERP', '')
        else:
            new_kwargs['symbol'] = kwargs['symbol']

        new_kwargs['side'] = kwargs['side']
        new_kwargs['quantity'] = kwargs['quantity']
        new_kwargs['type'] = 'MARKET'

        return session, new_kwargs

    async def create_order(self, user_id,  **kwargs):
        session, kwargs = self._check_kwargs(user_id, **kwargs)
        if session:
            if self._get_state(user_id) == 'test':
                await session.test_order(user_id, **kwargs)
            elif self._get_state(user_id):
                await session.create_order(user_id, **kwargs)
        else:
            await Bot.get_current().send_message(user_id, f'There are no sessions with API {kwargs["exchange"]}')


if __name__ == '__main__':
    a = UserDB()
    a.create_session('binance', 'jdso98u9dsa', 'jdfdojodsoi88')
    a.create_session('binance', 'jddfdsfdssa', 'jdfdojodsoi88')
    a.create_session('bitmax', 'jddfdsssa', 'jdfdojodsoi88')
    a.create_session('bitmax', 'jddfdsssa', 'jdfdojodsoi88')
    a.get_state(123)
    a.get_state()
    a.set_state(123, True)
    a.set_state(1234, False)
    a.save()
    b = UserDB()
