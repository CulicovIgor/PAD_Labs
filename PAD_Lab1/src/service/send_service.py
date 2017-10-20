import time
import threading

from src.logic.queue_logic import _MESSAGE_QUEUE
from src.logic.queue_logic import static_topics
from src.logic.queue_logic import dynamic_topics
from src.logic.subscribers import notify


class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Thread started")
        while True:
            while not _MESSAGE_QUEUE.empty():
                msg = yield from _MESSAGE_QUEUE.get()
                notify('', msg)
            for static_topic in static_topics:
                while not static_topic.empty():
                    msg = yield from static_topic.get()
                    notify('', msg)
            for dynamic_topic in dynamic_topics:
                while not dynamic_topic.empty():
                    msg = yield from dynamic_topic.get()
                    notify('', msg)
            time.sleep(1)
        pass
