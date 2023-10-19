from pose_estimation.pose_estimation_loop import estimate_pose
import threading


class PoseEstimator:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def start_pose_estimation(self, morphing_queue, data_queue):
        pose_estimation = threading.Thread(
            target=estimate_pose,
            args=(
                self.config_manager.get_config("files")["model_path"],
                morphing_queue,
                data_queue,
            ),
            daemon=True,
        )
        pose_estimation.start()
