from pynput import keyboard
from utils import CONFIG_PATH
from config_manager import ConfigManager
from pose_estimation.morpher_manager import MorpherManager
from audio_utilities.audio_manager import AudioManager


class MessageHandler:
    def __init__(self, config_manager, audio_manager, morpher_manager):
        self.config_manager = config_manager
        self.audio_manager = audio_manager
        self.morpher_manager = morpher_manager

    def process_message(self, message, data_queue, morphing_queue):
        print(f'Message received "{message}"')

        if message == "Rec":
            self.audio_manager.toggle_recording(data_queue, morphing_queue)

        elif message == "Play":
            self.audio_manager.play()

        elif message == "Pause":
            self.audio_manager.pause()

        elif message == "Clear":
            self.audio_manager.clear()

        else:
            self._handle_invalid_message(message)

    def _handle_invalid_message(self, message):
        messages = self.config_manager.get_config("controller")["messages"]
        if message not in messages:
            print(f"ERROR. {message} is not a valid message.")


class Controller:
    def __init__(self, App, config_manager):
        self.App = App
        self.connectionIsActive = True
        self.config_manager = config_manager

        # Initialize the new managers
        self.morpher_manager = MorpherManager(config_manager)
        self.audio_manager = AudioManager(config_manager, self.morpher_manager)
        self.morpher_manager.audio_manager = self.audio_manager
        self.message_handler = MessageHandler(
            config_manager, self.audio_manager, self.morpher_manager
        )

        self.exitListener = keyboard.Listener(on_press=self.on_press, daemon=True)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.connectionIsActive = False
            return False

    def run_controller(self, command_queue, data_queue, morphing_queue):
        print("\nEnter 'Esc' to close the connection at any time\n")
        self.exitListener.start()

        while self.connectionIsActive:
            if not command_queue.empty():
                message = command_queue.get()
                self.message_handler.process_message(
                    message, data_queue, morphing_queue
                )

        print("Closing app.")

        try:
            self.App.quit()
        except:
            pass


def main_controller(App, command_queue, data_queue, morphing_queue):
    config_manager = ConfigManager(CONFIG_PATH)
    controller_instance = Controller(App, config_manager)
    controller_instance.run_controller(command_queue, data_queue, morphing_queue)
