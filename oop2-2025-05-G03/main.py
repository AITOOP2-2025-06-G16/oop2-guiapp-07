import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFrame
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer

# =================================================================
# 1. 画像合成クラス (lecture05_k24025.py のロジックを移植)
# =================================================================
class ImageProcessor:
    @staticmethod
    def synthesize(base_img_path: str, capture_img: np.ndarray) -> np.ndarray:
        """
        背景画像の白色部分をキャプチャ画像で置換する処理
        """
        # 背景画像 (google.png) の読み込み
        google_img = cv2.imread(base_img_path)
        if google_img is None:
            raise FileNotFoundError(f"{base_img_path} が見つかりません。")

        # サイズ取得
        g_hight, g_width, _ = google_img.shape
        c_hight, c_width, _ = capture_img.shape

        # 加工用にコピー
        result_img = google_img.copy()

        # lecture05_k24025.py のロジック: ピクセルごとに判定して置換
        # (処理速度向上のため本来はNumpy機能を使いますが、講義のロジックを尊重します)
        for x in range(g_width):
            for y in range(g_hight):
                # BGRの順で取得
                b, g, r = result_img[y, x]
                
                # もし白色(255,255,255)だったら置き換える
                if (b, g, r) == (255, 255, 255):
                    # キャプチャ画像をグリッド状に並べる計算
                    cap_x = x % c_width
                    cap_y = y % c_hight
                    
                    # 画素の置換
                    result_img[y, x] = capture_img[cap_y, cap_x]
        
        return result_img

