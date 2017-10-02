import asyncio
import json

from src.queue_logic.queue_logic import _MESSAGE_QUEUE
from src.queue_logic.queue_logic import static_topics
from src.queue_logic.queue_logic import dynamic_topics


@asyncio.coroutine
def handle_command(type, topic, payload):
    msg = ''
    if type == 'send':
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
    elif type == 'read':
        if topic == '':
            yield from _MESSAGE_QUEUE.get()
        elif topic in static_topics.keys():
            msg = yield from static_topics[topic].get()
        elif topic in dynamic_topics.keys():
            msg = yield from dynamic_topics[topic].get()
        else:
            print("Unhandled error")
            msg = "Error!"
    return {
        'type': 'response',
        'payload': msg

    }


@asyncio.coroutine
def dispatch_message(message):
    message_type = message.get('type')
    topic = message.get('topic')
    print('Dispatching command ', message_type)
    response = yield from handle_command(message_type, topic, message.get('payload'))
    return response


@asyncio.coroutine
def handle_message(reader, writer):
    data = yield from reader.read()
    address = writer.get_extra_info('peername')

    print('Recevied message from ', address)

    try:
        message = json.loads(data.decode('utf-8'))
    except ValueError as e:
        print('Invalid message received')
        send_error(writer, str(e))
        return

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


@asyncio.coroutine
def send_error(writer, reason):
    message = {
        'type': 'error',
        'payload': reason
    }
    payload = json.dumps(message).encode('utf-8')
    writer.write(payload)
    yield from writer.drain()