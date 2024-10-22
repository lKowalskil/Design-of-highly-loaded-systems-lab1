import hazelcast
import threading
import time

client = hazelcast.HazelcastClient()

def increment_counter(map_name):
    for _ in range(10000):
        value = map_name.get("counter")
        map_name.put("counter", value + 1)

def increment_counter_pessimistic(map_name):
    for _ in range(10000):
        map_name.lock("counter")
        try:
            value = map_name.get("counter")
            map_name.put("counter", value + 1)
        finally:
            map_name.unlock("counter")

def increment_counter_optimistic(map_name):
    for _ in range(10000):
        while True:
            old_value = map_name.get("counter")
            new_value = old_value + 1
            if map_name.replace_if_same("counter", old_value, new_value):
                break

def run_threads(target_function):
    start_time = time.time()
    map_name = client.get_map("my-distributed-map").blocking()
    map_name.put("counter", 0)
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=target_function, args=(map_name,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    end_time = time.time()
    diff_time = end_time - start_time
    return f"{map_name.get('counter')}", diff_time

def print_results(label, result_counter, diff_time):
    print(f"{label:25}: {result_counter:<10} | {diff_time:.6f} seconds")

print("Performance Results".center(50, '-'))
print_results("No lock", *run_threads(increment_counter))
print_results("Pessimistic locking", *run_threads(increment_counter_pessimistic))
print_results("Optimistic locking", *run_threads(increment_counter_optimistic))
print("-" * 50)

client.shutdown()
