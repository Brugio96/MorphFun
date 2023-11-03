"""
user_interactions.py

This module defines the UserInteractions for a GUI application. It includes logic for handling user actions such as starting/stopping recording, playing/pausing audio, and clearing sessions. The UserInteractions class integrates with GUI components and a command queue to orchestrate the core functionalities of user-triggered events.

Classes:
    UserInteractions: Manages interactions between the user and the GUI components.
"""

from gui.images_paths import (
    REC_BUTTON_PATH,
    REC_BUTTON_ON_PATH,
    REC_BUTTON_PRESSED_PATH,
    PLAY_BUTTON_PATH,
    STOP_BUTTON_PATH,
    PLAY_BUTTON_PRESSED_PATH,
    STOP_BUTTON_PRESSED_PATH,
)


class UserInteractions:
    """
    This class manages the interactions between the user and the GUI components.
    It encapsulates the behavior of the user interface, such as button clicks and
    other actions, by updating the GUI and posting commands to the command queue.

    Attributes:
        gui (object): The GUI components that this class will interact with.
        cmd_queue (queue.Queue): The command queue for communicating with other parts of the application.
        paused (bool): A flag to indicate if the playback is paused.
        isRecording (bool): A flag to indicate if recording is currently active.
        button_paths (dict): A dictionary mapping buttons to their image paths.

    Methods:
        init_connections: Connects the GUI buttons to their respective event handlers.
        handle_recording: Handles the logic for the recording button.
        handle_play_pause: Handles the logic for toggling play/pause.
        handle_clear: Sends a command to clear the current session or recording.
    """

    def __init__(self, gui_components, cmd_queue, button_paths):
        """
        Initializes the UserInteractions class with the GUI components, a command queue, and button image paths.

        Parameters:
            gui_components (object): The components of the GUI to be controlled.
            cmd_queue (queue.Queue): The queue for posting commands to be executed.
            button_paths (dict): Paths to the button images for different states.
        """
        self.gui = gui_components
        self.cmd_queue = cmd_queue
        self.paused = False
        self.isRecording = False
        self.button_paths = button_paths
        self.init_connections()

    def init_connections(self):
        """Connects GUI buttons to their respective event-handling methods."""
        self.gui.rec_btn.clicked.connect(self.handle_recording)
        self.gui.play_btn.clicked.connect(self.handle_play_pause)
        self.gui.clear_btn.clicked.connect(self.handle_clear)

    def handle_recording(self):
        """
        Toggles the recording state and updates the recording button's appearance.
        Posts the appropriate command to the command queue based on the recording state.
        """
        if self.isRecording:
            self.gui.parent.set_button_style(
                self.gui.rec_btn, REC_BUTTON_PATH, REC_BUTTON_PRESSED_PATH
            )
            self.gui.parent.set_button_style(
                self.gui.play_btn, STOP_BUTTON_PATH, STOP_BUTTON_PRESSED_PATH
            )
            self.paused = False
            self.isRecording = False
            self.cmd_queue.put("Stop Rec")
        else:
            self.gui.parent.set_button_style(
                self.gui.rec_btn, REC_BUTTON_ON_PATH, REC_BUTTON_PRESSED_PATH
            )
            self.isRecording = True
            self.cmd_queue.put("Start Rec")

    def handle_play_pause(self):
        """
        Toggles the playback state and updates the play/pause button's appearance.
        Posts the appropriate command to the command queue based on the playback state.
        """
        if self.paused:
            self.gui.parent.set_button_style(
                self.gui.play_btn, STOP_BUTTON_PATH, STOP_BUTTON_PRESSED_PATH
            )
            self.paused = False
            self.cmd_queue.put("Play")
        else:
            self.gui.parent.set_button_style(
                self.gui.play_btn, PLAY_BUTTON_PATH, PLAY_BUTTON_PRESSED_PATH
            )
            self.paused = True
            self.cmd_queue.put("Pause")

    def handle_clear(self):
        """
        Handles the clear button behavior by posting a 'Clear' command to the command queue.
        """
        self.cmd_queue.put("Clear")
