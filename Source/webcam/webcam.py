"""
webcam.py

This module defines the WebcamCapture and Webcam classes. It includes logic for capturing video from the default webcam, reading and processing frames, and signaling new frames for display. The Webcam class integrates with various components like KeypointsProcessor, FrameDisplayProcessor, and a thread manager to orchestrate the core functionalities of real-time pose estimation.

Classes:
    WebcamCapture: Handles basic operations for webcam capture.
    Webcam: Extends QtCore.QThread to manage the webcam capture and frame processing in a separate thread.
"""

from pose.pose_estimation import KeypointsProcessor
from webcam.frame_processing import FrameDisplayProcessor
import cv2
from PyQt5 import QtCore
from utils import CONFIG_PATH, load_config
from PyQt5.QtCore import pyqtSignal


class WebcamCapture:
    """
    Handles basic operations for webcam capture including initialization,
    reading frames, and releasing the webcam device.

    Methods:
        initialize: Starts the video capture for the default webcam.
        read_frame: Reads a frame from the webcam.
        release: Releases the webcam device.
    """

    def __init__(self):
        """Initializes the WebcamCapture object."""
        pass

    def initialize(self):
        """
        Starts the video capture for the default webcam.

        Returns:
            cv2.VideoCapture: The video capture object.
        """
        return cv2.VideoCapture(0)

    def read_frame(self, cap):
        """
        Reads a frame from the webcam.

        Parameters:
            cap: The video capture object from which to read.

        Returns:
            ndarray or None: The captured frame, or None if no frame is captured.
        """
        ret, frame = cap.read()
        return frame if ret else None

    def release(self, cap):
        """
        Releases the webcam device.

        Parameters:
            cap: The video capture object to release.
        """
        cap.release()


class Webcam(QtCore.QThread):
    """
    Extends QtCore.QThread and handles the webcam capture and frame processing
    in a separate thread to provide real-time video capture without blocking the main application.

    Attributes:
        newFrameSignal: pyqtSignal to emit the processed frames for display.
        is_running: Boolean indicating if the webcam thread is running.
        thread_manager: Reference to the manager that handles threading events and queues.
        keypoints_queue: Queue for storing keypoints data from the processed frames.
        frame_callback: The callback function to be executed with each new frame.
        config: Loaded configuration settings.
        boost: Configuration setting for latency factor in pose classification.
        webcam: WebcamCapture instance to manage webcam operations.
        keypoints_processor: KeypointsProcessor instance to process keypoints from frames.
        display_processor: FrameDisplayProcessor instance to prepare frames for display.

    Methods:
        __init__: Constructor to initialize the Webcam thread.
        _load_config: Loads configuration settings from a file.
        run: Main entry point for the QThread.
        _process_frames: Processes frames from the webcam in real-time.
        stop: Signals the thread to stop running.
    """

    newFrameSignal = pyqtSignal(object)

    def __init__(self, thread_manager, frame_callback, parent=None):
        """
        Initializes the Webcam object with necessary components and state variables.

        Parameters:
            thread_manager: The ThreadManager object managing threading events and queues.
            frame_callback: The callback function to execute for each frame.
            parent: The parent QObject, if any (default is None).
        """
        super(Webcam, self).__init__(parent=parent)
        self.is_running = True
        self.thread_manager = thread_manager
        self.keypoints_queue = self.thread_manager.queue_manager.create_queue(
            "keypoints_data"
        )
        self.frame_callback = frame_callback
        self.config = self._load_config()
        self.boost = self.config["pose_classification"]["latency_factor"]
        self.webcam = WebcamCapture()
        self.keypoints_processor = KeypointsProcessor(self.keypoints_queue, self.boost)
        self.display_processor = FrameDisplayProcessor()

    def _load_config(self):
        """
        Loads configuration from the CONFIG_PATH.

        Returns:
            dict: The configuration settings loaded from the file.
        """
        return load_config(CONFIG_PATH)

    def run(self, stop_event):
        """
        The main entry point for the QThread. Starts the webcam capture and processes frames.

        Parameters:
            stop_event: Optional threading.Event that signals the thread to stop (default is None).
        """

        cap = self.webcam.initialize()
        self._process_frames(cap, stop_event)
        self.webcam.release(cap)

    def _process_frames(self, cap, stop_event):
        """
        Processes frames from the webcam to extract keypoints and prepare for display.

        Parameters:
            cap: The video capture object from which to read frames.
            stop_event: The threading.Event that signals the thread to stop.
        """
        sequence = []
        counter = 0
        self.thread_manager.create_event("start_extraction")

        while self.is_running and cap.isOpened():
            if stop_event.is_set():
                break

            frame = self.webcam.read_frame(cap)
            if frame is not None:
                if self.thread_manager.is_event_set("start_extraction"):
                    counter, sequence = self.keypoints_processor.update_frame_data(
                        frame, counter, sequence
                    )
            processed_frame = self.display_processor._prepare_frame_for_display(frame)
            self.newFrameSignal.emit(processed_frame)

    def stop(self):
        """
        Signals the thread to stop running and clean up.
        """
        self.is_running = False
