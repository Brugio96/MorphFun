import threading
from ddsp_utils.DDSP_engine import DDSPEngine
from pose_estimation.pose_estimator import PoseEstimator


class MorpherManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.DDSP_engine = DDSPEngine()
        self.pose_estimator = PoseEstimator(config_manager)
        self.sound_ready_event = threading.Event()

    def transform_audio(self):
        morphing_process = threading.Thread(
            target=self.DDSP_engine.transform_audio, daemon=True
        )
        morphing_process.start()
        morphing_process.join()
        self.sound_ready_event.set()

    def start_pose_estimation(self, morphing_queue, data_queue):
        self.pose_estimator.start_pose_estimation(morphing_queue, data_queue)
