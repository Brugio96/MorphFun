"""
frame_processing.py

This module defines the FrameDisplayProcessor for the Webcam. It includes logic for processing webcam frames for display. The FrameDisplayProcessor integrates with various components like OpenCV and PyQt5 to orchestrate the core functionalities of webcam image processing.

Classes:
    FrameDisplayProcessor: Handles the processing and emission of frames for display.
"""

import cv2
from PyQt5 import QtGui, QtCore


class FrameDisplayProcessor:
    """
    Handles the processing and emission of frames for display.

    This class is responsible for taking raw frames from a webcam feed, processing them, and then emitting them in a format that can be easily displayed by a GUI component. Processing includes converting the frame to the RGB color space, cropping, flipping, and scaling to the appropriate size for display.

    Methods:
        emit_frame_for_display: Takes a raw frame, processes it, and emits it through a signal for display.
        _prepare_frame_for_display: Prepares the frame by converting to RGB, cropping, flipping, and scaling.
        _convert_frame_to_rgb: Converts a frame from BGR to RGB color space.
        _crop_and_flip_frame: Crops and flips the frame horizontally.
        _scale_frame: Scales the frame to a preset resolution.
    """

    def emit_frame_for_display(self, frame, changePixmap):
        """
        Processes the frame and emits it for display.

        This function processes a raw frame using private methods to prepare it for display and emits the processed frame through a given signal.

        Parameters:
            frame: The raw frame captured from the webcam to be processed.
            changePixmap: A PyQt signal used to emit the processed frame to the GUI component for display.
        """
        processed_frame = self._prepare_frame_for_display(frame)
        changePixmap.emit(processed_frame)

    def _prepare_frame_for_display(self, frame):
        """
        Prepares the frame by converting, cropping, flipping, and scaling.

        It sequentially calls internal methods to convert the frame to RGB format, crop and flip it, and finally scale it to the desired size.

        Parameters:
            frame: The raw frame to be processed.

        Returns:
            QImage: The processed Qt Image ready to be displayed.
        """
        frame = self._convert_frame_to_rgb(frame)
        frame = self._crop_and_flip_frame(frame)
        return self._scale_frame(frame)

    def _convert_frame_to_rgb(self, frame):
        """
        Converts the frame from BGR to RGB format.

        This is necessary because OpenCV captures images in BGR format, but the display typically expects RGB format.

        Parameters:
            frame: The frame in BGR format to be converted.

        Returns:
            ndarray: The frame converted to RGB format.
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _crop_and_flip_frame(self, frame):
        """
        Crops and horizontally flips the frame.

        Flipping is commonly used in webcam applications to mirror the user's movements.

        Parameters:
            frame: The frame to be cropped and flipped.

        Returns:
            ndarray: The cropped and flipped frame.
        """
        return cv2.flip(frame, 1)

    def _scale_frame(self, frame):
        """
        Scales the frame to the desired dimensions.

        This method converts the frame into a QImage and scales it, maintaining the aspect ratio, to a standard size for display.

        Parameters:
            frame: The frame to be scaled.

        Returns:
            QImage: The scaled Qt Image with a fixed resolution.
        """
        h, w, ch = frame.shape
        bytesPerLine = ch * w
        qt_image = QtGui.QImage(
            frame.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888
        )
        return qt_image.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
