from threading import Thread
from pose_estimation.pose_estimation_loop import PoseEstimation


class PoseEstimator:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.model_path = self.config_manager.get_config("files")["model_path"]
        self.pose_estimation = PoseEstimation(self.model_path)

    def start_pose_estimation(self, morphing_queue, data_queue):
        pose_estimation_thread = Thread(
            target=self.pose_estimation.estimate_pose,
            args=(morphing_queue, data_queue),
            daemon=True,
        )
        pose_estimation_thread.start()
