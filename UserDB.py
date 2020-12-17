import pandas as pd
from pathlib import Path
import pickle
import numpy as np
import bnnc


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


    def _add_user(self, user_id, username, ):
        """
        Add new user to the database
        :param user_id:
        :param username:
        :return:
        """
        user_dict = {'user_id': user_id,
                     'username': username,
                     'sessions': bnnc.Sessions(),
                     'state': False}
        ind = len(self.index)
        data = np.array(list(user_dict.values()), dtype=object)
        self.loc[ind] = data

    def get_state(self, user_id=None):
        """
        Get user state
        :param user_id:
        :return:
        """
        if user_id:
            if self._is_userid_exists(user_id):
                return self.loc[self['user_id'] == user_id, 'state'].values[0]
            else:
                raise ValueError(f'There are no such user_id: |{user_id}| in database')
        else:
            return self.loc[:, ['user_id', 'username', 'state']]

    def set_state(self, user_id, state):
        """
        Set state for the user
        :param user_id:
        :param state:
        :return:
        """
        if self._is_userid_exists(user_id):
            if isinstance(state, bool):
                self.loc[self['user_id'] == user_id, 'state'] = state
            else:
                raise TypeError(f'state variable should be bool, not {type(state)}')
        else:
            print('At first you should add API')
            # TODO: Сообщение, что надо сначала добавить API
            pass

    def _add_session(self, user_id, session):
        """
        Adds new session to sessions store
        :param user_id:
        :param session:
        :return:
        """
        sessions = self.loc[self['user_id'] == user_id, 'sessions'].tolist()[0]
        sessions.append(session)
        # TODO: Сообщение в телегу, что сессия добавлена

    def _is_userid_exists(self, user_id):
        """
        Check if userid exists
        :param user_id:
        :return:
        """
        users_id = self.loc[:, 'user_id'].values
        if user_id in users_id:
            return True
        return False

    def _is_session_exists(self, user_id, api, api_key):
        """
        Check if session exists
        :param user_id:
        :param api:
        :param api_key:
        :return:
        """
        sessions = self.loc[self['user_id'] == user_id, 'sessions'].values[0]
        for session in sessions:
            if session.api_key == api_key and session.api == api:
                return True
            return False

    def _is_new_user(self, user_id, username):
        """
        Check if user is new.
        :param user_id:
        :param username:
        :return:
        """
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

    def create_session(self, user_id, username, api, api_key, s_key):
        """
        Creates new session
        :param user_id:
        :param username:
        :param api:
        :param api_key:
        :param s_key:
        :return:
        """
        if self._is_new_user(user_id, username):
            self._add_user(user_id, username)
            session = bnnc.Session(api, api_key, s_key)
            self._add_session(user_id, session)
        else:
            if not self._is_session_exists(user_id, api, api_key):
                session = bnnc.Session(api, api_key, s_key)
                self._add_session(user_id, session)
                # TODO: Сообщение в телегу, что сессия создана
            else:
                pass
                # TODO: Сообщение в телегу, что такая сессия уже существует


if __name__ == '__main__':
    a = UserDB()
    a.create_session(123, 'sdfdsf', 'binance', 'jdso98u9dsa', 'jdfdojodsoi88')
    a.create_session(123, 'sdfdsf', 'binance', 'jddfdsfdssa', 'jdfdojodsoi88')
    a.create_session(1234, 'sdfdssdff', 'bitmax', 'jddfdsssa', 'jdfdojodsoi88')
    a.create_session(1234, 'sdfdssdff', 'bitmax', 'jddfdsssa', 'jdfdojodsoi88')
    a.get_state(123)
    a.get_state()
    a.set_state(123, True)
    a.set_state(1234, False)
    a.save()
    b = UserDB()
