from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from gui.images_paths import (
    ICON_PATH,
    BACKGROUND_PATH,
    REC_BUTTON_PATH,
    REC_BUTTON_PRESSED_PATH,
    PLAY_BUTTON_PATH,
    PLAY_BUTTON_PRESSED_PATH,
    CLEAR_BUTTON_PATH,
    CLEAR_BUTTON_PRESSED_PATH,
)


class GuiComponents:
    def __init__(self, parent):
        self.parent = parent
        self._initialize_window_properties()
        self._create_gui_components()

    def _initialize_window_properties(self):
        """Set up main window attributes."""
        self.parent.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.parent.setGeometry(
            self.parent.left, self.parent.top, self.parent.width, self.parent.height
        )
        self.parent.setWindowTitle(self.parent.title)

    def _create_gui_components(self):
        """Create and initialize all GUI components."""
        self._create_background_image()
        self._create_webcam_display_label()
        self.rec_btn = self._create_button(
            93, 577, 123, 100, REC_BUTTON_PATH, REC_BUTTON_PRESSED_PATH
        )
        self.play_btn = self._create_button(
            243, 576, 123, 88, PLAY_BUTTON_PATH, PLAY_BUTTON_PRESSED_PATH
        )
        self.clear_btn = self._create_button(
            393, 576, 123, 88, CLEAR_BUTTON_PATH, CLEAR_BUTTON_PRESSED_PATH
        )

    def _create_background_image(self):
        """Set the background image for the main window."""
        vbox = QVBoxLayout()
        label_image = QLabel(self.parent)
        pixmap = QPixmap(BACKGROUND_PATH)
        label_image.setPixmap(pixmap)
        vbox.addWidget(label_image)

    def _create_webcam_display_label(self):
        """Create the label to display webcam feed."""
        self.label = QLabel(self.parent)
        self.label.move(61, 67)
        self.label.resize(495, 470)
        self.label.setStyleSheet("border: 2px solid #fcd462; border-radius: 5px;")

    def _create_button(self, x, y, width, height, normal_image, pressed_image):
        """Create a button with given specifications."""
        button = QtWidgets.QPushButton(self.parent)
        button.setGeometry(x, y, width, height)
        self.parent.set_button_style(button, normal_image, pressed_image)
        return button
