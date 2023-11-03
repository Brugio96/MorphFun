"""
main_window.py

This module defines the Window class for the MorphFun application. It includes logic for the graphical user interface and its interactions. The Window class integrates with various components like GuiComponents and UserInteractions, to orchestrate the core functionalities of the MorphFun application.

Classes:
    Window: Provides the main dialog window for the MorphFun application.

"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
from pynput.keyboard import Key, Controller
from gui.components import GuiComponents
from gui.user_interactions import UserInteractions
from gui.images_paths import (
    REC_BUTTON_PATH,
    REC_BUTTON_ON_PATH,
    REC_BUTTON_PRESSED_PATH,
    PLAY_BUTTON_PATH,
    STOP_BUTTON_PATH,
    PLAY_BUTTON_PRESSED_PATH,
    STOP_BUTTON_PRESSED_PATH,
    CLEAR_BUTTON_PATH,
    CLEAR_BUTTON_PRESSED_PATH,
)


class Window(QDialog):
    """
    Window class that serves as the main dialog for the MorphFun application.

    Attributes:
        cmd_queue: A queue for GUI commands.
        gui: An instance of the GuiComponents class.
        interactions: An instance of the UserInteractions class for managing user interactions.

    Methods:
        __init__: Constructs the main window and initializes components.
        _initialize_window_properties: Sets up the properties of the window.
        _initialize_user_interactions: Initializes the interactions with GUI components.
        set_image: Updates the image displayed on the main label.
        set_button_style: Configures the visual style of a button using image paths.
        close_event: Handles the event when the window is closed.
    """

    closing = pyqtSignal()

    def __init__(self, thread_manager):
        """
        Initializes the Window dialog with necessary components and state variables.

        Parameters:
            thread_manager: The manager for different threads used within the application which provides command queue for GUI.
        """
        super().__init__()

        # Extract queues from thread_manager
        self.cmd_queue = thread_manager.create_queue("gui_commands")

        # Initialize window properties
        self._initialize_window_properties()

        # Initialize GUI components and user interactions
        self.gui = GuiComponents(self)
        self.interactions = self._initialize_user_interactions()

        self.show()

    def _initialize_window_properties(self):
        """
        Initialize the main properties of the window including title, position, and size.
        """
        self.title = "MorphFun"
        self.left = 350
        self.top = 180
        self.width = 1280
        self.height = 720
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def _initialize_user_interactions(self):
        """
        Initialize user interactions with GUI components and link them with their respective button image paths.

        Returns:
            UserInteractions: An initialized UserInteractions object for handling user interactions within the GUI.
        """
        button_paths = {
            "rec": (REC_BUTTON_PATH, REC_BUTTON_ON_PATH, REC_BUTTON_PRESSED_PATH),
            "play": (
                PLAY_BUTTON_PATH,
                STOP_BUTTON_PATH,
                PLAY_BUTTON_PRESSED_PATH,
                STOP_BUTTON_PRESSED_PATH,
            ),
            "clear": (CLEAR_BUTTON_PATH, CLEAR_BUTTON_PRESSED_PATH),
        }
        return UserInteractions(self.gui, self.cmd_queue, button_paths)

    def set_image(self, image):
        """
        Updates the displayed image on the GUI.

        Parameters:
            image: An image object that will be converted to a QPixmap and displayed on the GUI.
        """
        qt_image = QPixmap.fromImage(image)
        self.gui.label.setPixmap(qt_image)

    def set_button_style(self, button, normal_image, pressed_image):
        """
        Sets the visual style of a button using the provided image paths for its normal and pressed states.

        Parameters:
            button: The QPushButton object to be styled.
            normal_image: The path to the image for the button's normal state.
            pressed_image: The path to the image for the button's pressed state.
        """
        button.setStyleSheet(
            f"QPushButton{{background-image: url({normal_image}); background-repeat: no-repeat; border: none;}}"
            f"QPushButton::pressed{{background-image: url({pressed_image});}}"
        )

    def close_event(self, event):
        """
        Handles the window close event by simulating an ESC key press to ensure proper termination of the application.

        Parameters:
            event: The close event object that is passed when the QDialog is closed.
        """
        keyboard = Controller()
        keyboard.press(Key.esc)

    def closeEvent(self, event):
        """
        Handles the window close event by emitting the 'closing' signal to ensure proper termination of the application.

        Parameters:
            event: The close event object that is passed when the QDialog is closed.
        """
        self.closing.emit()
        super().closeEvent(event)
