import asyncio
import argparse
import re
import logging

import wordbook


def parse_args():
    parser = argparse.ArgumentParser(description='WordSearch - find definition of words')
    parser.add_argument('-c', '--host')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('-b', '--database')
    parser.add_argument('-s', '--strategy')
    parser.add_argument('--debug', action='store_true')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--match')
    group.add_argument('-d', '--define')
    group.add_argument('--list-databases', action='store_true')
    group.add_argument('--list-strategies', action='store_true')
    return parser.parse_args()


def print_line(line):

    line, numr = re.subn(r'^\[(.*)\]\s*$', '\n\x1b[1;33m\\1\x1b[0m\n', line)
    if numr > 0:
        print(line)
        return

    line = re.sub(r'(\[[^\]]+\])', '\x1b[0;33m\\1\x1b[0m', line)
    line = re.sub(r'({[^}]+})', '\x1b[0;36m\\1\x1b[0m', line)
    print(line)


async def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    wb = wordbook.WordBook(host=args.host,
                           port=args.port,
                           database=args.database,
                           strategy=args.strategy)
    await wb.connect()

    if args.list_databases:
        dbs = await wb.get_databases()
        for db in dbs:
            print("{:30} {}".format(*db.get_database()))

    elif args.list_strategies:
        sgs = await wb.get_strategies()
        for sg in sgs:
            print("{:30} {}".format(*sg.get_strategy()))

    elif args.match is not None:
        matches = await wb.match(args.match)

        if matches:
            for match in matches:
                print("{:30} {}".format(*match.split(' ', 1)))
        else:
            print('No match found')

    elif args.define is not None:
        defines = await wb.define(args.define)

        if defines:
            for define in defines:
                print_line(define)
            print()
        else:
            print('No definition found')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
