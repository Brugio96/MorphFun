from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
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
    def __init__(self, cmd_queue):
        super().__init__()

        # Initialize window properties
        self._initialize_window_properties()

        # Initialize GUI components and user interactions
        self.gui = GuiComponents(self)
        self.interactions = self._initialize_user_interactions(cmd_queue)

        self.show()

    def _initialize_window_properties(self):
        """Initialize the main properties of the window."""
        self.title = "MorphFun"
        self.left = 350
        self.top = 180
        self.width = 1280
        self.height = 720
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def _initialize_user_interactions(self, cmd_queue):
        """Initialize user interactions with buttons and their paths."""
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
        return UserInteractions(self.gui, cmd_queue, button_paths)

    def set_webcam_thread(self, webcam_thread):
        """Set and start the webcam thread."""
        self.webcam_thread = webcam_thread
        self.webcam_thread.newFrameSignal.connect(self.set_image)
        self.webcam_thread.start()

    def set_image(self, image):
        """Updates the displayed image."""
        qt_image = QPixmap.fromImage(image)
        self.gui.label.setPixmap(qt_image)

    def set_button_style(self, button, normal_image, pressed_image):
        """Sets the visual style of a button using images."""
        button.setStyleSheet(
            f"QPushButton{{background-image: url({normal_image}); background-repeat: no-repeat; border: none;}}"
            f"QPushButton::pressed{{background-image: url({pressed_image});}}"
        )

    def close_event(self, event):
        """Handles the window close event."""
        keyboard = Controller()
        keyboard.press(Key.esc)
