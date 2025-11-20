import numpy as np
import cv2
# 学籍番号はK24025として進めます
from my_module.K24025.lecture05_camera_image_capture import MyVideoCapture

def lecture05_01():

    # カメラキャプチャ実行
    app = MyVideoCapture()
    app.run()

    # 画像をローカル変数に保存
    google_img : cv2.Mat = cv2.imread('images/google.png')
    # 動作テスト用なので提出時にこの行を消すこと
    # capture_img : cv2.Mat = cv2.imread('images/camera_capture.png')
    
    # 1. カメラキャプチャ画像の取得
    capture_img : cv2.Mat = app.get_img()
    # もし画像がNoneで返ってきた場合は、処理を中断する（実装上の安全策）
    if capture_img is None:
        print("カメラ画像がキャプチャされませんでした。")
        return

    g_hight, g_width, g_channel = google_img.shape
    c_hight, c_width, c_channel = capture_img.shape
    print(google_img.shape)
    print(capture_img.shape)

    for x in range(g_width):
        for y in range(g_hight):
            # BGRの順で取得
            b, g, r = google_img[y, x]
            
            # もし白色(255,255,255)だったら置き換える
            if (b, g, r) == (255, 255, 255):
                # 2. 白色ピクセルの置換
                # google_imgの(x, y)の座標に対応するcapture_imgのピクセル座標を計算
                # 拡大縮小せず、キャプチャ画像をグリッド状に並べるため、
                # capture_imgのサイズで割った剰余を使用する
                cap_x = x % c_width
                cap_y = y % c_hight
                
                # google_imgの白色ピクセルをcapture_imgの対応するピクセルで置き換える
                google_img[y, x] = capture_img[cap_y, cap_x]

    # 3. 画像保存
    output_filepath = 'output_images/k24025_google.png'
    cv2.imwrite(output_filepath, google_img)
    print(f"加工済み画像を {output_filepath} に保存しました。")


    # カメラキャプチャプログラムのファイルに保存する機能を使わないため、
    # app.write_imgはコメントアウトまたは削除
    # app.write_img
