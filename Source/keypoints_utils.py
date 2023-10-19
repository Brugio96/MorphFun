import cv2
import mediapipe as mp
import numpy as np


class KeypointsExtractor:
    def __init__(self):
        self._model = mp.solutions.holistic.Holistic(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

    def detect_keypoints(self, image):
        """
        Detect keypoints in the given image.
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Color conversion BGR to RGB
        image.flags.writeable = False  # Image is no longer writeable
        results = self._model.process(image)  # Make prediction
        return results

    def extract_keypoints(self, results):
        """
        Extract keypoints from the detection results.
        """
        pose = (
            np.array(
                [
                    [res.x, res.y, res.z, res.visibility]
                    for res in results.pose_landmarks.landmark
                ]
            ).flatten()
            if results.pose_landmarks
            else np.zeros(33 * 4)
        )
        lh = (
            np.array(
                [[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]
            ).flatten()
            if results.left_hand_landmarks
            else np.zeros(21 * 3)
        )
        rh = (
            np.array(
                [[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]
            ).flatten()
            if results.right_hand_landmarks
            else np.zeros(21 * 3)
        )
        return np.concatenate([pose, lh, rh])
