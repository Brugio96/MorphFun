"""
gui_events.py

This module defines the GuiEvents class for the application. It includes logic for handling synchronization between different GUI components through threading events. The GuiEvents class integrates with various components like buttons and triggers to orchestrate the core functionalities of user interaction within the application.

Classes:
    GuiEvents: Manages threading events for GUI interaction.
"""

import threading


class GuiEvents:
    """
    Manages threading events to synchronize user interactions in the GUI.

    Attributes:
        start_recording (threading.Event): Event to signal the start of a recording.
        stop_recording (threading.Event): Event to signal the stop of a recording.
        play (threading.Event): Event to signal that playback should start.
        pause (threading.Event): Event to signal that playback should pause.
        clear (threading.Event): Event to signal that the current data should be cleared.
        events_map (dict): A mapping of event names to their threading.Event objects.

    Methods:
        get_triggered_event: Returns the name of the event that was triggered, if any.
        reset_event: Resets the specified event to its default state (not set).
    """

    def __init__(self):
        """
        Initializes the GuiEvents with threading events for start, stop, play, pause, and clear actions.
        """
        self.start_recording = threading.Event()
        self.stop_recording = threading.Event()
        self.play = threading.Event()
        self.pause = threading.Event()
        self.clear = threading.Event()
        self.events_map = {
            "start_recording": self.start_recording,
            "stop_recording": self.stop_recording,
            "play": self.play,
            "pause": self.pause,
            "clear": self.clear,
        }

    def get_triggered_event(self):
        """
        Checks all events and returns the name of the event that is set.

        Returns:
            str: The name of the triggered event, or None if no event is set.
        """
        for event_name, event_obj in self.events_map.items():
            if event_obj.is_set():
                return event_name
        return None

    def reset_event(self, event_name):
        """
        Resets the specified event, allowing it to be triggered again.

        Parameters:
            event_name (str): The name of the event to reset.
        """
        event_obj = self.events_map.get(event_name)
        if event_obj:
            event_obj.clear()
