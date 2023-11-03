"""
thread_manager.py

This module manages threading and inter-thread communication for the application. It provides a centralized way to manage threads, queues, and events which are crucial for orchestrating concurrent tasks.

Classes:
    QueueManager: Manages queues for inter-thread communication.
    EventManager: Manages events for inter-thread synchronization.
    ThreadManager: Central manager for creating and controlling threads, and for handling queues and events.
"""

import threading
from queue import Empty
from queue import Queue
import logging


class QueueManager:
    """
    Manages the creation, retrieval, and deletion of message queues.

    Attributes:
        queues (dict): A dictionary holding queue names as keys and queue objects as values.

    Methods:
        create_queue: Creates a new queue with a given name.
        get_queue: Retrieves a queue by its name.
        delete_queue: Deletes a queue by its name.
    """

    def __init__(self):
        """Initializes a new QueueManager object with an empty dictionary of queues."""
        self.queues = {}

    def create_queue(self, name):
        """
        Creates a new queue with the specified name if it doesn't exist.

        Parameters:
            name (str): The name of the queue to create.

        Returns:
            Queue: The created or existing queue.
        """
        if name not in self.queues:
            self.queues[name] = Queue()
        return self.queues[name]

    def get_queue(self, name):
        """
        Retrieves a queue by its name.

        Parameters:
            name (str): The name of the queue to retrieve.

        Returns:
            Queue or None: The retrieved queue or None if it doesn't exist.
        """
        return self.queues.get(name)

    def delete_queue(self, name):
        """
        Deletes a queue by its name.

        Parameters:
            name (str): The name of the queue to delete.
        """
        self.queues.pop(name, None)


class EventManager:
    """
    Manages threading events for synchronization between threads.

    Attributes:
        events (dict): A dictionary holding event names as keys and event objects as values.

    Methods:
        create_event: Creates a threading event with a given name.
        set_event: Sets the state of an event to true.
        clear_event: Resets the state of an event to false.
        is_event_set: Checks if an event is set.
        get_event: Retrieves an event by name.
        wait_for_event: Waits for an event to be set.
    """

    def __init__(self):
        """Initializes a new EventManager object with an empty dictionary of events."""
        self.events = {}

    def create_event(self, event_name):
        """
        Creates a threading event with the specified name if it doesn't already exist.

        Parameters:
            event_name (str): The name of the event to create.

        Returns:
            Event: The created or existing event.
        """
        if event_name not in self.events:
            self.events[event_name] = threading.Event()
        return self.events[event_name]

    def set_event(self, event_name):
        """
        Sets the state of an event to true.

        Parameters:
            event_name (str): The name of the event to set.
        """
        self.events.get(event_name, threading.Event()).set()

    def clear_event(self, event_name):
        """
        Resets the state of an event to false.

        Parameters:
            event_name (str): The name of the event to clear.
        """
        self.events.get(event_name, threading.Event()).clear()

    def is_event_set(self, event_name):
        """
        Checks if an event is set.

        Parameters:
            event_name (str): The name of the event to check.

        Returns:
            bool: True if the event is set, False otherwise.
        """
        return self.events.get(event_name, threading.Event()).is_set()

    def get_event(self, event_name):
        """
        Retrieves an event by its name.

        Parameters:
            event_name (str): The name of the event to retrieve.

        Returns:
            Event or None: The retrieved event or None if it doesn't exist.
        """
        return self.events.get(event_name)

    def wait_for_event(self, event_name, timeout=None):
        """
        Waits for an event to be set or a timeout to occur.

        Parameters:
            event_name (str): The name of the event to wait for.
            timeout (float or None): The maximum number of seconds to wait.

        Returns:
            bool: True if the event was set, False if a timeout occurred.
        """
        return self.events.get(event_name, threading.Event()).wait(timeout=timeout)


