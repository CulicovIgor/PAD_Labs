import asyncio

from src.logic.queue_logic import save_queue
from src.logic.queue_logic import load_queue
from src.logic.message_logic import handle_message
from src.service.send_service import MyThread


def run_server(hostname='localhost', port=14141, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    load_queue()
    task = asyncio.start_server(handle_message, hostname, port, loop=loop)
    server = loop.run_until_complete(task)
    print('Serving on ', server.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    save_queue()
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    run_server()