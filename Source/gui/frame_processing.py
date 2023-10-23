import cv2
from PyQt5 import QtGui, QtCore


class FrameDisplayProcessor:
    """Handles the processing and emission of frames for display."""

    def emit_frame_for_display(self, frame, changePixmap):
        """Processes the frame and emits it for display."""
        processed_frame = self._prepare_frame_for_display(frame)
        changePixmap.emit(processed_frame)

    def _prepare_frame_for_display(self, frame):
        """Prepares the frame by converting, cropping, flipping, and scaling."""
        frame = self._convert_frame_to_rgb(frame)
        frame = self._crop_and_flip_frame(frame)
        return self._scale_frame(frame)

    def _convert_frame_to_rgb(self, frame):
        """Converts the frame from BGR to RGB format."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _crop_and_flip_frame(self, frame):
        """Crops and horizontally flips the frame."""
        return cv2.flip(frame, 1)

    def _scale_frame(self, frame):
        """Scales the frame to the desired dimensions."""
        h, w, ch = frame.shape
        bytesPerLine = ch * w
        qt_image = QtGui.QImage(
            frame.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888
        )
        return qt_image.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
