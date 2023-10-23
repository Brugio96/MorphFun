from pose_estimation.keypoints_utils import KeypointsProcessor
from gui.frame_processing import FrameDisplayProcessor
import cv2
from PyQt5 import QtCore
from utils import CONFIG_PATH, load_config
from PyQt5.QtCore import pyqtSignal


class WebcamCapture:
    """Handles basic operations for webcam capture."""

    def __init__(self):
        """Initializes the WebcamCapture object."""
        pass

    def initialize(self):
        """Starts the video capture for the default webcam."""
        return cv2.VideoCapture(0)

    def read_frame(self, cap):
        """Reads a frame from the webcam."""
        ret, frame = cap.read()
        return frame if ret else None

    def release(self, cap):
        """Releases the webcam."""
        cap.release()


class WebcamThread(QtCore.QThread):
    newFrameSignal = pyqtSignal(object)

    def __init__(self, data_queue, frame_callback, parent=None):
        """Initializes the WebcamThread with data queue and frame callback."""
        super(WebcamThread, self).__init__(parent=parent)
        self.is_running = True
        self.queue = data_queue
        self.frame_callback = frame_callback
        self.config = self._load_config()
        self.boost = self.config["pose_estimation"]["latency_factor"]
        self.webcam = WebcamCapture()
        self.keypoints_processor = KeypointsProcessor(self.queue, self.boost)
        self.display_processor = FrameDisplayProcessor()

    def _load_config(self):
        """Loads configuration from the CONFIG_PATH."""
        return load_config(CONFIG_PATH)

    def run(self):
        """Starts the webcam capture and processes frames."""
        cap = self.webcam.initialize()
        self._process_frames(cap)
        self.webcam.release(cap)

    def _process_frames(self, cap):
        """Processes frames from the webcam to extract keypoints and prepare for display."""
        sequence = []
        counter = 0
        while self.is_running and cap.isOpened():
            frame = self.webcam.read_frame(cap)
            if frame is not None:
                counter, sequence = self.keypoints_processor.update_frame_data(
                    frame, counter, sequence
                )
            processed_frame = self.display_processor._prepare_frame_for_display(frame)
            self.newFrameSignal.emit(processed_frame)
        return

    def stop(self):
        """Stops the webcam thread."""
        self.is_running = False
