"""
main.py

This module initializes and runs an application that interfaces with a webcam using a GUI built with PyQt5. It sets up TensorFlow configurations, handles threading for concurrent execution of webcam feed processing and GUI control, and manages application termination. The GUI displays images from the webcam, and a controller listens for events to coordinate the application's operations.

Classes:
    TensorFlowConfiguration: Configures TensorFlow settings and numpy-like behavior.
    Application: Initializes and manages the main components of the system such as the GUI, webcam, and controller, and controls the application's execution flow.
"""

import sys
import logging
import os

from PyQt5.QtWidgets import QApplication
import tensorflow as tf
from tensorflow.python.ops.numpy_ops import np_config

from gui.main_window import Window
from webcam.webcam import Webcam
from controller import Controller
from thread_manager import ThreadManager

# Configure logging at INFO level
logging.basicConfig(level=logging.INFO)


class TensorFlowConfiguration:
    """
    Handles the configuration of TensorFlow to minimize verbosity and enforce numpy-like behavior in TensorFlow operations.

    This configuration is static and intended to be set before the TensorFlow-related operations are started. It reduces the logging level of TensorFlow to avoid flooding the console with unnecessary information and enables numpy compatibility mode for consistency in tensor operations.
    """

    @staticmethod
    def configure():
        """
        Set TensorFlow's verbosity to ERROR level and enable numpy-like behavior.
        """
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        np_config.enable_numpy_behavior()


class Application:
    """
    Orchestrates the initialization and management of the main application components including the GUI, webcam interface, and the controller for event handling.

    The Application class encapsulates the entire application setup, including the creation of the main window, the webcam thread for capturing frames, and the controller that manages user interactions. It also ensures that the application exits cleanly when the GUI is closed.
    """

    def __init__(self):
        """
        Initializes the application, the thread manager, TensorFlow configurations, and the main GUI components.
        """
        self.thread_manager = ThreadManager()
        TensorFlowConfiguration.configure()
        self.app = QApplication(sys.argv)
        self.main_window = Window(self.thread_manager)
        self.webcam = Webcam(self.thread_manager, self.main_window.set_image)
        self.controller = Controller(self.app, self.thread_manager)
        self.main_window.closing.connect(self.controller.close_app)

    def run(self):
        """
        Starts the webcam feed, controller thread, and sets up the application exit mechanism.
        """
        self.start_webcam()
        self.start_controller()
        self.exit_application_on_close()

    def start_webcam(self):
        """
        Initiates the webcam thread, enabling the capture of frames, and connects the GUI update signal.
        """
        try:
            self.thread_manager.start_thread("webcam", self.webcam.run)
            self.webcam.newFrameSignal.connect(self.main_window.set_image)
        except Exception as e:
            logging.error(f"Error starting webcam thread: {e}")

    def start_controller(self):
        """
        Commences the operation of the controller in a dedicated thread for handling user interactions.
        """
        try:
            self.thread_manager.start_thread("controller", self.controller.run)
        except Exception as e:
            logging.error(f"Error starting controller: {e}")

    def exit_application_on_close(self):
        """
        Executes the GUI event loop and ensures the application exits gracefully when the GUI window is closed.
        """
        try:
            sys.exit(self.app.exec_())
        except Exception as e:
            logging.error(f"Error closing the application: {e}")
            sys.exit(1)


if __name__ == "__main__":
    application = Application()
    application.run()
