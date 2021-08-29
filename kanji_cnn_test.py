import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
# import plaidml.keras
# plaidml.keras.install_backend()
import keras
from keras.models import load_model
from scipy import signal
from jiscode import jiscode
import pickle
from jFont import *


def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

# ハガキ画像から郵便番号領域を抽出する関数
def detect_zipno(fname):
    # 画像を読み込む
    img = imread(fname)
    img_copy = img
    # plt.imshow(img)
    # plt.show()
    # 画像のサイズを求める
    h0, w0 = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    ysum = np.zeros(h0)
    for i in range(h0):
        ysum[i] = np.sum(inv[i,:])

    num = 50  # 移動平均の個数
    b = np.ones(num) / num
    ysum = np.convolve(ysum, b, mode='same')  # 移動平均
    ysum = ysum / np.max(ysum) * w0 / 2
    plt.imshow(img)
    plt.plot(ysum, np.arange(h0))

    # ピーク値のインデックスを取得
    maxid = signal.argrelmax(ysum, order=num)[0]  # 最大値
    minid = signal.argrelmin(ysum, order=num)[0]  # 最小値

    if len(maxid)>0:
        x1 = []
        y1 = []
        for id in maxid:
            x1.append(ysum[id])
            y1.append(id)
        plt.plot(x1,y1, marker='o', linestyle='None')

        if len(minid)>0:
            x2 = []
            y2 = []
            for id in minid:
                x2.append(ysum[id])
                y2.append(id)
            plt.plot(x2,y2, marker='o', linestyle='None')
        else:
            pass

        lh1=[]
        lh2=[]
        hh = 0
        n = len(maxid)
        for i in range(n - 1):
            lh1.append(hh)
            y = (maxid[i] + maxid[i+1])//2
            plt.plot([0,w0],[y,y])
            lh2.append(y)
            hh = y + 1
        lh1.append(hh)
        lh2.append(h0)

        esy = int(0.01 * np.max(ysum))
        for i in range(len(ysum)):
            if ysum[i]>esy:
                lh1[0] = i - 5
                break

        for i in range(maxid[n-1],len(ysum)):
            if ysum[i] < esy:
                lh2[n-1] = i + 5
                break


    plt.show()

    img2 = []
    img4 = []
    hh2 = []
    for i in range(n):
        img1 = img[lh1[i]:lh2[i],:]
        hh2.append(lh2[i] - lh1[i] + 1)

        inv = cv2.bitwise_not(img1)
        xsum = np.zeros(w0)
        for j in range(w0):
            xsum[j] = np.sum(inv[:, j])

        num = 25  # 移動平均の個数
        b = np.ones(num) / num
        xsum = np.convolve(xsum, b, mode='same')  # 移動平均
        xsum = xsum / np.max(xsum) * hh2[i]
        plt.imshow(img1)
        plt.plot(np.arange(w0),xsum )
        plt.show()

        # s1=0
        # s=[]
        # m=5
        # for j in range(len(xsum)-5):
        #     s.append(((xsum[j+m]-xsum[j])/m))
        # s = s / np.max(s) * hh2[i]
        # plt.plot(np.arange(w-5), s)
        # # ピーク値のインデックスを取得
        # xmaxid = signal.argrelmax(xsum, order=40)[0]  # 最大値
        # xminid = signal.argrelmin(xsum, order=40)[0]  # 最小値

        es = int(0.01 * np.max(xsum))

        j = 0
        p = xsum[0]
        s_pos = []
        e_pos = []
        while(True):
            while(True):
                j += 1
                if j>= w0:break
                if xsum[j] > es:
                    s_pos.append(j-10)
                    break

            while(True):
                j += 1
                if j >= w0: break
                if xsum[j]< es:
                    e_pos.append(j+9)
                    j += 4
                    break

            if j >= w0: break

        if len(s_pos)>0:
            for s in s_pos:
                plt.plot([s,s],[0,hh2[i]])

        if len(e_pos)>0:
            for s in e_pos:
                plt.plot([s,s],[0,hh2[i]])

        # x2 = []
        # y2 = []
        # for id in xmaxid:
        #     x2.append(id)
        #     y2.append(xsum[id])
        # plt.plot(x2,y2, marker='o', linestyle='None')


        img2.append(img1)
        # plt.subplot(n,1,i+1)
        # plt.imshow(img1)

        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
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
            # 大きすぎる小さすぎる領域を除去 --- (*5)
            if not ((5 < w < 200) and (5 < h < 200)): continue
            result.append([x, y, w, h])
        # 抽出した輪郭が左側から並ぶようソート --- (*6)
        result = sorted(result, key=lambda x: x[0])

        for x, y, w, h in result:
            cv2.rectangle(im2, (x, y), (x + w, y + h), (255, 255, 255), 3)
        plt.imshow(im2)
        plt.show()


        sn = min(len(s_pos), len(e_pos))
        pn = len(result)
        result2 = []
        for j in range(sn):
            x1 = s_pos[j]
            w1 = e_pos[j] - s_pos[j]
            x = 0
            y = 0
            for k in range(pn):
                [x2, y2, w2, h2] = result[k]
                xx = x2 - x1
                if -w2  < xx and xx < w1 :
                    if x == 0:
                        x = x2
                        xw = x2 + w2
                        y = y2
                        yh = y2 + h2
                    else:
                        if x2 < x: x = x2
                        if (x2 + w2) > xw: xw = x2 + w2
                        if y2 < y: y = y2
                        if (y2 + h2) > yh: yh = y2 + h2
            if x > 0:
                result2.append([x, y, xw - x, yh - y])

        img3 = []
        for x, y, w, h in result2:
            im = img[y+lh1[i]:y+lh1[i] + h, x:x + w]
            L = int(max(h, w) * 1.1)
            X = np.zeros((L, L, 3)) + 255
            X = X.astype(np.uint8)
            dx = (L - w) // 2
            dy = (L - h) // 2
            X[dy:dy + h, dx:dx + w] = im
            img3.append(X)
            cv2.rectangle(img, (x, y+lh1[i]), (x + w, y+lh1[i] + h), (0, 255, 0), 3)

        plt.imshow(img)
        plt.show()

        img4.append(img3)

        # result = sorted(result, key=lambda x: x[0])

        # for x, y, w, h in result:
        #     cv2.rectangle(im2, (x, y), (x + w, y + h), (255, 255, 255), 3)

        # plt.imshow(im2)
        # plt.show()

        # pn = len(result)
        # s = np.zeros(pn)
        # i = 0
        # result2 = []
        # flag = True
        # dx = 20
        # dy = 30
        # for i in range(pn):
        #     # if i > pn - 1:
        #     #     break
        #
        #     if s[i] == 0:
        #
        #         [x1, y1, w1, h1] = result[i]
        #         x = x1
        #         y = y1
        #         xw = x1 + w1
        #         yh = y1 + h1
        #         for j in range(i + 1, pn):
        #             if s[j] == 0:
        #                 [x2, y2, w2, h2] = result[j]
        #                 xx = x2 - x1
        #                 yy = y2 - y1
        #                 if -(w2 + dx) < xx and xx < (w1 + dx) and -(h2 + dy) < yy and yy < (h1 + dy):
        #                     # if ((x2 < x1+w1 < x2+w2) and (y2 < y1+h1 < y2+h2)) or ((x2 < x1+w1 < x2+w2) and (y2 < y1 < y2+h2)):
        #                     s[j] = 1
        #                     if x2 < x: x = x2
        #                     if (x2 + w2) > xw: xw = x2 + w2
        #                     if y2 < y: y = y2
        #                     if (y2 + h2) > yh: yh = y2 + h2
        #
        #         result2.append([x, y, xw - x, yh - y])
        #
        #         img3 = []
        #         for x, y, w, h in result2:
        #             im = img[y:y + h, x:x + w]
        #             L = int(max(h, w) * 1.4)
        #             X = np.zeros((L, L, 3)) + 255
        #             X = X.astype(np.uint8)
        #             dx = (L - w) // 2
        #             dy = (L - h) // 2
        #             X[dy:dy + h, dx:dx + w] = im
        #             img3.append(X)
        #             cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        #
        #         img4.append(img3)
        #
        # img4.append([])
    # plt.show()
    # ハガキ画像の右上のみ抽出する --- (*1)
    # img = img[0:h//2, :]

    # # 画像を二値化 --- (*2)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # # plt.imshow(gray)
    # # plt.show()
    # gray = cv2.GaussianBlur(gray, (3, 3), 1)
    # # plt.imshow(gray)
    # # plt.show()
    # im2 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
    # # plt.imshow(im2)
    # # plt.show()
    #
    # # 輪郭を抽出 --- (*3)
    # cnts = cv2.findContours(im2,
    #                         cv2.RETR_LIST,
    #                         cv2.CHAIN_APPROX_SIMPLE)[0]
    #
    # # 抽出した輪郭を単純なリストに変換--- (*4)
    # result = []
    # for pt in cnts:
    #     x, y, w, h = cv2.boundingRect(pt)
    #     # if w > h :
    #     #     y -= (w - h)//2
    #     #     h = w
    #     # else:
    #     #     x -= (h - w) // 2
    #     #     w = h
    #
    #     # x -= w//4
    #     # y -= h//4
    #     # w = int(w*1.25)
    #     # h = int(h*1.25)
    #     # 大きすぎる小さすぎる領域を除去 --- (*5)
    #     if not ((10 < w < 200) or (10 < h < 200)): continue
    #     result.append([x, y, w, h])
    # # 抽出した輪郭が左側から並ぶようソート --- (*6)
    # result = sorted(result, key=lambda x: x[0])
    #
    # for x, y, w, h in result:
    #     cv2.rectangle(im2, (x, y), (x + w, y + h), (255, 255, 255), 3)
    #
    # # plt.imshow(im2)
    # # plt.show()
    #
    # pn = len(result)
    # s = np.zeros(pn)
    # i = 0
    # result2 = []
    # flag = True
    # dx = 20
    # dy = 30
    # for i in range(pn):
    #     # if i > pn - 1:
    #     #     break
    #
    #     if s[i] == 0:
    #
    #         [x1, y1, w1, h1] = result[i]
    #         x = x1
    #         y = y1
    #         xw = x1 + w1
    #         yh = y1 + h1
    #         for j in range(i + 1, pn):
    #             if s[j] == 0:
    #                 [x2, y2, w2, h2] = result[j]
    #                 xx = x2 - x1
    #                 yy = y2 - y1
    #                 if -(w2 + dx) < xx and xx < (w1 + dx) and -(h2 + dy) < yy and yy < (h1 + dy):
    #                     # if ((x2 < x1+w1 < x2+w2) and (y2 < y1+h1 < y2+h2)) or ((x2 < x1+w1 < x2+w2) and (y2 < y1 < y2+h2)):
    #                     s[j] = 1
    #                     if x2 < x: x = x2
    #                     if (x2 + w2) > xw: xw = x2 + w2
    #                     if y2 < y: y = y2
    #                     if (y2 + h2) > yh: yh = y2 + h2
    #
    #         result2.append([x, y, xw - x, yh - y])
    #
    # print(len(result2))
    # # x = b[:x] - a[:x]
    # # y = b[:y] - a[:y]
    # # if -b[:w] < x & & x < a[:w] & &
    # #     -b[:h] < y & & y < a[:h]
    # # 抽出した輪郭が近すぎるものを除去 --- (*7)
    # # result2 = []
    # # lastx = -100
    # # for x, y, w, h in result1:
    # # if (x - lastx) < 10: continue
    #
    # # result2.append([x, y, w, h])
    # # lastx = x
    # # 緑色の枠を描画 --- (*8)
    # # plt.imshow(img)
    # # plt.show()
    # img3 = []
    # for x, y, w, h in result2:
    #     im = img[y:y + h, x:x + w]
    #     L = int(max(h, w) * 1.4)
    #     X = np.zeros((L ,L, 3)) + 255
    #     X = X.astype(np.uint8)
    #     dx = (L - w)//2
    #     dy = (L - h)//2
    #     X[dy:dy+h, dx:dx+w] = im
    #     img3.append(X)
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

    return result2, img_copy, img4


