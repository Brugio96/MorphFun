"""
pose_estimation.py

This module defines the KeypointsExtractor and KeypointsProcessor classes for the pose estimation. It includes logic for detecting and extracting keypoints from images using the mediapipe library. The KeypointsExtractor class integrates with the mediapipe's Holistic model to orchestrate the core functionalities of keypoints detection and extraction.

Classes:
    KeypointsExtractor: Extracts pose, left hand, and right hand keypoints from images.
    KeypointsProcessor: Processes frames to extract and manage sequences of keypoints for further analysis or action.

"""

import cv2
import mediapipe as mp
import numpy as np


class KeypointsExtractor:
    """
    This class uses mediapipe's Holistic model to extract keypoints related to pose, hands, and face from images.

    Attributes:
        _model: An instance of mediapipe's Holistic model configured with minimum detection and tracking confidence.
        LANDMARK_SIZES: A dictionary specifying the number of landmarks and their dimensions for pose and hand keypoints.

    Methods:
        detect_keypoints: Detects and returns the keypoints from a given image.
        extract_keypoints: Extracts and concatenates pose and hand keypoints from the detection results.
        _extract_landmarks: Helper method to flatten the detected landmarks.
    """

    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initializes the KeypointsExtractor with mediapipe's Holistic model with specified confidence levels.

        Parameters:
            min_detection_confidence: The minimum confidence value ([0.0, 1.0]) for the detection to be considered successful.
            min_tracking_confidence: The minimum confidence value ([0.0, 1.0]) for the tracking to be considered successful.
        """
        self._model = mp.solutions.holistic.Holistic(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.LANDMARK_SIZES = {"pose": (33, 4), "hand": (21, 3)}

    def detect_keypoints(self, image):
        """
        Detects keypoints in the given BGR image using the initialized Holistic model.

        Parameters:
            image: The image in which keypoints are to be detected.

        Returns:
            A processed image with detected landmarks by the Holistic model.
        """
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            return self._model.process(image_rgb)
        except Exception as e:
            raise Exception(f"Error detecting keypoints: {e}")

    def _extract_landmarks(self, landmarks, landmark_type):
        """
        Extracts and flattens the landmarks from the provided mediapipe landmark results based on the specified type.

        Parameters:
            landmarks: The landmark results from mediapipe's Holistic model.
            landmark_type: A string indicating the type of landmarks to extract ('pose' or 'hand').

        Returns:
            A flattened numpy array of the landmarks.
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
        Extracts and concatenates the keypoints for pose, left hand, and right hand from the detection results.

        Parameters:
            results: The detection results containing the pose, left hand, and right hand landmarks.

        Returns:
            A numpy array containing the flattened keypoints for pose, left hand, and right hand.
        """
        pose = self._extract_landmarks(results.pose_landmarks, "pose")
        left_hand = self._extract_landmarks(results.left_hand_landmarks, "hand")
        right_hand = self._extract_landmarks(results.right_hand_landmarks, "hand")

        return np.concatenate([pose, left_hand, right_hand])


class KeypointsProcessor:
    """
    Processes frames to extract and manage sequences of keypoints.

    Attributes:
        keypoints_extractor: An instance of KeypointsExtractor to extract keypoints from frames.
        queue: A queue to store sequences of keypoints for further processing.
        boost: An integer representing the factor by which the counter is incremented.
        SEQUENCE_LENGTH: The fixed length of the keypoints sequence to be maintained.

    Methods:
        update_frame_data: Updates the keypoints sequence with keypoints extracted from a new frame.
        _extract_keypoints_from_frame: Extracts keypoints from the provided frame.
        _update_sequence_and_counter: Manages the keypoints sequence and counter.
    """

    SEQUENCE_LENGTH = 30

    def __init__(self, queue, boost):
        """
        Initializes KeypointsProcessor with a queue for storing sequences and a boost factor for the counter.

        Parameters:
            queue: A queue to store sequences of keypoints for further processing.
            boost: An integer representing the boost factor for the counter.
        """
        self.keypoints_extractor = KeypointsExtractor()
        self.queue = queue
        self.boost = boost

    def update_frame_data(self, frame, counter, sequence):
        """
        Updates the keypoints sequence with keypoints extracted from a new frame and manages the sequence length.

        Parameters:
            frame: The frame from which to extract keypoints.
            counter: The current value of the counter.
            sequence: The current sequence of keypoints.

        Returns:
            A tuple of the updated counter and keypoints sequence.
        """
        keypoints = self._extract_keypoints_from_frame(frame)
        sequence.append(keypoints)
        sequence = sequence[-self.SEQUENCE_LENGTH :]
        counter = self._update_sequence_and_counter(sequence, counter)
        return counter, sequence

    def _extract_keypoints_from_frame(self, frame):
        """
        Extracts keypoints from the given frame using the KeypointsExtractor.

        Parameters:
            frame: The frame from which to extract keypoints.

        Returns:
            A numpy array of extracted keypoints.
        """
        results = self.keypoints_extractor.detect_keypoints(frame)
        keypoints = self.keypoints_extractor.extract_keypoints(results)
        return keypoints

    def _update_sequence_and_counter(self, sequence, counter):
        """
        Manages the keypoints sequence and counter. If the sequence reaches the set length, it is added to the queue and the counter is reset.

        Parameters:
            sequence: The current keypoints sequence.
            counter: The current value of the counter.

        Returns:
            The updated value of the counter.
        """
        if len(sequence) == self.SEQUENCE_LENGTH:
            if counter == self.SEQUENCE_LENGTH * self.boost:
                self.queue.put(sequence)
                counter = 0
            else:
                counter += 1
        return counter
