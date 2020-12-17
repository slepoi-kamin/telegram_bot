import pathlib
import pickle
import typing
import json
from awaits.awaitable import awaitable

from aiogram.contrib.fsm_storage.memory import MemoryStorage


class _FileStorage(MemoryStorage):
    def __init__(self, path: typing.Union[pathlib.Path, str]):
        """
        :param path: file path
        """
        super(_FileStorage, self).__init__()
        path = self.path = pathlib.Path(path)

        try:
            self.data = self.read(path)
        except FileNotFoundError:
            pass

    async def save(self):
        await self.write(self.path)

    async def close(self):
        if self.data:
            await self.save()
        await super(_FileStorage, self).close()

    def read(self, path: pathlib.Path):
        raise NotImplementedError

    @awaitable
    def write(self, path: pathlib.Path):
        raise NotImplementedError


class JSONStorage(_FileStorage):
    """
    JSON File storage based on MemoryStorage
    """

    def read(self, path: pathlib.Path):
        with path.open('r') as f:
            return json.load(f)

    @awaitable
    def write(self, path: pathlib.Path):
        with path.open('w') as f:
            return json.dump(self.data, f, indent=4)


class PickleStorage(_FileStorage):
    """
    Pickle File storage based on MemoryStorage
    """

    def read(self, path: pathlib.Path):
        with path.open('rb') as f:
            return pickle.load(f)

    @awaitable
    def write(self, path: pathlib.Path):
        with path.open('wb') as f:
            return pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)