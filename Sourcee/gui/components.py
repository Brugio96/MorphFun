"""
components.py

This module defines the GuiComponents class for the application's graphical user interface. It includes logic for setting up the main window properties and creating GUI elements such as buttons and labels. The GuiComponents class integrates with PyQt5 components to orchestrate the core functionalities of the application's user interface.

Classes:
    GuiComponents: Manages and initializes all the graphical components of the application's main window.
"""

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
    """
    This class manages and initializes all the graphical components of the application's main window.

    Attributes:
        parent: The parent window (usually the main window) for which this class manages GUI components.
        rec_btn: The record button component.
        play_btn: The playback button component.
        clear_btn: The clear button component.
        label: The label used to display the webcam feed.

    Methods:
        _initialize_window_properties: Sets up the main window's icon, geometry, and title.
        _create_gui_components: Creates and initializes all the GUI components.
        _create_background_image: Sets the background image for the main window.
        _create_webcam_display_label: Creates the label to display the webcam feed.
        _create_button: Creates a button with normal and pressed images.
    """

    def __init__(self, parent):
        """
        Initializes the GuiComponents with necessary components and state variables.

        Parameters:
            parent: The main window instance that will serve as the parent for all GUI components.
        """
        self.parent = parent
        self._initialize_window_properties()
        self._create_gui_components()

    def _initialize_window_properties(self):
        """
        Sets up main window attributes including the icon, geometry, and title based on the parent attributes.
        """
        self.parent.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.parent.setGeometry(
            self.parent.left, self.parent.top, self.parent.width, self.parent.height
        )
        self.parent.setWindowTitle(self.parent.title)

    def _create_gui_components(self):
        """
        Creates and initializes all GUI components including background image, webcam display label, and buttons.
        """
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
        """
        Sets the background image for the main window using a QVBoxLayout and QLabel to hold the image.
        """
        vbox = QVBoxLayout()
        label_image = QLabel(self.parent)
        pixmap = QPixmap(BACKGROUND_PATH)
        label_image.setPixmap(pixmap)
        vbox.addWidget(label_image)

    def _create_webcam_display_label(self):
        """
        Creates a label on the main window to display the webcam feed with specific style and geometry.
        """
        self.label = QLabel(self.parent)
        self.label.move(61, 67)
        self.label.resize(495, 470)
        self.label.setStyleSheet("border: 2px solid #fcd462; border-radius: 5px;")

    def _create_button(self, x, y, width, height, normal_image, pressed_image):
        """
        Creates a styled button at a specified location with specific images for its normal and pressed states.

        Parameters:
            x: The x-coordinate of the button's top-left corner.
            y: The y-coordinate of the button's top-left corner.
            width: The width of the button.
            height: The height of the button.
            normal_image: The image path for the button's normal state.
            pressed_image: The image path for the button's pressed state.

        Returns:
            QPushButton: A button configured with specific styles and functionality.
        """
        button = QtWidgets.QPushButton(self.parent)
        button.setGeometry(x, y, width, height)
        self.parent.set_button_style(button, normal_image, pressed_image)
        return button
