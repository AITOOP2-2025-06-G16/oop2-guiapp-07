import sys
import cv2
import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout


class MyVideoCapture(QWidget):
    """
    PySide6 で動く Webカメラキャプチャアプリ（課題用）
    - ウィンドウを表示
    - カメラ映像を QLabel に表示
    - 「写真を撮る」ボタンで画像を保存
    """

    def __init__(self):
        super().__init__()

        # --- UI 構築 ---
        self.setWindowTitle("Camera Capture")
        self.label = QLabel("カメラ映像がここに表示されます")
        self.label.setFixedSize(640, 480)

        self.btn_capture = QPushButton("写真を撮る")
        self.btn_capture.clicked.connect(self.capture_image)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_capture)
        self.setLayout(layout)

        # --- カメラ初期化 ---
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.captured_img = None

        # --- タイマーでフレーム更新 ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)   # 30msごとに更新

    def update_frame(self):
        """カメラ映像を1フレーム取得して QLabel に表示"""
        ret, frame = self.cap.read()
        if not ret:
            return

        img = frame.copy()

        # ターゲットマーク描画
        rows, cols, _ = img.shape
        center = (cols // 2, rows // 2)
        img = cv2.circle(img, center, 30, (0, 0, 255), 3)
        img = cv2.circle(img, center, 60, (0, 0, 255), 3)
        img = cv2.line(img, (center[0], center[1] - 80),
                       (center[0], center[1] + 80), (0, 0, 255), 3)
        img = cv2.line(img, (center[0] - 80, center[1]),
                       (center[0] + 80, center[1]), (0, 0, 255), 3)

        # 左右反転
        img = cv2.flip(img, 1)

        # OpenCV → Qt 表示形式へ変換
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        # ラベルに表示
        self.label.setPixmap(pix)
        self.current_frame = frame.copy()

    def capture_image(self):
        """現在のフレームを撮影して保存"""
        if hasattr(self, "current_frame"):
            self.captured_img = self.current_frame.copy()
            cv2.imwrite("camera_capture.png", self.captured_img)
            print("写真を保存しました → camera_capture.png")

    def __del__(self):
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyVideoCapture()
    window.show()
    sys.exit(app.exec())