if __name__ == '__main__':
    # ハガキ画像を指定して領域を抽出
    # cnts, img, img3 = detect_zipno("手書き数字1.jpg")
    # cnts, img, img3= detect_zipno("手書き数字＆かなカナ.tif")
    cnts, img, img3 = detect_zipno("手書きサンプル005.tif")
    # cnts, img, img3 = detect_zipno("理事会議事録カラー.jpg")
    # cnts, img, img3 = detect_zipno("第2回理事会議事録グレー.jpg")
    # cnts, img, img3 = detect_zipno("理事会議事録白黒.tif")


    jis_code_file = 'ETL9B_KANA_JIS_CODE.picle'
    (code_mat) = pickle.load(open(jis_code_file, "rb"))
    # 画面に抽出結果を描画
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # plt.savefig("detect-zip.png", dpi=200)
    # plt.show()

    img4 = []
    k=0
    gn = sum([len(v) for v in img3])
    for i in range(len(img3)):
        im1 = img3[i]
        for j in range(len(im1)):
            im2 = np.array(im1[j])
            gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 1)
            im2 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
            img4.append(im2)
            k += 1
            if k<= 35:
                plt.subplot(7, 5, k)
                plt.imshow(cv2.cvtColor(im2, cv2.COLOR_BGR2RGB))
        # plt.axis('off')
    plt.show()

    im_rows = 32  # 画像の縦ピクセルサイズ
    im_cols = 32  # 画像の横ピクセルサイズ
    im_color = 1  # 画像の色空間/グレイスケール
    in_shape = (im_rows, im_cols, im_color)
    out_size = 10

    # X_test = img4.reshape(-1, im_rows, im_cols, im_color)
    im3 = []
    for im in img4:
        im2 = cv2.resize(im,(im_rows, im_cols))
        im3.append(im2)

    im3 = np.array(im3)
    X_test = im3.reshape(-1, im_rows, im_cols, im_color)
    X_test = X_test.astype('float32') / 255


    model=load_model('etl9b_model15-1_32_2048_100_02.h5')
    # model.load_weights('etl9b_25_weight04.h5')

    y1 = model.predict(X_test, verbose=1)
    jis1 = jiscode()
    ch = []
    code = []
    for y in y1:
        # print('max={} , index={}'.format(np.max(y), np.argmax(y)))
        s1 = np.argsort(y)[::-1]
        for i in range(10):
            cn = code_mat[s1[i]]
            c1 = chr(jis1.jis2uni(cn))
            y1 = y[s1[i]]
            print('{0:}({1:.3f}),'.format(c1, y1), end='')
            # print(chr(jis.jis2uni(code_mat[s1[i]]))+' ', end='')
        print()
        # ch.append(chr(48 + np.argmax(y)))
        c = code_mat[np.argmax(y)]
        code.append(c)
        c2 = jis1.jis2uni(c)
        ch.append(chr(c2))

    k = 0
    moji = ''
    fp1 = mincho_font_set(6,1.0)
    for i in range(len(img3)):
        im1 = img3[i]
        for j in range(len(im1)):
            im2 = np.array(im1[j])

            if k<=34:
                plt.subplot(7, 5, k + 1)
                # plt.imshow(im1)
                plt.imshow(cv2.cvtColor(im2, cv2.COLOR_BGR2RGB))
                plt.axis('off')
                plt.title('char={}'.format(ch[k]), FontProperties=fp1)
                moji += ch[k]
                k += 1

        if i < len(im3-1):
            moji += '\n'

    print(moji)
    plt.show()