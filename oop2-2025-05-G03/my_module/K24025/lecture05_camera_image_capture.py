import cv2
import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap


class MyVideoCaptureQt:
    """
    PySide6 GUI で扱うための Webカメラキャプチャクラス。
    - QTimer で一定間隔ごとにフレーム取得
    - QLabel に表示できる QPixmap を生成
    - 最後に撮影した画像を NumPy 配列として保持・取得可能
    """

    def __init__(self, label, width=640, height=480):
        """
        Args:
            label (QLabel): 映像表示先
            width (int): カメラ画像の幅
            height (int): カメラ画像の高さ
        """
        self.label = label
        self.width = width
        self.height = height

        # OpenCV カメラ起動
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.captured_img = None  # 最後に撮影した画像（numpy配列）

        # --- PySide6 用のタイマー ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def start(self):
        """カメラ映像の取得開始"""
        self.timer.start(100)

    def stop(self):
        """カメラ停止"""
        self.timer.stop()

    def update_frame(self):
        """フレームを取得して QLabel に表示"""
        ret, frame = self.cap.read()
        if not ret:
            return

        # 加工するともとの frame が使えないためコピー
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

        # OpenCV(BGR) → Qt(RGB)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        # QLabel に表示
        self.label.setPixmap(pix)

        # 現在のフレームを保存（後で撮影できる）
        self.current_frame = frame.copy()

    def capture(self):
        """
        現在表示中の画像を撮影して保持する。
        Returns:
            numpy.ndarray: 撮影した画像
        """
        if hasattr(self, "current_frame"):
            self.captured_img = self.current_frame.copy()
            return self.captured_img
        return None

    def get_img(self):
        """撮影済み画像（numpy形式）を返す"""
        return self.captured_img

    def __del__(self):
        """終了処理"""
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
