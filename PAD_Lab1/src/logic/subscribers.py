topic_subs = {}


def add_sub(topic, sub):
    if topic in topic_subs:
        topic_subs[topic].append(sub)
    else:
        topic_subs[topic] = []
        topic_subs[topic].append(sub)


def notify(topic):
    for sub in topic_subs[topic]:
        sub
