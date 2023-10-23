from pynput import keyboard

from utils import CONFIG_PATH
from CONFIG.config_manager import ConfigManager
from pose_estimation.morpher_manager import MorpherManager
from audio_utilities.audio_manager import AudioManager

# Constants
REC = "Rec"
PLAY = "Play"
PAUSE = "Pause"
CLEAR = "Clear"


class MessageHandler:
    def __init__(self, controller):
        self.controller = controller
        self._config_manager = controller.config_manager

    def process_message(self, message, data_queue, morphing_queue):
        """Process the received message and execute corresponding action."""
        print(f'Message received "{message}"')

        message_actions = {
            REC: self.controller.toggle_recording,
            PLAY: self.controller.audio_manager.play,
            PAUSE: self.controller.audio_manager.pause,
            CLEAR: self.controller.audio_manager.clear,
        }

        action = message_actions.get(
            message, lambda: self._handle_invalid_message(message)
        )
        action(data_queue, morphing_queue)

    def _handle_invalid_message(self, message):
        """Handle messages that do not correspond to any action."""
        messages = self._config_manager.get_config("controller")["messages"]
        if message not in messages:
            print(f"ERROR. {message} is not a valid message.")


class Controller:
    def __init__(self, App):
        self.App = App
        self.connectionIsActive = True
        self.config_manager = ConfigManager(CONFIG_PATH)
        self.morpher_manager = MorpherManager(self.config_manager)
        self.audio_manager = AudioManager(self.config_manager)
        self.message_handler = MessageHandler(self)
        self.exitListener = keyboard.Listener(on_press=self.on_press, daemon=True)

    def on_press(self, key):
        """Listen for the 'Esc' key press to close the connection."""
        if key == keyboard.Key.esc:
            self.connectionIsActive = False
            return False

    def toggle_recording(self, data_queue, morphing_queue):
        self.audio_manager.toggle_recording()

        if not self.audio_manager.audio_recorder.is_recording:
            self.perform_morphing(data_queue, morphing_queue)

    def perform_morphing(self, data_queue, morphing_queue):
        """Handle the audio morphing process."""
        self.audio_manager.save_recorded_audio()
        print("\n!!! MORPHING BEGINS !!!\n")
        self.audio_manager.play_recorded_audio()
        self.morpher_manager.transform_audio()
        self.morpher_manager.sound_ready_event.wait()
        self.audio_manager.audio_player.player.load_sounds()
        data_queue.put("start")
        self.morpher_manager.start_pose_estimation(morphing_queue, data_queue)
        self.audio_manager.audio_player.player.start_morphing(morphing_queue)

    def run(self, command_queue, data_queue, morphing_queue):
        """Main loop for the controller."""

        print("\nEnter 'Esc' to close the connection at any time\n")
        self.exitListener.start()

        while self.connectionIsActive:
            if not command_queue.empty():
                message = command_queue.get()
                self.message_handler.process_message(
                    message, data_queue, morphing_queue
                )

        self.close_app()

    def close_app(self):
        """Close the application safely."""
        print("Closing app.")
        try:
            self.App.quit()
        except Exception as e:
            print(f"Error closing app: {e}")
