import sys
import threading
import logging
import os
from queue import Queue

from PyQt5.QtWidgets import QApplication
import tensorflow as tf
from tensorflow.python.ops.numpy_ops import np_config

from gui.main_window import Window
from gui.webcam import WebcamThread
from controller import Controller

logging.basicConfig(level=logging.INFO)


class TensorFlowConfiguration:
    @staticmethod
    def configure():
        """
        Configures TensorFlow to limit verbosity and enable numpy behavior.
        """
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        np_config.enable_numpy_behavior()


class ApplicationInitializationError(Exception):
    pass


class Application:
    def __init__(self):
        TensorFlowConfiguration.configure()
        (
            self._command_queue,
            self._data_queue,
            self._morphing_queue,
        ) = self._initialize_queues()
        self.app, self.main_window = self._initialize_app()

    def _initialize_queues(self):
        """Initialize communication queues and return them."""
        return Queue(), Queue(), Queue()

    def _initialize_app(self):
        """Initialize and return the PyQt application and main window."""
        try:
            app = QApplication(sys.argv)
            main_window = Window(self._command_queue)
            webcam_thread = WebcamThread(self._data_queue, main_window.set_image)
            main_window.set_webcam_thread(webcam_thread)
            return app, main_window
        except Exception as e:
            logging.error(f"Error initializing the application: {e}")
            raise ApplicationInitializationError(
                f"Failed to initialize application: {e}"
            )

    def _start_controller_thread(self):
        """Start the main controller in a separate thread."""
        try:
            controller = Controller(self.app)
            controller_thread = threading.Thread(
                target=controller.run,
                args=(
                    self._command_queue,
                    self._data_queue,
                    self._morphing_queue,
                ),
            )
            controller_thread.start()
        except threading.ThreadError as e:
            logging.error(f"Error starting the controller: {e}")

    def run(self):
        """Begin the event loop of the application."""
        self._start_controller_thread()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    try:
        application = Application()
        application.run()
    except ApplicationInitializationError as e:
        logging.error(e)
        sys.exit(1)
