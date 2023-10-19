from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog
from PyQt5.QtGui import QPixmap
from pynput.keyboard import Key, Controller
import cv2
import numpy as np
from utils import CONFIG_PATH, load_config
from keypoints_utils import KeypointsExtractor


class WebcamThread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, data_queue, parent=None):
        super(WebcamThread, self).__init__(parent=parent)
        self.is_running = True
        self.queue = data_queue
        self.keypoints_extractor = KeypointsExtractor()

    def run(self):
        sequence_length = 30
        sequence = []
        cap = cv2.VideoCapture(0)
        counter = 0
        config = load_config(CONFIG_PATH)
        boost = config["pose_estimation"]["latency_factor"]

        while self.is_running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Detect keypoints
                results = self.keypoints_extractor.detect_keypoints(frame)

                # Extract keypoints data
                keypoints = self.keypoints_extractor.extract_keypoints(results)
                sequence.append(keypoints)
                sequence = sequence[-sequence_length:]

                if len(sequence) == sequence_length:
                    if counter == 30 * boost:
                        self.queue.put(sequence)
                        counter = 0
                    else:
                        counter += 1

                # Convert the frame for display in the GUI
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgbImage = rgbImage[5:463, 80:560]  # Crop the image
                rgbImage = cv2.flip(rgbImage, 1)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(
                    rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888
                )
                p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

        cap.release()  # Release the webcam resource

    def stop(self):
        self.is_running = False


class Window(QDialog):
    ICON_PATH = "./Source/images/music-notes.ico"
    BACKGROUND_PATH = "./Source/images/background.png"
    REC_BUTTON_PATH = "./Source/images/recbutton.png"
    REC_BUTTON_PRESSED_PATH = "./Source/images/recbutton_pressed.png"
    REC_BUTTON_ON_PATH = "./Source/images/recbutton_on.png"
    PLAY_BUTTON_PATH = "./Source/images/playbutton.png"
    PLAY_BUTTON_PRESSED_PATH = "./Source/images/playbutton_pressed.png"
    STOP_BUTTON_PATH = "./Source/images/stopbutton.png"
    STOP_BUTTON_PRESSED_PATH = "./Source/images/stopbutton_pressed.png"
    CLEAR_BUTTON_PATH = "./Source/images/clearbutton.png"
    CLEAR_BUTTON_PRESSED_PATH = "./Source/images/clearbutton_pressed.png"

    def __init__(self, cmd_queue, data_queue):
        super().__init__()

        self.title = "MorphFun"
        self.left = 350
        self.top = 180
        self.width = 1280
        self.height = 720
        self.paused = False
        self.isRecording = False

        self.InitWindow(cmd_queue, data_queue)

    def closeEvent(self, event):
        keyboard = Controller()
        keyboard.press(Key.esc)

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def sendMessageAtClick(self, cmd_queue, message):
        cmd_queue.put(message)

    def setButtonStyle(self, button, normal_image, pressed_image):
        button.setStyleSheet(
            f"QPushButton{{background-image: url({normal_image}); background-repeat: no-repeat; border: none;}}"
            f"QPushButton::pressed{{background-image: url({pressed_image});}}"
        )

    def play_pause(self, cmd_queue):
        if self.paused:
            self.setButtonStyle(
                self.play_btn, self.PLAY_BUTTON_PATH, self.PLAY_BUTTON_PRESSED_PATH
            )
            self.paused = False
            self.sendMessageAtClick(cmd_queue, "Play")
        else:
            self.setButtonStyle(
                self.play_btn, self.STOP_BUTTON_PATH, self.STOP_BUTTON_PRESSED_PATH
            )
            self.paused = True
            self.sendMessageAtClick(cmd_queue, "Pause")

    def recording(self, cmd_queue):
        if self.isRecording:
            self.setButtonStyle(
                self.rec_btn, self.REC_BUTTON_PATH, self.REC_BUTTON_PRESSED_PATH
            )
            self.setButtonStyle(
                self.play_btn, self.PLAY_BUTTON_PATH, self.PLAY_BUTTON_PRESSED_PATH
            )
            self.paused = False
            self.isRecording = False
            self.sendMessageAtClick(cmd_queue, "Rec")
        else:
            self.setButtonStyle(
                self.rec_btn, self.REC_BUTTON_ON_PATH, self.REC_BUTTON_PRESSED_PATH
            )
            self.isRecording = True
            self.sendMessageAtClick(cmd_queue, "Rec")

    def InitWindow(self, cmd_queue, data_queue):
        self.setWindowIcon(QtGui.QIcon(self.ICON_PATH))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        vbox = QVBoxLayout()
        labelImage = QLabel(self)
        pixmap = QPixmap(self.BACKGROUND_PATH)
        labelImage.setPixmap(pixmap)
        vbox.addWidget(labelImage)

        self.label = QLabel(self)
        self.label.move(61, 67)
        self.label.resize(495, 470)
        self.label.setStyleSheet("border: 2px solid #fcd462; border-radius: 5px;")

        th = WebcamThread(data_queue)
        th.changePixmap.connect(self.setImage)
        th.start()

        self.rec_btn = QtWidgets.QPushButton(self)
        self.rec_btn.setGeometry(93, 577, 123, 100)
        self.setButtonStyle(
            self.rec_btn, self.REC_BUTTON_PATH, self.REC_BUTTON_PRESSED_PATH
        )
        self.rec_btn.clicked.connect(lambda: self.recording(cmd_queue))

        self.play_btn = QtWidgets.QPushButton(self)
        self.play_btn.setGeometry(243, 576, 123, 88)
        self.setButtonStyle(
            self.play_btn, self.PLAY_BUTTON_PATH, self.PLAY_BUTTON_PRESSED_PATH
        )
        self.play_btn.clicked.connect(lambda: self.play_pause(cmd_queue))

        self.clear_btn = QtWidgets.QPushButton(self)
        self.clear_btn.setGeometry(393, 576, 123, 88)
        self.setButtonStyle(
            self.clear_btn, self.CLEAR_BUTTON_PATH, self.CLEAR_BUTTON_PRESSED_PATH
        )
        self.clear_btn.clicked.connect(
            lambda: self.sendMessageAtClick(cmd_queue, "Clear")
        )

        self.show()