# =================================================================
# 2. カメラ管理クラス (lecture05_camera_image_capture.py をGUI用に改良)
# =================================================================
class CameraManager:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            # ID 0で開けない場合、1を試す（Macや一部PC用）
            self.cap = cv2.VideoCapture(1)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def get_frame(self):
        """
        カメラから1フレーム取得し、以下の2つを返す:
        1. raw_frame: 合成用の生データ
        2. display_frame: 画面表示用のターゲットマーク付きデータ
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        # 合成用には加工前の画像を使う
        raw_frame = frame

        # 表示用にはターゲットマークを描画する（コピーを作成）
        display_frame = np.copy(frame)
        rows, cols, _ = display_frame.shape
        center = (int(cols / 2), int(rows / 2))
        
        # 赤いターゲットマーク描画
        cv2.circle(display_frame, center, 30, (0, 0, 255), 3)
        cv2.circle(display_frame, center, 60, (0, 0, 255), 3)
        cv2.line(display_frame, (center[0], center[1] - 80), (center[0], center[1] + 80), (0, 0, 255), 3)
        cv2.line(display_frame, (center[0] - 80, center[1]), (center[0] + 80, center[1]), (0, 0, 255), 3)

        # 左右反転（鏡のように表示するため）
        display_frame = cv2.flip(display_frame, 1)
        
        # ※合成用(raw_frame)も左右反転させておくと、見たままの向きで合成されます
        raw_frame = cv2.flip(raw_frame, 1)

        return raw_frame, display_frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()

# =================================================================
# 3. メインウィンドウ (GUI)
# =================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K24025 画像合成アプリ (GUI)")
        self.resize(1000, 600)

        # カメラ管理クラスのインスタンス化
        self.camera = CameraManager()
        
        # データ保持用
        self.captured_frame = None  # 撮影した静止画データ

        # GUI構築
        self.init_ui()

        # タイマー設定 (約30fps = 33msごとに画面更新)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_view)
        self.timer.start(33)

    def init_ui(self):
        """画面レイアウトの作成"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)

        # --- 左側：カメラエリア ---
        left_layout = QVBoxLayout()
        
        title_cam = QLabel("1. カメラ映像")
        title_cam.setFont(self.get_bold_font())
        
        self.lbl_camera_display = QLabel("カメラ起動中...")
        self.lbl_camera_display.setFixedSize(640, 480)
        self.lbl_camera_display.setFrameShape(QFrame.Box)
        self.lbl_camera_display.setAlignment(Qt.AlignCenter)
        self.lbl_camera_display.setStyleSheet("background-color: #222; color: #fff;")

        self.btn_capture = QPushButton("撮影 (Capture)")
        self.btn_capture.setMinimumHeight(50)
        self.btn_capture.clicked.connect(self.on_capture_clicked)

        left_layout.addWidget(title_cam)
        left_layout.addWidget(self.lbl_camera_display)
        left_layout.addWidget(self.btn_capture)

        # --- 右側：結果エリア ---
        right_layout = QVBoxLayout()

        title_res = QLabel("2. 合成結果")
        title_res.setFont(self.get_bold_font())

        self.lbl_result_display = QLabel("ここに結果が表示されます")
        self.lbl_result_display.setFixedSize(640, 480)
        self.lbl_result_display.setFrameShape(QFrame.Box)
        self.lbl_result_display.setAlignment(Qt.AlignCenter)
        self.lbl_result_display.setStyleSheet("background-color: #eee; color: #555;")

        self.btn_process = QPushButton("合成実行 (Process)")
        self.btn_process.setMinimumHeight(50)
        self.btn_process.setEnabled(False)
        self.btn_process.clicked.connect(self.on_process_clicked)

        right_layout.addWidget(title_res)
        right_layout.addWidget(self.lbl_result_display)
        right_layout.addWidget(self.btn_process)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("アプリ起動完了")

    def get_bold_font(self):
        font = self.font()
        font.setBold(True)
        font.setPointSize(12)
        return font

    def update_camera_view(self):
        """タイマーによって定期的に呼ばれ、カメラ映像を更新する"""
        # 生データと表示用データを取得
        raw, display = self.camera.get_frame()
        
        if display is not None:
            # 最新のフレームを一時保存（撮影ボタンが押されたとき用）
            self.current_raw_frame = raw
            
            # GUI表示用に変換
            qt_img = self.convert_cv_to_qt(display)
            self.lbl_camera_display.setPixmap(qt_img)

    def on_capture_clicked(self):
        """撮影ボタン押下時：現在のフレームを保存"""
        if hasattr(self, 'current_raw_frame') and self.current_raw_frame is not None:
            self.captured_frame = self.current_raw_frame
            
            self.status_bar.showMessage("キャプチャしました。合成ボタンを押してください。")
            self.btn_process.setEnabled(True)
            
            # 右側の画面に、キャプチャした画像をプレビュー表示
            preview_img = self.convert_cv_to_qt(self.captured_frame)
            self.lbl_result_display.setPixmap(preview_img)
        else:
            QMessageBox.warning(self, "エラー", "カメラ映像が取得できていません。")

    def on_process_clicked(self):
        """合成実行ボタン押下時"""
        if self.captured_frame is None:
            return

        self.status_bar.showMessage("処理中...")
        # GUIを固まらせないために本来は別スレッド推奨だが、今回は簡易的に処理
        QApplication.processEvents() 
        
        try:
            # 画像合成処理 (images/google.png が必要)
            result_img = ImageProcessor.synthesize("images/google.png", self.captured_frame)
            
            # 結果表示
            qt_result = self.convert_cv_to_qt(result_img)
            self.lbl_result_display.setPixmap(qt_result)
            
            # 保存
            save_path = 'output_images/k24025_result.png'
            # フォルダがない場合のエラー回避（任意）
            import os
            os.makedirs('output_images', exist_ok=True)
            
            cv2.imwrite(save_path, result_img)
            
            self.status_bar.showMessage(f"保存完了: {save_path}")
            QMessageBox.information(self, "完了", f"合成が完了し保存しました！\n{save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "処理エラー", f"エラーが発生しました:\n{e}")
            self.status_bar.showMessage("エラー発生")

    def convert_cv_to_qt(self, cv_img):
        """OpenCV画像(BGR)をPySide画像(QPixmap)に変換"""
        if cv_img is None: return QPixmap()
        
        # BGR -> RGB 変換
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        # QImage作成
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # 表示ラベルのサイズに合わせて縮小（アスペクト比保持）
        p = QPixmap.fromImage(qimg).scaled(640, 480, Qt.KeepAspectRatio)
        return p

    def closeEvent(self, event):
        """ウィンドウを閉じるときの処理"""
        self.timer.stop()
        self.camera.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())