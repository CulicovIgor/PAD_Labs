from source.node.node import Node

# Create new threads
thread1 = Node("Node-1", 9091, [])
thread2 = Node("Node-2", 9092, [9093, 9094, 9095])
thread3 = Node("Node-3", 9093, [9092, 9094, 9095])
thread4 = Node("Node-4", 9094, [9092, 9093, 9095])
thread5 = Node("Node-5", 9095, [9092, 9093, 9094])
thread6 = Node("Node-6", 9096, [])

# Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
print("Exiting Main Thread")
