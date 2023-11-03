"""
controller.py

This module defines the controller and command handler for the application. It includes the logic for handling user commands, managing audio recording and playback, performing timbre transfer, and classifying poses using a separate thread manager. The Controller class integrates with various components like the audio manager, timbre transfer engine, and pose classifier to orchestrate the application's core functionalities.

Classes:
    CommandHandler: Interprets and executes user commands routed through the GUI.
    Controller: Manages the primary logic flow of the application, coordinating between user inputs, audio processing, and system events.
"""

import logging
import threading
from pynput import keyboard

from utils import CONFIG_PATH
from CONFIG.config_manager import ConfigManager
from audio.audio_manager import AudioManager
from timbre_transfer.DDSP_engine import DDSPEngine
from pose.pose_classifier import PoseClassifier

# Constants for commands
START_REC = "Start Rec"
STOP_REC = "Stop Rec"
PLAY = "Play"
PAUSE = "Pause"
CLEAR = "Clear"


class CommandHandler:
    """
    A command interpreter that executes actions based on user commands from the GUI.

    It maps predefined commands to the corresponding methods in the controller and processes incoming commands to invoke these methods.
    """

    def __init__(self, controller):
        """
        Initializes the CommandHandler with a reference to the controller object.

        Parameters:
            controller: The main controller instance which contains methods for command execution.
        """
        self.controller = controller
        self.command_actions = {
            START_REC: self.controller.start_recording,
            STOP_REC: self.controller.stop_recording_and_process,
            PLAY: self.controller.play_audio,
            PAUSE: self.controller.pause_audio,
            CLEAR: self.controller.clear,
        }

    def process_command(self, command):
        """
        Executes the action associated with the received command.

        Parameters:
            command: A string indicating the command to process.
        """
        print(f"Received Command: {command}")
        action = self.command_actions.get(command, self._handle_invalid_command)
        action()

    def _handle_invalid_command(self):
        """Log an error message when an invalid command is received."""
        logging.error("Received an invalid command.")


class Controller:
    """
    Initializes the Controller with necessary components and state variables.

    Parameters:
        app: The main PyQt5 QApplication object that manages the GUI.
        thread_manager: The ThreadManager object that manages threading operations.
    """

    def __init__(self, app, thread_manager):
        self.app = app
        self.connection_is_active = True
        self.config_manager = ConfigManager(CONFIG_PATH)
        self.audio_manager = AudioManager(self.config_manager)
        self.pose_classifier = PoseClassifier(self.config_manager)
        self.ddsp_engine = DDSPEngine()
        self.thread_manager = thread_manager
        self.command_queue = self.thread_manager.get_queue("gui_commands")
        self.command_handler = CommandHandler(self)
        self.exit_listener = keyboard.Listener(on_press=self.on_press, daemon=True)
        self.is_first_recording = True

    def start_recording(self):
        """Start the audio recording process."""
        if not self.is_first_recording:
            self.clear()
        self.audio_manager.toggle_recording()

    def stop_recording_and_process(self):
        """Stop the recording and process the audio for playback and morphing."""
        self.is_first_recording = False
        self.stop_recording()
        self.playback_recorded_audio()
        self.perform_timbre_transfer()
        self.pose_classification()
        self.start_audio_morphing()

    def stop_recording(self):
        """Stop the audio recording and save the audio file."""
        self.audio_manager.toggle_recording()
        self.audio_manager.save_recorded_audio()

    def playback_recorded_audio(self):
        """Play back the recorded audio."""
        self.audio_manager.play_recorded_audio()

    def perform_timbre_transfer(self):
        """Perform a timbre transfer on the recorded audio."""
        logging.info("Morphing begins")
        self.ddsp_engine.timbre_transfer()
        self.audio_manager.load_sounds()

    def pose_classification(self):
        """Start the pose classification process."""
        self._initialize_thread_events_and_queues()
        self.thread_manager.start_thread(
            "pose_classification_thread",
            target_function=self.pose_classifier.classify_pose,
            args=(self.thread_manager,),
        )

    def start_audio_morphing(self):
        """Begin audio morphing in the player."""
        self.thread_manager.start_thread(
            "audio_morphing",
            self.audio_manager.audio_player.start_morphing,
            args=(self.thread_manager,),
        )

    def play_audio(self):
        """Play audio."""
        self.audio_manager.play()

    def pause_audio(self):
        """Pause audio playback."""
        self.audio_manager.pause()

    def stop_thread(self, thread_name):
        """
        Stops the specified thread managed by the thread manager, ensuring graceful termination and resource release.

        Parameters:
            thread_name (str): The name of the thread to be stopped.
        """
        try:
            if self.thread_manager.is_thread_active(thread_name):
                self.thread_manager.stop_thread(thread_name)
        except Exception as e:
            logging.error(f"Error while stopping thread {thread_name}: {e}")

    def clear(self):
        """Clear the current audio, stopping playback and resetting the state."""
        self.audio_manager.clear()
        self.stop_thread("pose_classification_thread")
        self.stop_thread("audio_morphing")

    def _initialize_thread_events_and_queues(self):
        """Initialize thread-related events and queues."""
        self.thread_manager.set_event("start_extraction")
        self.thread_manager.create_event("start_pose_classification")
        self.thread_manager.set_event("start_pose_classification")
        self.thread_manager.create_queue("morphing_data")

    def run(self, stop_event):
        """
        Starts the controller's main event loop, listening for commands and shutting down on request.

        Parameters:
            stop_event: A threading event to signal when to stop the loop and exit the application.
        """
        logging.info("Press 'Esc' to close the connection at any time")
        self.exit_listener.start()
        while self.connection_is_active:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                self.command_handler.process_command(command)

            # Controlla se l'evento di stop è stato segnalato
            if stop_event and stop_event.is_set():
                break  # Esci dal ciclo principale

        self.close_app()

    def on_press(self, key):
        """
        Responds to key press events, particularly the 'Esc' key to terminate the application.

        Parameters:
            key: The key that was pressed.
        """
        if key == keyboard.Key.esc:
            self.connection_is_active = False
            return False

    def close_app(self):
        """Closes the application, ensuring all resources are freed and threads are terminated safely."""
        logging.info("Closing app.")
        try:
            # Ottieni l'ID del thread corrente
            current_thread_id = threading.get_ident()

            # Termina tutti i thread attivi eccetto il thread corrente
            for thread_name, thread in list(self.thread_manager.threads.items()):
                if thread.ident != current_thread_id:
                    self.thread_manager.stop_thread(thread_name)

            # Chiudi l'applicazione GUI
            self.app.quit()

        except Exception as e:
            logging.error(f"Error closing app: {e}")
