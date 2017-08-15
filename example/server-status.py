import asyncio
import argparse
import logging

import wordbook


def parse_args():
    parser = argparse.ArgumentParser(description='Dump stats from DICT server')
    parser.add_argument('-c', '--host')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


async def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    dictb = wordbook.DictBase()
    await dictb.connect(args.host, args.port)
    await dictb.client('wordbook/server-status.py')
    print('-' * 80)
    info = await dictb.show_server()
    for line in info:
       print(line)
    print('-' * 80)
    status = await dictb.status()
    print(status)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
