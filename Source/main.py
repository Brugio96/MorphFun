import os
import sys
import threading
import warnings
from queue import Queue
from PyQt5.QtWidgets import QApplication
import tensorflow as tf
from gui import Window
from controller import main_controller  # Import the new main_controller function

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from tensorflow.python.ops.numpy_ops import np_config

np_config.enable_numpy_behavior()


def main():
    warnings.filterwarnings("ignore")

    # Initialize the queues
    command_queue = Queue()
    data_queue = Queue()
    morphing_queue = Queue()

    # Start the PyQt application
    App = QApplication(sys.argv)
    window = Window(command_queue, data_queue)

    # Start the controller in a separate thread
    controller_thread = threading.Thread(
        target=main_controller, args=(App, command_queue, data_queue, morphing_queue)
    )
    controller_thread.start()

    sys.exit(App.exec())


if __name__ == "__main__":
    main()
