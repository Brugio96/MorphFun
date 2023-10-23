import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from utils import CONFIG_PATH, load_config


class Detector:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic  # Holistic model
        self.mp_drawing = mp.solutions.drawing_utils  # Drawing utilities

    def detect(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR 2 RGB
        image_rgb.flags.writeable = False  # Image is no longer writeable
        results = self.mp_holistic.process(image_rgb)  # Make prediction
        return image, results


class KeypointsExtractor:
    POSE_DIMENSION = 4
    HAND_DIMENSION = 3
    POSE_KEYPOINTS = 33
    HAND_KEYPOINTS = 21

    @staticmethod
    def _extract_keypoints(landmarks, dimension):
        if landmarks:
            return np.array(
                [
                    [res.x, res.y, res.z] + ([res.visibility] if dimension == 4 else [])
                    for res in landmarks
                ]
            ).flatten()
        else:
            return np.zeros(
                dimension
                * (
                    len(landmarks)
                    if landmarks
                    else KeypointsExtractor.POSE_KEYPOINTS
                    if dimension == 4
                    else KeypointsExtractor.HAND_KEYPOINTS
                )
            )

    @staticmethod
    def extract(results):
        pose = KeypointsExtractor._extract_keypoints(
            results.pose_landmarks.landmark, KeypointsExtractor.POSE_DIMENSION
        )
        lh = KeypointsExtractor._extract_keypoints(
            results.left_hand_landmarks.landmark, KeypointsExtractor.HAND_DIMENSION
        )
        rh = KeypointsExtractor._extract_keypoints(
            results.right_hand_landmarks.landmark, KeypointsExtractor.HAND_DIMENSION
        )

        return np.concatenate([pose, lh, rh])


class PoseModel:
    def __init__(self, model_path, sequence_length, actions, model_config=None):
        self.actions = actions
        self.model = self._init_model(model_path, sequence_length, model_config)

    def _init_model(self, model_path, sequence_length, config=None):
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
            return_seq = True if i != len(config["lstm_layers"]) - 1 else False
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
        return self.model.predict(np.expand_dims(sequence, axis=0))[0]

    def predict_action(self, sequence, threshold=0.6):
        probabilities = self.predict(sequence)
        predicted_index = np.argmax(probabilities)
        predicted_value = probabilities[predicted_index]

        return (
            self.actions[predicted_index],
            predicted_index if predicted_value > threshold else None,
        )


class PoseEstimation:
    def __init__(self, model_path):
        self.config = load_config(CONFIG_PATH)
        self.detector = Detector()
        self.extractor = KeypointsExtractor()
        self.pose_model = PoseModel(
            model_path,
            self.config["pose_estimation"]["sequence_length"],
            np.array(self.config["pose_estimation"]["actions"]),
        )

    def estimate_pose(self, morphing_queue, data_queue):
        predictions = []
        threshold = 0.6

        self._wait_for_start_sequence(data_queue)

        sequence = data_queue.get()
        while sequence != -1:
            sequence = self._prepare_sequence(sequence)
            if sequence is not None:
                self._handle_prediction(
                    sequence, predictions, morphing_queue, threshold
                )
            sequence = data_queue.get()

    def _wait_for_start_sequence(self, data_queue):
        sequence = data_queue.get()
        while sequence != "start":
            sequence = data_queue.get()

    def _prepare_sequence(self, sequence):
        sequence = np.asarray(sequence)
        if sequence.shape[1] != 30:
            if sequence.shape[1] > 30:
                return sequence[:30, :]
            else:
                return None
        return sequence

    def _handle_prediction(self, sequence, predictions, morphing_queue, threshold):
        predicted_action, predicted_index = self.pose_model.predict_action(
            sequence, threshold
        )
        if predicted_index is not None:
            print(f"Current M0RPH: {predicted_action}")
            if len(predictions) > 0:
                if predicted_action != predictions[-1]:
                    predictions.append(predicted_action)
                    morphing_queue.put(predicted_index)
            else:
                predictions.append(predicted_action)
                morphing_queue.put(predicted_index)
