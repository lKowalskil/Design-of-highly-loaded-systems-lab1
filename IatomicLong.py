import hazelcast
import threading
import time

client = hazelcast.HazelcastClient()

cp_subsystem = client.cp_subsystem
atomic_counter = cp_subsystem.get_atomic_long("my-atomic-counter").blocking()

def increment_atomic_counter():
    for _ in range(10000):
        atomic_counter.increment_and_get()

threads = []
start_time = time.time()

for _ in range(10):
    thread = threading.Thread(target=increment_atomic_counter)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()

final_counter_value = atomic_counter.get()
execution_time = end_time - start_time

print("\n" + "-" * 50)
print("IAtomicLong")
print(f"{'Final counter value:'} {final_counter_value}")
print(f"{'Execution time:'} {execution_time} seconds")
print("-" * 50)

client.shutdown()
