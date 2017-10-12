import asyncio
import json
import random

topics = {
    0: "",
    1: "ect",
    2: "lab",
    3: "random",
    4: "pad"
}


@asyncio.coroutine
def get_message(loop):
    reader, writer = yield from asyncio.open_connection(
        '127.0.0.1', 14141, loop=loop
    )
    writer.write(json.dumps({
        'type': 'read',
        'topic': topics[topic_number]
    }).encode('utf-8'))
    print(json.dumps({
        'type': 'read',
        'topic': topics[topic_number]
    }).encode('utf-8'))
    writer.write_eof()
    yield from writer.drain()
    response = yield from reader.read()
    writer.close()
    return response


@asyncio.coroutine
def run_receiver(loop):
    while True:
        try:
            print("try")
            response = yield from get_message(loop)
            print('Received %s', response)
        except KeyboardInterrupt:
            break


def main():
    global topic_number
    topic_number = random.randint(0, 4)
    print("Topic: ", topics[topic_number])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_receiver(loop))


if __name__ == '__main__':
    main()
