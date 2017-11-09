from source.node.node import Node

# Create new threads
thread1 = Node(1, "Thread-1", 14141)
thread2 = Node(2, "Thread-2", 14142)

# Start new Threads
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print("Exiting Main Thread")
