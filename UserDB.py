import pandas as pd
from pathlib import Path
import pickle
import numpy as np
import bnnc
from aiogram import types


class UserDB(pd.DataFrame):
    db_file = Path('user_db.txt')

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

    def save(self):
        """
        Save database to .txt
        :return:
        """
        file = open(self.db_file, 'wb')
        pickle.dump(self, file)
        file.close()

    def load(self):
        """
        Load database from .txt
        :return:
        """
        file = open(self.db_file, 'rb')
        pd.DataFrame.__init__(self, pickle.load(file))
        file.close()


    def _add_user(self):
        """
        Add new user to the database
        :return:
        """
        user = types.User.get_current()

        user_dict = {'user_id': user.id,
                     'username': user.username,
                     'sessions': bnnc.Sessions(),
                     'state': False}
        ind = len(self.index)
        data = np.array(list(user_dict.values()), dtype=object)
        self.loc[ind] = data

    def get_state(self, all_users=False):
        """
        Get user state
        :param all_users:
        :return:
        """
        if not all_users:
            user_id = types.User.get_current().id
            if self._is_userid_exists():
                return self.loc[self['user_id'] == user_id, 'state'].values[0]
            else:
                raise ValueError(f'There are no such user_id: |{user_id}| in database')
        else:
            return self.loc[:, ['user_id', 'username', 'state']]

    def _set_state(self, state):
        """
        Set state for the user
        :param state:
        :return:
        """
        if self._is_userid_exists():
            if isinstance(state, bool):
                self.loc[self['user_id'] == types.User.get_current().id, 'state'] = state
            else:
                raise TypeError(f'state variable should be bool, not {type(state)}')
        else:
            print('At first you should add API')
            # TODO: Сообщение, что надо сначала добавить API
            pass

    def set_state(self):
        _set_state(True)

    def reset_state(self):
        _set_state(False)

    def _add_session(self, session):
        """
        Adds new session to sessions store
        :param session:
        :return:
        """

        sessions = self.loc[self['user_id'] == types.User.get_current().id, 'sessions'].tolist()[0]
        sessions.append(session)
        # TODO: Сообщение в телегу, что сессия добавлена

    def _is_userid_exists(self):
        """
        Check if userid exists
        :return:
        """
        users_id = self.loc[:, 'user_id'].values
        if types.User.get_current().id in users_id:
            return True
        return False

    def _is_session_exists(self, api, api_key):
        """
        Check if session exists
        :param api:
        :param api_key:
        :return:
        """
        user_id = types.User.get_current().id

        sessions = self.loc[self['user_id'] == user_id, 'sessions'].values[0]
        for session in sessions:
            if session.api_key == api_key and session.api == api:
                return True
            return False

    def _is_new_user(self):
        """
        Check if user is new.
        :return:
        """
        user = types.User.get_current()
        user_id = user.id
        username = user.username

        if self.index.to_list():
            if user_id in self['user_id'].values and username in self['username'].values:
                return False
            elif user_id in self['user_id'].values or username in self['username'].values:
                raise ValueError('user_id не соответствует username')
                # TODO: Сообщение в телегу, об ошибке, убрать исключение
            elif user_id not in self['user_id'].values and username not in self['username'].values:
                print('New user')
                return True
            else:
                raise ValueError('something with user_id and username')
        else:
            print('New user')
            return True

    def create_session(self, api, api_key, s_key):
        """
        Creates new session
        :param api:
        :param api_key:
        :param s_key:
        :return:
        """
        if self._is_new_user():
            self._add_user()
            session = bnnc.Session(api, api_key, s_key)
            self._add_session(session)
        else:
            if not self._is_session_exists(api, api_key):
                session = bnnc.Session(api, api_key, s_key)
                self._add_session(session)
                # TODO: Сообщение в телегу, что сессия создана
            else:
                pass
                # TODO: Сообщение в телегу, что такая сессия уже существует


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
