topic_subs = {}


def add_sub(topic, sub):
    if topic in topic_subs:
        topic_subs[topic].append(sub)
    else:
        topic_subs[topic] = []
        topic_subs[topic].append(sub)


def notify(topic, msg):
    for sub in topic_subs[topic]:
        sub.write(msg)
        yield from sub.drain()
        sub.write_eof()
        sub.close()
