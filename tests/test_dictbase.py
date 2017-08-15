import unittest
import asyncio
from unittest.mock import patch, Mock

from tests.common import async_test, get_mock_coro, get_mock_coro_pop_list
import wordbook


class TestDictBaseConnect(unittest.TestCase):

    def setUp(self):
        self.dictbase = wordbook.dictbase.DictBase()
        mock_reader = Mock()
        mock_reader.readline = get_mock_coro(b"220 my mock-dictd <mock.capabilities> <mock-msg-id>\r\n")
        self.mock_open_connection = get_mock_coro((mock_reader, Mock()))
        patch('wordbook.dictbase.asyncio.open_connection', self.mock_open_connection).start()

    def tearDown(self):
        patch.stopall()

    @async_test
    def test_connect_host(self):
        yield from self.dictbase.connect('10.11.12.13', 9999)

        self.assertTrue(self.dictbase.connected)
        self.assertEqual(self.dictbase.msg_id, '<mock-msg-id>')
        self.mock_open_connection.assert_called_once_with('10.11.12.13', 9999)

    @async_test
    def test_connect_default(self):
        yield from self.dictbase.connect()

        self.assertTrue(self.dictbase.connected)
        self.assertEqual(self.dictbase.msg_id, '<mock-msg-id>')
        self.mock_open_connection.assert_called_once_with('127.0.0.1', 2628)


class TestDictBaseCommands(unittest.TestCase):

    def setUp(self):
        self.dictbase = wordbook.dictbase.DictBase()
        self.dictbase.writer = Mock()
        self.dictbase.writer.drain = get_mock_coro(None)
        self.dictbase.reader = Mock()

    def tearDown(self):
        patch.stopall()

    @async_test
    def test_client(self):
        self.dictbase.reader.readline = get_mock_coro(b"250 ok\r\n")

        ret = yield from self.dictbase.client('mock-client')

        self.assertIsNone(ret)
        self.dictbase.writer.write.assert_called_once_with(b'CLIENT mock-client\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_show_db_empty(self):
        self.dictbase.reader.readline = get_mock_coro(b"554 No databases\r\n")

        ret = yield from self.dictbase.show_db()

        self.assertEqual(ret, [])
        self.dictbase.writer.write.assert_called_once_with(b'SHOW DB\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_show_db_present(self):
        resp = [b'110 1 databases present\r\n', 
                b'db1 "Database 1"\r\n',
                b'db2 "Database 2"\r\n',
                b'.\r\n',
                b'250 ok\r\n']
        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.show_db()
        self.assertEqual(ret, ['db1 "Database 1"', 'db2 "Database 2"'])

    @async_test
    def test_show_info(self):
        resp = [b'112 information for db1\r\n',
                b'============ db1 ============\r\n',
                b'mock mock mock mock mock mock\r\n',
                b'=============================\r\n',
                b'.\r\n',
                b'250 ok\r\n']
        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.show_info('db1')

        self.assertEqual(ret, ['============ db1 ============',
                               'mock mock mock mock mock mock',
                               '============================='])

        self.dictbase.writer.write.assert_called_once_with(b'SHOW INFO db1\r\n') 

    @async_test
    def test_show_strat(self):
        resp = [b'111 12 strategies present\r\n',
                b'exact "Match headwords exactly"\r\n',
                b'prefix "Match prefixes"\r\n',
                b'.\r\n',
                b'250 ok\r\n']
        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.show_strat()

        self.assertEqual(ret, ['exact "Match headwords exactly"', 'prefix "Match prefixes"'])
        self.dictbase.writer.write.assert_called_once_with(b'SHOW STRAT\r\n')

    @async_test
    def test_show_server(self):
        resp = [b'114 server information\r\n',
                b'dictd 1.12.1/rf on Linux 4.10.0-27-generic\r\n',
                b'.\r\n',
                b'250 ok\r\n']
        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.show_server()

        self.assertEqual(ret, ['dictd 1.12.1/rf on Linux 4.10.0-27-generic'])
        self.dictbase.writer.write.assert_called_once_with(b'SHOW SERVER\r\n')

    @async_test
    def test_status(self):
        self.dictbase.reader.readline = get_mock_coro(b"210 status mock/mock/mock\r\n")

        ret = yield from self.dictbase.status()

        self.assertEqual(ret, 'status mock/mock/mock')
        self.dictbase.writer.write.assert_called_once_with(b'STATUS\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_help(self):
        resp = [b'113 help text follows\r\n',
                b'mock help line 1\r\n',
                b'line 2\r\n',
                b'.\r\n',
                b'250 ok\r\n']
        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.help()

        self.assertEqual(ret, ['mock help line 1', 'line 2'])
        self.dictbase.writer.write.assert_called_once_with(b'HELP\r\n')

    @async_test
    def test_quit(self):
        self.dictbase.reader.readline = get_mock_coro(b"221 bye [d/m/c = 0/0/0; 3.000r 0.000u 0.000s]")

        ret = yield from self.dictbase.quit()

        self.assertIsNone(ret)
        self.dictbase.writer.write.assert_called_once_with(b'QUIT\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_option_mime(self):
        self.dictbase.reader.readline = get_mock_coro(b"250 mock - using MIME headers")

        ret = yield from self.dictbase.option_mime()

        self.assertEqual(ret, 'mock - using MIME headers')
        self.dictbase.writer.write.assert_called_once_with(b'OPTION MIME\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_define_no_match(self):
        self.dictbase.reader.readline = get_mock_coro(b"552 no match [d/m/c = 0/0/52; 0.000r 0.000u 0.000s]")

        ret = yield from self.dictbase.define('db1', 'mock rock')

        self.assertEqual(ret, [])
        self.dictbase.writer.write.assert_called_once_with(b'DEFINE db1 "mock rock"\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_define_return(self):

        resp = [b'150 2 definitions retrieved\r\n',
				b'151 "The" db1 "The db1 mock\r\n"',
				b'mock from db1 line 1\r\n',
				b'mock from db1 line 2\r\n',
				b'.\r\n',
				b'151 "The" db9 "The mock db9"\r\n',
				b'mock from db2\r\n',
				b'.\r\n',
				b'250 ok\r\n']

        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.define('*', 'mock')

        self.assertEqual(ret, ['["The" db1 "The db1 mock\r]',
                               'mock from db1 line 1',
                               'mock from db1 line 2',
                               '["The" db9 "The mock db9"]',
                               'mock from db2'])

        self.dictbase.writer.write.assert_called_once_with(b'DEFINE * "mock"\r\n') 

    @async_test
    def test_match_no_match(self):
        self.dictbase.reader.readline = get_mock_coro(b"552 no match [d/m/c = 0/0/52; 0.000r 0.000u 0.000s]")

        ret = yield from self.dictbase.match('db1', 'strategy1', 'mock rock')

        self.assertEqual(ret, [])
        self.dictbase.writer.write.assert_called_once_with(b'MATCH db1 strategy1 "mock rock"\r\n') 
        self.dictbase.reader.readline.assert_called_once_with()

    @async_test
    def test_match_return(self):

        resp = [b'152 3 matches found\r\n',
                b'db1 "Abode\r\n',
                b'db1 "Abide\r\n',
                b'db2 "abide\r\n',
				b'.\r\n',
				b'250 ok\r\n']

        self.dictbase.reader.readline = get_mock_coro_pop_list(resp)

        ret = yield from self.dictbase.match('*', '.', 'mock')

        self.assertEqual(ret, ['db1 "Abode', 'db1 "Abide', 'db2 "abide'])
        self.dictbase.writer.write.assert_called_once_with(b'MATCH * . "mock"\r\n') 


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