class ThreadManager:
    """
    Manages threads, delegating thread functions and handling their life cycle.

    Attributes:
        threads (dict): A dictionary holding thread names as keys and thread objects as values.
        queue_manager (QueueManager): An instance of QueueManager to manage queues.
        event_manager (EventManager): An instance of EventManager to manage events.
        stop_events (dict): A dictionary holding thread names as keys and threading events as values to handle stopping of threads.

    Methods:
        get_thread_instance: Retrieves an instance of a thread by its name.
        start_thread: Starts a thread with a specified target function.
        stop_thread: Stops a thread by its name.
        is_thread_active: Checks if a thread is active.
        create_queue: Creates a queue with a specified name.
        get_queue: Retrieves a queue by its name.
        enqueue_message: Enqueues a message into a queue.
        dequeue_message: Dequeues a message from a queue.
        create_event: Creates an event with a specified name.
        set_event: Sets an event.
        clear_event: Clears an event.
        is_event_set: Checks if an event is set.
        get_event: Retrieves an event by its name.
        wait_for_event: Waits for an event to be set.
    """

    def __init__(self):
        """Initializes a new ThreadManager with empty dictionaries for threads and stop events."""
        self.threads = {}  # Store instances of threads
        self.queue_manager = QueueManager()
        self.event_manager = EventManager()
        self.stop_events = {}  # Dictionary to handle stop_events for each thread

    def get_thread_instance(self, thread_name):
        """
        Retrieves an instance of a thread by its name.

        Parameters:
            thread_name (str): The name of the thread to retrieve.

        Returns:
            Thread or None: The thread instance if found, None otherwise.
        """
        return self.threads.get(thread_name)

    def start_thread(self, thread_name, target_function, args=(), is_qthread=False):
        """
        Starts a thread with a specific target function.

        Parameters:
            thread_name (str): The name to identify the thread.
            target_function (callable): The function that the thread will execute.
            args (tuple): Arguments to pass to the target function.
            is_qthread (bool): If true, expects the target_function to be an instance of QThread.

        Returns:
            Thread: The thread instance that was started.
        """
        stop_event = threading.Event()
        self.stop_events[thread_name] = stop_event

        if is_qthread:
            # QThread handling is expected to be implemented by the caller.
            thread_instance = target_function
            thread_instance.start()
        else:
            thread_instance = threading.Thread(
                target=target_function, args=args + (stop_event,)
            )
            thread_instance.start()

        self.threads[thread_name] = thread_instance
        return thread_instance

    def stop_thread(self, thread_name):
        """
        Stops a thread by its name.

        Parameters:
            thread_name (str): The name of the thread to stop.
        """
        if thread_name not in self.threads:
            logging.info(f"Thread '{thread_name}' not found or already stopped.")
            return

        logging.info(f"Stopping thread '{thread_name}'...")

        # Segnala all'evento di stop di terminare il thread
        self.stop_events[thread_name].set()

        # Attendi che il thread termini
        thread_instance = self.threads[thread_name]
        thread_instance.join()

        # Rimuovi il thread dalla lista
        del self.threads[thread_name]
        del self.stop_events[thread_name]

        logging.info(f"Thread '{thread_name}' stopped.")

    def is_thread_active(self, thread_name):
        """
        Checks if a specific thread is currently running.

        Parameters:
            thread_name (str): The name of the thread to check.

        Returns:
            bool: True if the thread is active, False otherwise.
        """
        return thread_name in self.threads and self.threads[thread_name].is_alive()

    def create_queue(self, queue_name):
        """
        Creates a queue with the specified name.

        Parameters:
            queue_name (str): The name of the queue to create.

        Returns:
            Queue: The created queue.
        """
        return self.queue_manager.create_queue(queue_name)

    def get_queue(self, queue_name):
        """
        Retrieves a queue by its name.

        Parameters:
            queue_name (str): The name of the queue to retrieve.

        Returns:
            Queue or None: The retrieved queue or None if it doesn't exist.
        """
        return self.queue_manager.get_queue(queue_name)

    def enqueue_message(self, queue_name, message):
        """
        Enqueues a message into a specified queue.

        Parameters:
            queue_name (str): The name of the queue where to enqueue the message.
            message (Any): The message to enqueue.
        """
        target_queue = self.get_queue(queue_name)
        if target_queue:
            target_queue.put(message)

    def dequeue_message(self, queue_name, timeout=None):
        """
        Dequeues a message from a specified queue.

        Parameters:
            queue_name (str): The name of the queue from which to dequeue the message.
            timeout (float or None): The number of seconds to wait for a message before returning None.

        Returns:
            Any or None: The dequeued message or None if the queue is empty or a timeout occurs.
        """
        target_queue = self.get_queue(queue_name)
        if target_queue:
            try:
                return target_queue.get(timeout=timeout)
            except Empty:
                return None

    def create_event(self, event_name):
        """
        Creates an event with the specified name.
        """
        return self.event_manager.create_event(event_name)

    def set_event(self, event_name):
        """
        Sets an event, allowing threads waiting on it to continue.
        """
        self.event_manager.set_event(event_name)

    def clear_event(self, event_name):
        """
        Clears an event, resetting its state to False.
        """
        self.event_manager.clear_event(event_name)

    def is_event_set(self, event_name):
        """
        Checks if an event is set.
        """
        return self.event_manager.is_event_set(event_name)

    def get_event(self, event_name):
        """
        Retrieves an event by its name.
        """
        return self.event_manager.get_event(event_name)

    def wait_for_event(self, event_name, timeout=None):
        """
        Waits for an event to be set.
        """
        return self.event_manager.wait_for_event(event_name, timeout=timeout)
