import asyncio
import glob
import os

_MESSAGE_QUEUE = asyncio.Queue(loop=asyncio.get_event_loop())
static_topics = {
    "lab": asyncio.Queue(loop=asyncio.get_event_loop()),
    "pad": asyncio.Queue(loop=asyncio.get_event_loop())
}
dynamic_topics = {}


def save_queue():
    file = open('data.txt', "w")
    while not _MESSAGE_QUEUE.empty():
        msg = _MESSAGE_QUEUE.get_nowait()
        print(msg)
        file.write(msg + "\n")
    for key in static_topics.keys():
        file = open('' + key + '.txt', "w")
        while not static_topics[key].empty():
            msg = static_topics[key].get_nowait()
            print(msg)
            file.write(msg + "\n")
        file.close()
    for key in dynamic_topics.keys():
        file = open('' + key + '.txt', "w")
        while not dynamic_topics[key].empty():
            msg = dynamic_topics[key].get_nowait()
            print(msg)
            file.write(msg + "\n")
        file.close()


def load_queue():
    os.chdir("backup")
    for file in glob.glob("*.txt"):
        if os.path.splitext(file)[0] in static_topics.keys():
            for line in reversed(list(open(file, 'r+'))):
                txt = line.rstrip()
                print(txt)
                static_topics[os.path.splitext(file)[0]].put_nowait(txt)
        elif os.path.splitext(file)[0] == 'data':
            for line in reversed(list(open(file, 'r+'))):
                txt = line.rstrip()
                print(txt)
                _MESSAGE_QUEUE.put_nowait(txt)
        else:
            for line in reversed(list(open(file, "r+"))):
                dynamic_topics[os.path.splitext(file)[0]] = asyncio.Queue(loop=asyncio.get_event_loop())
                txt = line.rstrip()
                print(txt)
                dynamic_topics[os.path.splitext(file)[0]].put_nowait(txt)
