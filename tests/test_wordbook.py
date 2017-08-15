import unittest
import asyncio
from unittest.mock import patch, Mock

from tests.common import async_test, get_mock_coro, get_mock_coro_pop_list
import wordbook


class TestWordBook(unittest.TestCase):

    def setUp(self):
        self.mock_dictbase = patch('wordbook.wordbook.DictBase').start()

    def tearDown(self):
        patch.stopall()

    @async_test
    def test_connect_default(self):
        self.mock_dictbase.return_value.connect = get_mock_coro(None)
        self.mock_dictbase.return_value.client = get_mock_coro(None)
        wb = wordbook.WordBook()
        yield from wb.connect()
        self.mock_dictbase.assert_called_once_with()
        self.mock_dictbase.return_value.connect.assert_called_once_with(None, None)
        self.mock_dictbase.return_value.client.assert_called_once_with('wordbook')
        self.assertEqual(wb.get_database(), ['*', '<all>'])
        self.assertEqual(wb.get_strategy(), ['.', '<default>'])

    @async_test
    def test_connect_host(self):
        self.mock_dictbase.return_value.connect = get_mock_coro(None)
        self.mock_dictbase.return_value.client = get_mock_coro(None)
        wb = wordbook.WordBook('1.2.3.4', 5)
        yield from wb.connect()
        self.mock_dictbase.assert_called_once_with()
        self.mock_dictbase.return_value.connect.assert_called_once_with('1.2.3.4', 5)
        self.mock_dictbase.return_value.client.assert_called_once_with('wordbook')

    @async_test
    def test_get_databases(self):
        wb = wordbook.WordBook()
        self.mock_dictbase.return_value.show_db = get_mock_coro(['db "mock db"'])
        ret = yield from wb.get_databases() 
        self.mock_dictbase.return_value.show_db.assert_called_once_with()
        self.assertIsInstance(ret[0], wordbook.WordBookDatabase)
        self.assertEqual(ret[0].database, 'db "mock db"')
        self.assertEqual(ret[0].get_database(), ['db', '"mock db"'])

    @async_test
    def test_get_strategies(self):
        wb = wordbook.WordBook()
        self.mock_dictbase.return_value.show_strat = get_mock_coro(['st mock'])
        ret = yield from wb.get_strategies() 
        self.mock_dictbase.return_value.show_strat.assert_called_once_with()
        self.assertIsInstance(ret[0], wordbook.WordBookStrategy)
        self.assertEqual(ret[0].strategy, 'st mock')
        self.assertEqual(ret[0].get_strategy(), ['st', 'mock'])

    @async_test
    def test_match(self):
        wb = wordbook.WordBook()
        self.mock_dictbase.return_value.match = get_mock_coro(['mock result'])
        ret = yield from wb.match('mock query') 
        self.assertEqual(ret, ['mock result'])
        self.mock_dictbase.return_value.match.assert_called_once_with('*', '.', 'mock query')

    @async_test
    def test_define(self):
        wb = wordbook.WordBook()
        self.mock_dictbase.return_value.define = get_mock_coro(['mock result'])
        ret = yield from wb.define('mock query') 
        self.assertEqual(ret, ['mock result'])
        self.mock_dictbase.return_value.define.assert_called_once_with('*', 'mock query')


class TestWordBookFilter(unittest.TestCase):

    def setUp(self):
        self.mock_dictbase = patch('wordbook.wordbook.DictBase').start()

    def tearDown(self):
        patch.stopall()

    @async_test
    def test_database_match(self):
        wb = wordbook.WordBookDatabase('mock-db')
        self.mock_dictbase.return_value.match = get_mock_coro(['mock result'])
        ret = yield from wb.match('mock query') 
        self.assertEqual(ret, ['mock result'])
        self.mock_dictbase.return_value.match.assert_called_once_with('mock-db', '.', 'mock query')

    @async_test
    def test_strategy_match(self):
        wb = wordbook.WordBookStrategy('mock-strat')
        self.mock_dictbase.return_value.match = get_mock_coro(['mock result'])
        ret = yield from wb.match('mock query') 
        self.assertEqual(ret, ['mock result'])
        self.mock_dictbase.return_value.match.assert_called_once_with('*', 'mock-strat', 'mock query')

    @async_test
    def test_mix_match(self):
        wb_base = wordbook.WordBook()
        wb_db = wordbook.WordBookDatabase('mock-db', wb_base)
        wb_st = wordbook.WordBookStrategy('mock-st', wb_db)
        
        self.mock_dictbase.return_value.match = get_mock_coro(['mock result'])
        ret = yield from wb_st.match('mock query') 
        self.assertEqual(ret, ['mock result'])
        self.mock_dictbase.return_value.match.assert_called_once_with('mock-db', 'mock-st', 'mock query')


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
