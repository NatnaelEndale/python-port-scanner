# Threading

We will discuss the following concepts in this part of the documentation

- [why sequential scanning is slow](#why-sequential-scanning-is-slow)
- [why threading is improves network scanning](#why-threading-is-improves-network-scanning)
- [how python threads behave](#how-python-threads-behave)
- [why ThreadpoolExecutor was chosen](#why-threadpoolexecutor-was-chosen)
- [how worker threads scan ports concurrently](#how-worker-threads-scan-ports-concurrently)
- [what synchronization problems exist](#what-synchronization-problems-exist)

## Why Sequential Scanning is Slow

When scanning a network for open ports, a common approach is to scan each port sequentially. This means that the scanner will check one port at a time, waiting for a response before moving on to the next port. This can be very slow, especially if there are many ports to scan or if the target host is slow to respond. Network operations spend most of their time waiting for responses, which can lead to significant delays when scanning multiple ports.

e.g ` Port 1 --> wait <br>
Port 2 --> wait <br>
Port 3 --> wait <br>
`
This sequential approach can take a long time to complete, especially if the target host has many ports to scan or if the network latency is high.

## Blocking I/O and Waiting

Sockets block while waiting for a response, which means that the thread that is performing the scan will be blocked until it receives a response from the target host. This can lead to inefficiencies in resource utilization, as the thread is not able to perform any other tasks while it is waiting for a response.

Network latency dominates scanning time, and the time spent waiting for responses can be significant. If you have multiple threads performing blocking I/O operations, they can all be waiting at the same time, which can lead to inefficiencies in resource utilization.

CPU is mostly idle during waiting for responses, as the thread is not executing any code while it is waiting. This means that if you have multiple threads performing blocking I/O operations, they can all be idle at the same time, which can lead to inefficiencies in resource utilization.

When a thread performs a blocking I/O operation, such as waiting for a response from a network request, it is put to sleep until the operation completes. During this time, the thread is not executing any code and is essentially idle. This means that if you have multiple threads performing blocking I/O operations, they can all be waiting at the same time, which can lead to inefficiencies in resource utilization.

## What is a Thread

A thread is a lightweight unit of execution within a process. It allows for concurrent execution of code, which can improve performance in certain scenarios, such as network scanning. Threads can be used to perform multiple tasks simultaneously, which can help to reduce the overall time taken to complete a task.

Also, threads share the same memory space, which allows them to communicate and share data easily. This can be beneficial for tasks that require a lot of data sharing, such as network scanning.

e.g Look at this analogy: Imagine you have a team of workers who are responsible for scanning a large building for open doors. If each worker scans one door at a time, it will take a long time to complete the task. However, if you have multiple workers scanning different doors simultaneously, the task can be completed much faster. In this analogy, each worker represents a thread, and the doors represent the ports being scanned.

## Why Threading Improves Network Scanning

Threading allows for concurrent execution of code, which can improve performance in certain scenarios, such as network scanning. By using multiple threads to scan different ports simultaneously, you can reduce the overall time taken to complete the scan.

When a thread performs a blocking I/O operation, such as waiting for a response from a network request, it is put to sleep until the operation completes. During this time, the thread is not executing any code and is essentially idle. However, if you have multiple threads performing blocking I/O operations, they can all be waiting at the same time, which can lead to inefficiencies in resource utilization. By using threading, you can allow other threads to continue executing while one thread is waiting for a response, which can help to improve performance.

e.g.
`Thread 1 --> waitng for port 22<br>
 Thread 2 --> scanning prot 80<br>
 Thread 3 --> scanning port 443<br>
 `
In this example, while Thread 1 is waiting for a response from port 22, Thread 2 and Thread 3 can continue scanning ports 80 and 443, respectively. This allows for more efficient use of resources and can significantly reduce the overall time taken to complete the scan. This is the key concurrency concept.

## Python GLI(Global Interpreter Lock)
In Python, the Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously. This means that even if you have multiple threads in your Python program, only one thread can execute Python code at a time. This can lead to performance issues when using threads for CPU-bound tasks, as the GIL can become a bottleneck.

However, for I/O-bound tasks, such as network scanning, the GIL is less of an issue. This is because when a thread is performing a blocking I/O operation, it releases the GIL, allowing other threads to execute while it is waiting for a response. This means that even with the GIL, you can still achieve concurrency and improve performance when using threads for network scanning.

## I/O-bound vs CPU-bound tasks
I/O-bound tasks are tasks that spend most of their time waiting for input/output operations to complete, such as reading from a file or waiting for a response from a network request. These tasks can benefit from threading, as the threads can continue executing while one thread is waiting for a response. 

CPU-bound tasks, on the other hand, are tasks that spend most of their time executing code and performing calculations. These tasks can be negatively impacted by the GIL, as only one thread can execute Python code at a time. For CPU-bound tasks, it may be more effective to use multiprocessing instead of threading to achieve true parallelism.

## Why ThreadPoolExecutor was Chosen
ThreadPoolExecutor is a high-level interface for managing a pool of threads. Instead of creating and managing individual threads, you can use ThreadPoolExecutor to submit tasks to a pool of worker threads. This allows for easier management of threads and can help to improve performance when performing concurrent tasks, such as network scanning.

-**thread reuse**: ThreadPoolExecutor allows for thread reuse, which can help to reduce the overhead of creating and destroying threads. This can lead to improved performance when performing a large number of tasks, such as scanning multiple ports.
-**simpler management**: ThreadPoolExecutor provides a simpler interface for managing threads, as you can submit tasks to the pool and let it handle the scheduling and execution of the threads. This can help to reduce the complexity of your code and make it easier to maintain.
-**scalability**: ThreadPoolExecutor can help to improve scalability, as it can manage a large number of threads and tasks efficiently. This can be particularly beneficial when scanning large networks with many ports to scan.
-**clear architecture**: Using ThreadPoolExecutor can help to improve the architecture of your code, as it provides a clear separation between the task submission and the thread management. This can make your code easier to understand and maintain.

## Worker Model
In a worker model, you have a pool of worker threads that are responsible for performing tasks concurrently. Each worker thread can be assigned a task, such as scanning a specific port, and can execute that task independently of the other threads. This allows for concurrent execution of tasks, which can improve performance when scanning a network for open ports. The worker threads can be managed using a ThreadPoolExecutor, which allows for easier management of threads and can help to improve performance when performing concurrent tasks, such as network scanning.

` Port list --> Thread pool --> Worker threads --> Sacn results`

## Understanding `executor.map()`

`executor.map()` is a method provided by the ThreadPoolExecutor class in Python's concurrent.futures module. It allows you to apply a function to each item in an iterable, distributing the tasks across the worker threads in the thread pool.

When you call `executor.map()`, you provide a function and an iterable (such as a list of ports to scan). The method will automatically distribute the tasks across the worker threads in the thread pool, allowing for concurrent execution of the tasks. Each worker thread will execute the function on a different item from the iterable, and the results will be collected and returned as an iterator.
```python
from concurrent.futures import ThreadPoolExecutor
def scan_port(port):
    # Code to scan the port
    return f"Port {port} is open"
ports_to_scan = [22, 80, 443]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(scan_port, ports_to_scan)
for result in results:
    print(result)
```     

In this example, the `scan_port` function is applied to each port in the `ports_to_scan` list. The `executor.map()` method distributes the tasks across the worker threads in the thread pool, allowing for concurrent execution of the port scanning tasks. The results are collected and printed out after all tasks have completed.

When using `executor.map()`, the tasks are automatically scheduled and executed by the thread pool, which can help to improve performance when performing concurrent tasks, such as network scanning. The method handles the distribution of tasks and the collection of results, allowing you to focus on the logic of your task rather than the management of threads.

## Passing Arguments to Worker Threads

When using `executor.map()`, you can pass arguments to the worker threads by including them in the function definition. The function you provide to `executor.map()` should accept the necessary arguments for the task you want to perform. When you call `executor.map()`, you can pass the iterable of arguments that will be used by the worker threads.

-**multiple iterables**: If your function requires multiple arguments, you can pass multiple iterables to `executor.map()`. Each iterable should correspond to a different argument in the function definition. The worker threads will receive the corresponding items from each iterable as arguments when executing the function.
```python
with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(port_scanner, range(p_range[0], p_range[1] + 1), repeat(target))
```
In this example, the `port_scanner` function is defined to accept two arguments: a port number and a target. The `executor.map()` method is called with two iterables: `range(p_range[0], p_range[1] + 1)` for the port numbers and `repeat(target)` for the target. The worker threads will receive the corresponding port number and target as arguments when executing the `port_scanner` function.

-**`repeat()`**: The `repeat()` function from the `itertools` module can be used to create an iterable that repeats a single value. This is useful when you want to pass the same argument to all worker threads while varying another argument, such as the port number in a port scanning task.
```Python
from itertools import repeat
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(port_scanner, range(p_range[0], p_range[1] + 1), repeat(target))
```
In this example, `repeat(target)` creates an iterable that will provide the same `target` value to each worker thread while the port numbers vary from `p_range[0]` to `p_range[1]`. This allows you to efficiently pass the same target to all threads while scanning different ports concurrently.

-**Why lambda was explored**: Lambda functions are anonymous functions that can be defined in a single line of code. They can be useful for simple tasks that do not require a full function definition. However, in the context of using `executor.map()`, lambda functions may not be the best choice for passing arguments to worker threads, as they can make the code less readable and harder to maintain. Using a regular function definition with clear argument names can improve the readability and maintainability of your code when working with concurrent tasks.

## Why `Queue()` Was Used
- thread-safe communication
- synchronized data sharing
- avoiding race conditions

We use `Queue()` from the `queue` module to facilitate thread-safe communication between worker threads and the main thread. The `Queue` class provides a thread-safe way to share data between threads, allowing worker threads to put results into the queue while the main thread can retrieve those results without worrying about synchronization issues. 

In a concurrent environment, multiple threads may try to access and modify shared data at the same time, which can lead to race conditions and inconsistent results. By using a `Queue`, we can ensure that the data is accessed in a thread-safe manner, as the `Queue` class handles the necessary locking and synchronization internally. This allows worker threads to safely communicate their results back to the main thread without the risk of data corruption or other synchronization problems.

```python
from queue import Queue
result_queue = Queue()
def worker_thread(port):
    # Code to scan the port
    result = f"Port {port} is open"
    result_queue.put(result)
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(worker_thread, range(1, 1025))
while not result_queue.empty():
    result = result_queue.get()
    print(result)
```
## Trade-offs of Threading
### advantages:
- faster scanning
- better resource utilization

Threading can significantly improve the performance of network scanning by allowing multiple ports to be scanned concurrently. This can lead to faster scanning times and better resource utilization, as threads can continue executing while others are waiting for responses.

### disadvantages:
- debugging complexity
- synchronization issues
- unordered results

While threading can improve performance, it can also introduce complexity in terms of debugging and synchronization. When multiple threads are accessing shared resources, such as a queue for storing results, there is a risk of race conditions and other synchronization issues that can lead to inconsistent results. Additionally, the results from worker threads may not be returned in the order they were submitted, which can make it more difficult to correlate results with specific tasks. Debugging issues in a multithreaded environment can also be more challenging due to the concurrent nature of thread execution.

**`Finally, while threading can provide significant performance benefits for I/O-bound tasks like network scanning, it is important to carefully consider the trade-offs and potential issues that can arise when using threads in your application. Proper synchronization and error handling are crucial to ensure that your multithreaded code runs correctly and efficiently.`**


