import numpy as np
import cv2
# 学籍番号はK24025として進めます




def lecture05_01(capture_img: cv2.Mat) -> cv2.Mat | None:
    """
    画像合成担当（K24025）

    - images/google.png を読み込む
    - google画像の白色(255,255,255)ピクセルを、capture_img の画素で置き換える
    - 合成結果を画面表示し、output_images/k24025_google.png に保存する

    Args:
        capture_img (cv2.Mat): カメラから撮影した画像（GUI側で取得したもの）

    Returns:
        cv2.Mat | None: 合成後の画像（失敗時は None）
    """

    # 0. 前提チェック
    if capture_img is None:
        print("エラー: カメラ画像(capture_img)が None です。")
        return None
    # 1. google画像の読み込み
    google_img: cv2.Mat = cv2.imread('images/google.png')
    if google_img is None:
        print("エラー: 'images/google.png' が読み込めませんでした。")
        return None

    # 2. 画像サイズの取得
    g_hight, g_width, g_channel = google_img.shape
    c_hight, c_width, c_channel = capture_img.shape
    print("google画像のサイズ:", google_img.shape)
    print("カメラ画像のサイズ:", capture_img.shape)

    # 3. 白色置換アルゴリズム
    #    google_img の各画素を走査し、白色(255,255,255)なら capture_img の画素で置換
    for x in range(g_width):
        for y in range(g_hight):
            # BGRの順で取得
            b, g, r = google_img[y, x]

            # もし白色(255,255,255)だったら置き換える
            if (b, g, r) == (255, 255, 255):
                # capture_img の範囲に合わせて座標を決める（はみ出し防止のため剰余を使用）
                cap_x = x % c_width
                cap_y = y % c_hight

                # google_img の白色ピクセルを capture_img の対応するピクセルで置き換える
                google_img[y, x] = capture_img[cap_y, cap_x]

    # 4. 合成結果の保存
    output_filepath = 'output_images/k24025_google.png'
    cv2.imwrite(output_filepath, google_img)
    print(f"加工済み画像を {output_filepath} に保存しました。")

    # 5. 合成結果の表示
    cv2.imshow("K24025 合成結果", google_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    ## 6. 呼び出し側で再利用できるように、合成画像も返す
    return google_img
