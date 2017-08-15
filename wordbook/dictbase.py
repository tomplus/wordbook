import asyncio
import re
import enum
import logging

from wordbook.exceptions import DictError, DictConnectionError, InvalidDatabase, InvalidStrategy


class ResponseCodes(enum.IntEnum):

    DATABASES_PRESENT = 110
    STRATEGIES_AVAILABLE = 111
    DATABASE_INFORMATION = 112
    HELP_TEXT = 113
    SERVER_INFORMATION = 114

    CHALLENGE_FOLLOWS = 130

    DEFINITIONS_RETRIEVED = 150
    WORD_DATABASE = 151
    MATCHES_FOUND = 152

    STATUS_INFO = 210
    CONNECT_ACCEPTED = 220
    AUTHENTICATION_SUCCESSFUL = 230
    CONECTION_CLOSING = 221
    OK = 250

    SEND_RESPONSE = 330

    SERVER_TEMPORARILY_UNAVAILABLE = 420
    SERVER_SHUTTING_DOWN = 421

    SYNTAX_ERROR_COMMAND = 500
    SYNTAX_ERROR_PARAMETERS = 501
    COMMAND_NOT_IMPLEMENTED = 502
    PARAMETER_NOT_IMPLEMENTED = 503
    ACCESS_DENIED_USER = 530
    ACCESS_DENIED_COMMAND = 531
    ACCESS_DENIED_UNKNOWN_MECHANISM = 532

    INVALID_DATABASE = 550
    INVALID_STRATEGY = 551
    NO_MATCH = 552
    NO_DATABASES_PRESENT = 554
    NO_STRATEGIES_AVAILABLE = 555

    UNKNOWN_ERROR = 599


class DictBase:

    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 2628

    def __init__(self):
        self.connected = False
        self.host = None
        self.port = None
        self.capabilities = None
        self.msg_id = None
        self.reader = None
        self.writer = None

    async def connect(self, host=None, port=None):

        if host is not None:
            self.host = host
        else:
            self.host = self.DEFAULT_HOST

        if port is not None:
            self.port = port
        else:
            self.port = self.DEFAULT_PORT

        logging.debug('Connect: %s %s', self.host, self.port)

        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        response = await self.reader.readline()
        logging.debug('Recv status: %s', response)
        response = response.decode('utf8')
        response_parse = re.search(r'^(\d+)\s+(.*?)\s+(<[^>]+>)\s+(\S+)\s*', response)
        if response_parse:
            code, text, self.capabilities, self.msg_id = response_parse.groups()
            if int(code) != ResponseCodes.CONNECT_ACCEPTED:
                raise DictConnectionError(code, text)
            self.connected = True
        else:
            raise DictConnectionError(ResponseCodes.UNKNOWN_ERROR, response)

    async def client(self, text):
        await self.send_command('CLIENT {}\r\n'.format(text))
        code, response, _ = await self.recv_response()
        if code == ResponseCodes.OK:
            return
        raise DictError(code, response)

    async def auth(self, username, authentication_string):
        raise NotImplementedError()

    async def show_db(self):
        await self.send_command('SHOW DB\r\n')
        code, response, body = await self.recv_response()
        if code == ResponseCodes.DATABASES_PRESENT:
            return body
        elif code == ResponseCodes.NO_DATABASES_PRESENT:
            return []
        raise DictError(code, response)

    async def show_info(self, database):
        await self.send_command('SHOW INFO {}\r\n'.format(database))
        code, response, body = await self.recv_response()
        if code == ResponseCodes.DATABASE_INFORMATION:
            return body
        elif code == ResponseCodes.INVALID_DATABASE:
            raise InvalidDatabase(code, response)
        raise DictError(code, response)

    async def show_strat(self):
        await self.send_command('SHOW STRAT\r\n')
        code, response, body = await self.recv_response()
        if code == ResponseCodes.STRATEGIES_AVAILABLE:
            return body
        elif code == ResponseCodes.NO_STRATEGIES_AVAILABLE:
            return []
        raise DictError(code, response)

    async def show_server(self):
        await self.send_command('SHOW SERVER\r\n')
        code, response, body = await self.recv_response()
        if code == ResponseCodes.SERVER_INFORMATION:
            return body
        raise DictError(code, response)

    async def status(self):
        await self.send_command('STATUS\r\n')
        code, response, _ = await self.recv_response()
        if code == ResponseCodes.STATUS_INFO:
            return response
        raise DictError(code, response)

    async def help(self):
        await self.send_command('HELP\r\n')
        code, response, body = await self.recv_response()
        if code == ResponseCodes.HELP_TEXT:
            return body
        raise DictError(code, response)

    async def quit(self):
        await self.send_command('QUIT\r\n')
        code, response, _ = await self.recv_response()
        if code == ResponseCodes.CONECTION_CLOSING:
            self.writer.close()
            self.connected = False
            return
        raise DictError(code, response)

    async def option_mime(self):
        await self.send_command('OPTION MIME\r\n')
        code, response, _ = await self.recv_response()
        if code == ResponseCodes.OK:
            return response
        raise DictError(code, response)

    async def define(self, database, word):
        await self.send_command('DEFINE {} "{}"\r\n'.format(database, word))
        code, response, body = await self.recv_response()
        if code == ResponseCodes.NO_MATCH:
            return []
        elif code == ResponseCodes.DEFINITIONS_RETRIEVED:
            return body
        elif code == ResponseCodes.INVALID_DATABASE:
            raise InvalidDatabase(code, response)
        raise DictError(code, response)

    async def match(self, database, strategy, word):
        await self.send_command('MATCH {} {} "{}"\r\n'.format(database, strategy, word))
        code, response, body = await self.recv_response()
        if code == ResponseCodes.NO_MATCH:
            return []
        elif code == ResponseCodes.MATCHES_FOUND:
            return body
        elif code == ResponseCodes.INVALID_DATABASE:
            raise InvalidDatabase(code, response)
        elif code == ResponseCodes.INVALID_STRATEGY:
            raise InvalidStrategy(code, response)
        raise DictError(code, response)

    async def send_command(self, command):
        logging.debug('Send command: %s', command)
        self.writer.write(command.encode())
        await self.writer.drain()

    async def recv_response(self):

        # read status
        status_line = await self.reader.readline()
        code, response = status_line.decode('utf8').rstrip().split(' ', 1)

        logging.debug('Recv status: %s', status_line)

        if code[0] == '1':
            body = []
            next_status = True
            while True:
                line = await self.reader.readline()
                logging.debug('Recv line: %s', line)

                line = line.decode('utf8').rstrip()
                if line == '.':
                    next_status = True
                    continue

                if next_status:
                    rcode = re.search(r'^(\d{3}) (.*)', line)
                    if rcode is not None:
                        fin_code, fin_response = rcode.groups()
                        fin_code = int(fin_code)
                        if fin_code == ResponseCodes.OK:
                            break
                        elif fin_code in (ResponseCodes.DEFINITIONS_RETRIEVED, ResponseCodes.WORD_DATABASE):
                            body.append('[{}]'.format(fin_response))
                            continue

                    next_status = False

                body.append(line)

        else:
            body = None

        return int(code), response, body
