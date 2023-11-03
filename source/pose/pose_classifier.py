"""
pose_classifier.py

This module defines the PoseModel and PoseClassifier classes for the application focused on classifying poses from sequences of keypoints. It includes logic for predicting human poses based on a pre-trained model and sequences provided in real-time. The PoseClassifier orchestrates the process of predicting and classifying poses, utilizing components like TensorFlow and custom utility functions, to manage pose classification flows within the application.

Classes:
    PoseModel: Handles the creation and inference of the neural network model for pose classification.
    PoseClassifier: Manages the classification process by interacting with PoseModel and the application threading system.

"""

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from utils import CONFIG_PATH, load_config
from queue import Empty


class PoseModel:
    """
    This class is responsible for initializing and utilizing a neural network model for classifying poses based on sequences of keypoints.

    Attributes:
        actions (list): List of possible actions that the model can classify.
        model (Sequential): The TensorFlow/Keras sequential model for pose classification.

    Methods:
        _init_model: Initializes and compiles the LSTM neural network.
        predict: Makes a prediction on a single sequence of keypoints.
        predict_action: Predicts the human action from a sequence of keypoints with a confidence threshold.
    """

    def __init__(self, model_path, sequence_length, actions, model_config=None):
        """
        Initializes the PoseModel with a specified path to the model weights, sequence length for the input data, and possible actions.

        Parameters:
            model_path (str): The path to the pre-trained model weights.
            sequence_length (int): The length of the input sequence the model expects.
            actions (list): A list of actions that the model is trained to recognize.
            model_config (dict, optional): Configuration for the LSTM and Dense layers of the model.
        """
        self.actions = actions
        self.model = self._init_model(model_path, sequence_length, model_config)

    def _init_model(self, model_path, sequence_length, config=None):
        """
        Initializes and constructs the neural network architecture for the pose classification.

        Parameters:
            model_path (str): The path to the pre-trained model weights.
            sequence_length (int): The length of the input sequence.
            config (dict): The configuration dictionary for the model's layers and dimensions.

        Returns:
            Sequential: The compiled TensorFlow/Keras model.
        """
        if config is None:
            config = {
                "lstm_layers": [64, 128, 64],
                "dense_layers": [64, 32],
                "input_dim": 258,
                "num_classes": len(self.actions),
            }

        model = Sequential()

        # Add LSTM layers
        for i, units in enumerate(config["lstm_layers"]):
            return_seq = i != len(config["lstm_layers"]) - 1
            if i == 0:
                model.add(
                    LSTM(
                        units,
                        return_sequences=return_seq,
                        activation="relu",
                        input_shape=(sequence_length, config["input_dim"]),
                    )
                )
            else:
                model.add(LSTM(units, return_sequences=return_seq, activation="relu"))

        # Add Dense layers
        for units in config["dense_layers"]:
            model.add(Dense(units, activation="relu"))

        model.add(Dense(config["num_classes"], activation="softmax"))
        model.load_weights(model_path)

        return model

    def predict(self, sequence):
        """
        Predicts the probabilities of each action for a single sequence of keypoints.

        Parameters:
            sequence (np.array): The input sequence of keypoints for which to make the prediction.

        Returns:
            np.array: Probabilities of each action for the input sequence.
        """
        return self.model.predict(np.expand_dims(sequence, axis=0))[0]

    def predict_action(self, sequence, threshold=0.6):
        """
        Predicts the most likely action and its index from a sequence of keypoints, with a confidence level above the given threshold.

        Parameters:
            sequence (np.array): The input sequence of keypoints for which to predict the action.
            threshold (float): The confidence threshold for accepting a prediction.

        Returns:
            tuple: A tuple containing the predicted action and the corresponding index if the confidence is above the threshold; otherwise, None for the index.
        """
        probabilities = self.predict(sequence)
        predicted_index = np.argmax(probabilities)
        predicted_value = probabilities[predicted_index]

        return (
            self.actions[predicted_index],
            predicted_index if predicted_value > threshold else None,
        )


class PoseClassifier:
    """
    This class manages the pose classification process by coordinating the interaction between the neural network model and the threading system in the application.

    Attributes:
        config_manager: An object to manage configuration settings for the classifier.
        model_path (str): The path to the neural network model file.
        config (dict): Configuration settings for the classifier.
        pose_model (PoseModel): The PoseModel object used for predicting actions.

    Methods:
        classify_pose: Processes keypoints to classify poses and sends predictions to the morphing system.
        _prepare_sequence: Prepares the input sequence for classification.
        _handle_prediction: Handles the prediction results and updates the morphing system.
    """

    def __init__(self, config_manager):
        """
        Initializes the PoseClassifier with a configuration manager.

        Parameters:
            config_manager: An object that provides access to configuration data.
        """
        self.config_manager = config_manager
        self.model_path = self.config_manager.get_config("files")["model_path"]
        self.config = load_config(CONFIG_PATH)
        self.pose_model = PoseModel(
            self.model_path,
            self.config["pose_classification"]["sequence_length"],
            np.array(self.config["pose_classification"]["actions"]),
        )

    def classify_pose(self, thread_manager, stop_event):
        """
        Runs the pose classification process within a thread, classifying poses and updating the morphing queue with predictions.

        Parameters:
            thread_manager: The manager handling different threads in the application.
            stop_event: An event to signal when to stop the classification process.
        """
        predictions = []
        threshold = 0.6

        keypoints_queue = thread_manager.get_queue("keypoints_data")
        morphing_queue = thread_manager.get_queue("morphing_data")

        while not stop_event.is_set():
            try:
                sequence = keypoints_queue.get(timeout=1)
            except Empty:
                continue

            if sequence == -1:
                break

            if thread_manager.is_event_set("start_pose_classification"):
                sequence = self._prepare_sequence(sequence)
                if sequence is not None:
                    predicted_index = self._handle_prediction(
                        sequence, predictions, threshold
                    )
                    if predicted_index is not None:
                        morphing_queue.put(predicted_index)

    def _prepare_sequence(self, sequence):
        """
        Prepares and validates the input sequence for classification.

        Parameters:
            sequence (list): The raw sequence of keypoints.

        Returns:
            np.array: The prepared sequence ready for prediction or None if the sequence is not valid.
        """
        sequence = np.asarray(sequence)

        if sequence.shape[1] != 30:
            if sequence.shape[1] > 30:
                return sequence[:30, :]
            else:
                return None
        return sequence

    def _handle_prediction(self, sequence, predictions, threshold):
        """
        Processes the prediction made by the PoseModel and manages the list of previous predictions.

        Parameters:
            sequence (np.array): The sequence of keypoints to predict the action for.
            predictions (list): The list of previous predictions.
            threshold (float): The threshold for a confident prediction.

        Returns:
            int: The index of the predicted action to be sent to the morphing system or None if the prediction is not confident.
        """
        predicted_action, predicted_index = self.pose_model.predict_action(
            sequence, threshold
        )

        if predicted_index is not None:
            print(f"Current M0RPH: {predicted_action}")
            if len(predictions) > 0:
                if predicted_action != predictions[-1]:
                    predictions.append(predicted_action)
                    return predicted_index
            else:
                predictions.append(predicted_action)
                return predicted_index
        return None
