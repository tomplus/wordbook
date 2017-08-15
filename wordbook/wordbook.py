import asyncio

from wordbook import DictBase


class WordBook:

    def __init__(self, host=None, port=None, database=None, strategy=None):
        self.host = host
        self.port = port
        self.conn = DictBase()
        self.database = database
        self.strategy = strategy

    def init_copy(self, source):
        self.host = source.host
        self.port = source.port
        self.conn = source.conn
        self.database = source.database
        self.strategy = source.strategy

    async def connect(self):
        await self.conn.connect(self.host, self.port)
        await self.conn.client('wordbook')

    async def get_databases(self):
        dbs = await self.conn.show_db()
        ret = []
        for dbn in dbs:
            ret.append(WordBookDatabase(dbn, self))
        return ret

    async def get_strategies(self):
        strats = await self.conn.show_strat()
        ret = []
        for strat in strats:
            ret.append(WordBookStrategy(strat, self))
        return ret

    async def match(self, query):
        database = self.get_database()[0]
        strategy = self.get_strategy()[0]
        ret = await self.conn.match(database, strategy, query)
        return ret

    async def define(self, word):
        database = self.get_database()[0]
        ret = await self.conn.define(database, word)
        return ret

    def get_database(self):
        if self.database is not None:
            return self.database.split(' ', 1)
        return ['*', '<all>']

    def get_strategy(self):
        if self.strategy is not None:
            return self.strategy.split(' ', 1)
        return ['.', '<default>']


class WordBookDatabase(WordBook):

    def __init__(self, database, base=None):
        if base is None:
            super().__init__()
        else:
            self.init_copy(base)
        self.database = database


class WordBookStrategy(WordBook):

    def __init__(self, strategy, base=None):
        if base is None:
            super().__init__()
        else:
            self.init_copy(base)
        self.strategy = strategy
