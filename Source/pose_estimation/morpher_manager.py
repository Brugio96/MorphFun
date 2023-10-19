import threading
from ddsp_functions.morpher_module import MorpherClass
from pose_estimation.pose_estimator import PoseEstimator


class MorpherManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.morpherClass = MorpherClass()
        self.pose_estimator = PoseEstimator(config_manager)
        self.audio_manager = None
        self.sound_ready_event = threading.Event()

    def transform_audio(self):
        morphing_process = threading.Thread(
            target=self.morpherClass.transform_audio, daemon=True
        )
        morphing_process.start()
        morphing_process.join()

        audio_folder = self.config_manager.get_config("files")["audio"]
        self.audio_manager.audio_controller_instance.audio_controller.load_sounds()
        print(f"Audios were generated and saved to {audio_folder}.")
        self.sound_ready_event.set()

    def start_pose_estimation(self, morphing_queue, data_queue):
        self.pose_estimator.start_pose_estimation(morphing_queue, data_queue)

    def start_morphing(self, morphing_queue):
        self.sound_ready_event.wait()
        morphing_thread = threading.Thread(
            target=self.audio_manager.audio_controller_instance.audio_controller.start_morphing,
            args=(morphing_queue,),
            daemon=True,
        )
        morphing_thread.start()
