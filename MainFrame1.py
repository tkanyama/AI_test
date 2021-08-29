# -*- coding: utf-8 -*-
'''

プログラム名：calc_main.py

風洞実験結果から応答解析を行い、報告書用の図表を作成するプログラム

バージョン：1.0

python 3.7.1

作成：2019/9 完山

'''

# ライブラリーの読み込み
import os
import wx
import wx.lib.scrolledpanel as scrolled
import platform


FRAME_WIDTH = 1800                          # メインパネルの幅
FRAME_HEIGHT = 1003                         # メインパネルの高さ
CONTROL_PANEL_WIDTH = 400                   # 左側のコントロールパネルの幅
BUTTON_WIDTH = CONTROL_PANEL_WIDTH//2-2     # 計算用ボタンの幅


class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):

        # OSの種類の読み込み（'Windows' or 'Darwin' or 'Linux'）
        self.osname = platform.system()
        self.home = os.path.expanduser('~')
        self.data_dir = self.home + "/PDF_DATA"
        self.user_dic = self.home + "/dic/gbrc_dic.csv"
        # ウインドウのバーの高さの設定（osによって異なるため）
        if self.osname == 'Windows':
            bar_h = 60
            self.bar_w = 18
            # 1.インストール済みのTesseractのパスを通す
            path_tesseract = "C:\\Program Files\\Tesseract-OCR"
            if path_tesseract not in os.environ["PATH"].split(os.pathsep):
                os.environ["PATH"] += os.pathsep + path_tesseract
            self.SCROLL_PAGE_HEIGHT = 68

        elif self.osname == 'Darwin':  # Mac OS
            bar_h = 22
            self.bar_w = 15
            self.SCROLL_PAGE_HEIGHT = 70
            from os.path import expanduser
        elif self.osname == 'Linux':
            bar_h = 22
            self.bar_w = 15
            self.SCROLL_PAGE_HEIGHT = 70
            from os.path import expanduser
        wx.Frame.__init__ (self, *args, **kwargs)   # メインパネルの作成
        self.Center()   # ウィンドウをモニターのセンターに表示
        (self.frame_w, self.frame_h) = self.GetSize()   # ウィンドウのサイズの読み込み


if __name__ == '__main__':
    app = wx.App()
    fx = FRAME_WIDTH
    fy = FRAME_HEIGHT
    s1 = wx.Size(fx,fy)
    frame = MainFrame(None, wx.ID_ANY, u'PDF読込プログラム', size=s1 )
    # frame.set_panel()

    frame.Show()
    app.MainLoop()