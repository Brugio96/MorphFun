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
    def __init__(self, gui_components, cmd_queue, button_paths):
        self.gui = gui_components
        self.cmd_queue = cmd_queue
        self.paused = False
        self.isRecording = False
        self.button_paths = button_paths
        self.init_connections()

    def init_connections(self):
        """Connect button signals to respective slots"""
        self.gui.rec_btn.clicked.connect(self.handle_recording)
        self.gui.play_btn.clicked.connect(self.handle_play_pause)
        self.gui.clear_btn.clicked.connect(self.handle_clear)

    def handle_recording(self):
        """Handles recording button behavior."""
        if self.isRecording:
            self.gui.parent.set_button_style(
                self.gui.rec_btn, REC_BUTTON_PATH, REC_BUTTON_PRESSED_PATH
            )
            self.gui.parent.set_button_style(
                self.gui.play_btn,
                PLAY_BUTTON_PATH,
                PLAY_BUTTON_PRESSED_PATH,
            )
            self.paused = False
            self.isRecording = False
            self.cmd_queue.put("Rec")
        else:
            self.gui.parent.set_button_style(
                self.gui.rec_btn,
                REC_BUTTON_ON_PATH,
                REC_BUTTON_PRESSED_PATH,
            )
            self.isRecording = True
            self.cmd_queue.put("Rec")

    def handle_play_pause(self):
        """Handles play/pause button behavior."""
        if self.paused:
            self.gui.parent.set_button_style(
                self.gui.play_btn,
                PLAY_BUTTON_PATH,
                PLAY_BUTTON_PRESSED_PATH,
            )
            self.paused = False
            self.cmd_queue.put("Play")
        else:
            self.gui.parent.set_button_style(
                self.gui.play_btn,
                STOP_BUTTON_PATH,
                STOP_BUTTON_PRESSED_PATH,
            )
            self.paused = True
            self.cmd_queue.put("Pause")

    def handle_clear(self):
        """Handles clear button behavior."""
        self.cmd_queue.put("Clear")
