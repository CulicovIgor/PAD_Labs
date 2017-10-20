import asyncio
import json

from src.logic.queue_logic import _MESSAGE_QUEUE
from src.logic.queue_logic import static_topics
from src.logic.queue_logic import dynamic_topics
from src.logic.subscribers import add_sub


@asyncio.coroutine
def handle_command(topic, payload):
    msg = ''
    if topic == '':
        yield from _MESSAGE_QUEUE.put(payload)
    elif topic in static_topics.keys():
        yield from static_topics[topic].put(payload)
    elif topic in dynamic_topics.keys():
        yield from dynamic_topics[topic].put(payload)
    else:
        dynamic_topics[topic] = asyncio.Queue(loop=asyncio.get_event_loop())
        yield from dynamic_topics[topic].put(payload)
        msg = 'OK'

    return {
        'type': 'response',
        'payload': msg

    }


@asyncio.coroutine
def dispatch_message(message):
    topic = message.get('topic')
    response = yield from handle_command(topic, message.get('payload'))
    return response


@asyncio.coroutine
def handle_message(reader, writer):
    if reader.at_eof():
        print("No data")
    else:
        data = yield from reader.read()
        address = writer.get_extra_info('peername')
        print('Recevied message from ', address)
        try:
            message = json.loads(data.decode('utf-8'))
        except ValueError as e:
            print('Invalid message received')
            send_error(writer, str(e))
            return

        message_type = message.get('type')
        print('Dispatching command ', message_type)
        if message_type == 'send':
            try:
                response = yield from dispatch_message(message)
                payload = json.dumps(response).encode('utf-8')
                writer.write(payload)
                yield from writer.drain()
                writer.write_eof()
            except ValueError as e:
                print('Cannot process the message.')
                send_error(writer, str(e))
                writer.close()
        else:
            topic = message.get('topic')
            add_sub(topic, writer)


@asyncio.coroutine
def send_error(writer, reason):
    message = {
        'type': 'error',
        'payload': reason
    }
    payload = json.dumps(message).encode('utf-8')
    writer.write(payload)
    yield from writer.drain()
