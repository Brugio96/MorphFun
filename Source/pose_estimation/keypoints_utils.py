import cv2
import mediapipe as mp
import numpy as np


class KeypointsExtractor:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the KeypointsExtractor with mediapipe's Holistic model.
        """
        self._model = mp.solutions.holistic.Holistic(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.LANDMARK_SIZES = {"pose": (33, 4), "hand": (21, 3)}

    def detect_keypoints(self, image):
        """
        Detect keypoints in the given BGR image and return the detected landmarks.
        """
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            return self._model.process(image_rgb)
        except Exception as e:
            raise Exception(f"Error detecting keypoints: {e}")

    def _extract_landmarks(self, landmarks, landmark_type):
        """
        Helper method to extract and flatten landmarks from the provided data.
        """
        num_landmarks, dimensions = self.LANDMARK_SIZES[landmark_type]
        if landmarks:
            if landmark_type == "pose":
                return np.array(
                    [
                        [res.x, res.y, res.z, res.visibility]
                        for res in landmarks.landmark
                    ]
                ).flatten()
            else:
                return np.array(
                    [[res.x, res.y, res.z][:dimensions] for res in landmarks.landmark]
                ).flatten()
        return np.zeros(num_landmarks * dimensions)

    def extract_keypoints(self, results):
        """
        Extract and flatten keypoints from the detection results.
        """
        pose = self._extract_landmarks(results.pose_landmarks, "pose")
        left_hand = self._extract_landmarks(results.left_hand_landmarks, "hand")
        right_hand = self._extract_landmarks(results.right_hand_landmarks, "hand")

        return np.concatenate([pose, left_hand, right_hand])


class KeypointsProcessor:
    """Processes frames to extract and manage sequences of keypoints."""

    SEQUENCE_LENGTH = 30

    def __init__(self, queue, boost):
        """Initializes with a queue for storing sequences and a boost factor."""
        self.keypoints_extractor = KeypointsExtractor()
        self.queue = queue
        self.boost = boost

    def update_frame_data(self, frame, counter, sequence):
        """Updates the keypoints sequence with data from a new frame."""
        keypoints = self._extract_keypoints_from_frame(frame)
        sequence.append(keypoints)
        sequence = sequence[-self.SEQUENCE_LENGTH :]
        counter = self._update_sequence_and_counter(sequence, counter)
        return counter, sequence

    def _extract_keypoints_from_frame(self, frame):
        """Extracts keypoints from the given frame."""
        results = self.keypoints_extractor.detect_keypoints(frame)
        keypoints = self.keypoints_extractor.extract_keypoints(results)
        return keypoints

    def _update_sequence_and_counter(self, sequence, counter):
        """Manages the sequence and counter based on the current sequence length."""
        if len(sequence) == self.SEQUENCE_LENGTH:
            if counter == self.SEQUENCE_LENGTH * self.boost:
                self.queue.put(sequence)
                counter = 0
            else:
                counter += 1
        return counter
