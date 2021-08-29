import cv2
import matplotlib.pyplot as plt
import numpy as np

# ハガキ画像から郵便番号領域を抽出する関数
def detect_zipno(fname):
    # 画像を読み込む
    img = cv2.imread(fname)
    # plt.imshow(img)
    # plt.show()
    # 画像のサイズを求める
    h, w = img.shape[:2]
    # ハガキ画像の右上のみ抽出する --- (*1)
    # img = img[0:h//2, :]
    
    # 画像を二値化 --- (*2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # plt.imshow(gray)
    # plt.show()
    gray = cv2.GaussianBlur(gray, (3, 3), 1)
    # plt.imshow(gray)
    # plt.show()
    im2 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
    # plt.imshow(im2)
    # plt.show()

    # 輪郭を抽出 --- (*3)
    cnts = cv2.findContours(im2, 
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE)[0]
    
    # 抽出した輪郭を単純なリストに変換--- (*4)
    result = []
    for pt in cnts:
        x, y, w, h = cv2.boundingRect(pt)
        # if w > h :
        #     y -= (w - h)//2
        #     h = w
        # else:
        #     x -= (h - w) // 2
        #     w = h

        # x -= w//4
        # y -= h//4
        # w = int(w*1.25)
        # h = int(h*1.25)
        # 大きすぎる小さすぎる領域を除去 --- (*5)
        if not((10 < w < 200) or (10 < h < 200)): continue
        result.append([x, y, w, h])
    # 抽出した輪郭が左側から並ぶようソート --- (*6)
    result = sorted(result, key=lambda x: x[0])

    for x, y, w, h in result:
        cv2.rectangle(im2, (x, y), (x+w, y+h), (255, 255, 255), 3)

    plt.imshow(im2)
    plt.show()

    pn = len(result)
    s = np.zeros(pn)
    i = 0
    result2 = []
    flag = True
    dx = 20
    dy = 30
    for i in range(pn):
        # if i > pn - 1:
        #     break

        if s[i]==0 :

            [x1, y1, w1, h1] = result[i]
            x = x1
            y = y1
            xw = x1 + w1
            yh = y1 + h1
            for j in range(i+1,pn):
                if s[j]==0 :
                    [x2, y2, w2, h2] = result[j]
                    xx = x2 - x1
                    yy = y2 - y1
                    if -(w2+dx) < xx and xx < (w1+dx) and -(h2+dy) < yy and yy < (h1+dy):
                    # if ((x2 < x1+w1 < x2+w2) and (y2 < y1+h1 < y2+h2)) or ((x2 < x1+w1 < x2+w2) and (y2 < y1 < y2+h2)):
                        s[j]=1
                        if x2 < x : x = x2
                        if (x2 + w2) > xw : xw = x2 + w2
                        if y2 < y : y = y2
                        if (y2 + h2) > yh: yh = y2 + h2

            result2.append([x, y, xw - x, yh - y])

    print(len(result2))
    # x = b[:x] - a[:x]
    # y = b[:y] - a[:y]
    # if -b[:w] < x & & x < a[:w] & &
    #     -b[:h] < y & & y < a[:h]
    # 抽出した輪郭が近すぎるものを除去 --- (*7)
    # result2 = []
    # lastx = -100
    # for x, y, w, h in result1:
        # if (x - lastx) < 10: continue


        # result2.append([x, y, w, h])
        # lastx = x
    # 緑色の枠を描画 --- (*8)
    plt.imshow(img)
    plt.show()
    img3 = []
    for x, y, w, h in result2:
        img3.append(img[y:y+h, x:x+w])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

    return result2, img, img3

if __name__ == '__main__':
    # ハガキ画像を指定して領域を抽出
    cnts, img, img3 = detect_zipno("手書き数字1.jpg")
    # cnts, img, img3= detect_zipno("手書き数字＆かなカナ.tif")
    # cnts, img, img3 = detect_zipno("理事会議事録カラー.jpg")
    # cnts, img, img3 = detect_zipno("第2回理事会議事録グレー.jpg")
    # cnts, img, img3 = detect_zipno("理事会議事録白黒.tif")

    # 画面に抽出結果を描画
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # plt.savefig("detect-zip.png", dpi=200)
    plt.show()

    for i in range(len(img3)):
        plt.subplot(5,6,i+1)
        plt.imshow(cv2.cvtColor(img3[i], cv2.COLOR_BGR2RGB))
        plt.axis('off')
    plt.show()