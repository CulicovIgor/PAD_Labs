import asyncio
import json
import uuid
import random

topics = {
    0: "",
    1: "ect",
    2: "lab",
    3: "random",
    4: "pad"
          }


@asyncio.coroutine
def send_message(message, loop):
    reader, writer = yield from asyncio.open_connection(
        '127.0.0.1', 14141, loop=loop
    )
    rand = random.randint(0, 4)
    payload = json.dumps({
        'type': 'send',
        'topic': topics[rand],
        'payload': message
    }).encode('utf-8')
    print("Send: ", str(payload))
    writer.write(payload)
    writer.write_eof()
    yield from writer.drain()

    response = yield from reader.read(2048)
    writer.close()
    return response


@asyncio.coroutine
def run_sender(loop):
    while True:
        try:
            message = 'UUID(%s)' % (uuid.uuid4().hex,)
            response = yield from send_message(message, loop)
            print('Received: ', response)
            yield from asyncio.sleep(1)
        except KeyboardInterrupt:
            break


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sender(loop))


if __name__ == '__main__':
    main()
