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
from PyPDF2 import PdfFileWriter, PdfFileReader
import shutil
from pdf2image import convert_from_path, convert_from_bytes
import pyocr
import pyocr.builders
from PIL import Image
import sys
# import MeCab
import re
from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome import tokenfilter, charfilter

import time
import pandas as pd
import platform
# import matplotlib
# matplotlib.interactive( True )
# matplotlib.use( 'WXAgg' )
# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_pdf import FigureCanvasPdf # PDFを作成するモジュールの読込
# from matplotlib.backends.backend_pdf import PdfPages  # PDFを作成するモジュールの読込
import numpy as np  # 数値計算用ライブラリー
# import pickle       # オブジェクトの保存・詠み込み用ライブラリー

# 当室で作成したライブラリーの読み込み
# import Calc1     # 風向別頻度計算用ライブラリー
# import Calc2     # 風工式ランク評価計算用ライブラリー
# import calc_responce as cr  # 応答計算用ライブラリー
# from make_graph import *    # 作図、作表用ライブラリー

# メニューIDの設定
ID_READ_PARA = 101                          # 層風力計算
# ID_CALC_RESPONSE =102                     # 応答解析
ID_EXIT = 105                               # 終了
ID_COPY = 201                               # コピー
ID_PASTE =202                               # 貼り付け

FRAME_WIDTH = 1800                          # メインパネルの幅
FRAME_HEIGHT = 1003                         # メインパネルの高さ
CONTROL_PANEL_WIDTH = 400                   # 左側のコントロールパネルの幅
BUTTON_WIDTH = CONTROL_PANEL_WIDTH//2-2     # 計算用ボタンの幅
BUTTON_HEIGHT = 40                          # 計算用ボタンの高さ
BUTTON_WIDTH1 = 150                         # 作図用ボタンの幅
BUTTON_HEIGHT1 = 40                         # 作図用ボタンの高さ
BUTTON_WIDTH0 = 60                          # 作図用ボタンの幅
BUTTON_HEIGHT0 = 24                         # 作図用ボタンの高さ
BUTTON_GAP = 1.0                            # ボタン間のギャップ
TEXT_WIDTH1 = CONTROL_PANEL_WIDTH-5         # テキストコントロール１の幅
TEXT_HEIGHT1 = 750                          # テキストコントロール１の高さ
TEXT_WIDTH2 = CONTROL_PANEL_WIDTH-5         # テキストコントロール２の幅
TEXT_HEIGHT2 = 440                          # テキストコントロール２の高さ
TEXT_WIDTH3 = CONTROL_PANEL_WIDTH-5         # テキストコントロール２の幅
TEXT_HEIGHT3 = 440                          # テキストコントロール２の高さ

TEXT_PANEL_WIDTH = 400

BUTTON_WIDTH2 = 33                          # 矢印用ボタンの幅
BUTTON_HEIGHT2 = 33                         # 矢印用ボタンの高さ

# SCROLL_PAGE_HEIGHT = 68                     # 1ページあたりのスクロール行数
SCROLL_PAGE_HEIGHT = 71                     # 1ページあたりのスクロール行数

# USER_DIC = "C:\\dic\\gbrc_dic.csv"

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
            # self.frame_hd = 3
            from os.path import expanduser
            # self.home = expanduser("~") + "\\Desktop\\PDF_DATA"
            # self.user_dic = "C:\\dic\\gbrc_dic.csv"
        elif self.osname == 'Darwin':  # Mac OS
            bar_h = 22
            self.bar_w = 15
            self.SCROLL_PAGE_HEIGHT = 70
            # self.frame_hd = 0
            from os.path import expanduser
            # self.data_dir = self.home + "/PDF_DATA"
            # self.user_dic = self.home + "/dic/gbrc_dic.csv"
        elif self.osname == 'Linux':
            bar_h = 22
            self.bar_w = 15
            self.SCROLL_PAGE_HEIGHT = 70
            # self.frame_hd = 0
            from os.path import expanduser
            # self.home = expanduser("~") + "/PDF_DATA"
            # self.user_dic = "~/dic/gbrc_dic.csv"
        wx.Frame.__init__ (self, *args, **kwargs)   # メインパネルの作成
        self.Center()   # ウィンドウをモニターのセンターに表示
        (self.frame_w, self.frame_h) = self.GetSize()   # ウィンドウのサイズの読み込み
        # 左側のコントロールパネルの位置とサイズと色の設定
        self.ctr_panel = wx.Panel(self, wx.ID_ANY, pos=(0, 0), size=(CONTROL_PANEL_WIDTH, self.frame_h - bar_h))
        self.ctr_panel.SetBackgroundColour(wx.LIGHT_GREY)
        (self.c_w, self.c_h) = self.ctr_panel.GetSize()

        # 右側のグラフパネルの位置とサイズと色の設定
        # self.g_panel = wx.Panel(self, wx.ID_ANY, pos=(CONTROL_PANEL_WIDTH, 0),
        #                         size=(FRAME_WIDTH - CONTROL_PANEL_WIDTH, self.frame_h - bar_h))
        self.g_panel = wx.Panel(self, wx.ID_ANY, pos=(CONTROL_PANEL_WIDTH, 0),
                                size=(self.frame_h - bar_h + self.bar_w, self.frame_h - bar_h))
        self.g_panel.SetBackgroundColour(wx.Colour(red=150, green=150, blue=150))

        # グラフ用紙をグラフパネルに貼り付け
        (self.g_w, self.g_h) = self.g_panel.GetSize()
        # self.gx = int(self.g_h / np.sqrt(2.0))  # 幅は高さの√2分の１
        self.gx = int(self.g_h )
        self.gy = self.g_h
        # x1 = (self.g_w - self.gx)//2
        x1 = 0
        self.graph_panel1 =scrolled.ScrolledPanel(self.g_panel, wx.ID_ANY, pos=(x1, 0), size=(self.gx+self.bar_w, self.gy))
        self.graph_panel1.SetupScrolling()
        self.graph_panel1.SetBackgroundColour(wx.Colour(red=220, green=220, blue=220))

        self.text_panel = wx.Panel(self, wx.ID_ANY, pos=(CONTROL_PANEL_WIDTH+self.frame_h - bar_h + self.bar_w, 0),
                                   size=(FRAME_WIDTH-self.c_w-self.g_w, self.frame_h - bar_h))
        self.text_panel.SetBackgroundColour(wx.LIGHT_GREY)
        (self.t_w, self.t_h) = self.text_panel.GetSize()
        # self.graph_panel1.OnChildFocus(evt=wx.EVT_CHILD_FOCUS)
        # self.graph_panel1.Bind(wx.EVT_SCROLLWIN, self.OnChildFocus)
        # self.graph_panel1.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
        # self.graph_panel1 = wx.Panel(self.g_panel, wx.ID_ANY, pos=(x1, 0),
        #                                            size=(self.gx + self.bar_w, self.gy))
        # self.graph_panel1.SetBackgroundColour(wx.Colour(red=220, green=220, blue=220))
        # ボタンの作成
        bdx = BUTTON_GAP; bdy = BUTTON_GAP      # ボタン間隔の設定
        bw = BUTTON_WIDTH; bh = BUTTON_HEIGHT   # ボタンサイズの設定
        bw1 = BUTTON_WIDTH1; bh1 = BUTTON_HEIGHT1   # ボタンサイズの設定
        bw0 = BUTTON_WIDTH0; bh0 = BUTTON_HEIGHT0
        th1 = 25

        # 設定ファイル表示用テキストコントロールの設定
        tw2 = TEXT_WIDTH2
        th2 = TEXT_HEIGHT1
        tx2 = bdx
        ty2 = FRAME_HEIGHT - TEXT_HEIGHT1 - bdy - bar_h
        self.ocr_text = wx.TextCtrl(self.ctr_panel, wx.ID_ANY, pos=(tx2, ty2), size=(tw2, th2), style=wx.TE_LEFT | wx.TE_MULTILINE)
        self.ocr_text.SetValue("")
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.ocr_text.SetFont(font)

        self.ocr_text_label = wx.StaticText(self.ctr_panel, wx.ID_ANY, 'OCRテキストデータ', pos=(bdx , ty2 - 24 * 2))
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.ocr_text_label.SetFont(font)
        self.ocr_text_label.SetForegroundColour('#0000FF')

        t1 = wx.StaticText(self.ctr_panel, wx.ID_ANY, '処理', pos=(bdx + bw * 0.75, bdy))
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        t1.SetFont(font)
        t1.SetForegroundColour('#0000FF')

        self.ocr_text_save_button = wx.Button(self.ctr_panel, wx.ID_ANY, '保存', pos=(tw2 - 100, ty2 - 26), size=(100, 25))
        self.Bind(wx.EVT_BUTTON, self.text_save_button_handler, self.ocr_text_save_button)  # イベントを設定
        # self.text_save_button.Disable()

        ty3 = FRAME_HEIGHT - TEXT_HEIGHT2 - bdy - bar_h
        self.analysis_text_label = wx.StaticText(self.text_panel, wx.ID_ANY, '形態解析テキストデータ', pos=(bdx, bdy))
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.analysis_text_label.SetFont(font)
        self.analysis_text_label.SetForegroundColour('#0000FF')

        b3 = wx.Button(self.text_panel, wx.ID_ANY, '形態解析', pos=(tw2 - 80, bdy), size=(100, 25))
        self.Bind(wx.EVT_BUTTON, self.text_analysis_button_handler, b3)  # イベントを設定

        # 設定ファイル表示用テキストコントロールの設定
        tw3 = TEXT_WIDTH2
        th3 = TEXT_HEIGHT2
        tx3 = bdx
        ty3 = FRAME_HEIGHT - TEXT_HEIGHT2 - bdy - bar_h
        self.analysis_text = wx.TextCtrl(self.text_panel, wx.ID_ANY, pos=(bdx, bdy + 26 ), size=(self.t_w - bdx - self.bar_w, th3),
                                         style=wx.TE_LEFT | wx.TE_MULTILINE)
        self.analysis_text.SetValue("")
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.analysis_text.SetFont(font)

        tx4 = bdx
        ty4 = FRAME_HEIGHT - TEXT_HEIGHT3 - bdy - bar_h
        self.result_text_label = wx.StaticText(self.text_panel, wx.ID_ANY, '認識テキストデータ', pos=(bdx, ty4 - 26))
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.result_text_label.SetFont(font)
        self.result_text_label.SetForegroundColour('#0000FF')

        tw4 = TEXT_WIDTH3
        th4 = TEXT_HEIGHT3
        self.result_save_button = wx.Button(self.text_panel, wx.ID_ANY, '保存', pos=(tw4-80, ty4-26), size=(100, 25))
        self.Bind(wx.EVT_BUTTON, self.text_result_button_handler, self.result_save_button)  # イベントを設定

        # 設定ファイル表示用テキストコントロー    ルの設定
        # tx4 = bdx
        # ty4 = bdy + 26
        self.result_text = wx.TextCtrl(self.text_panel, wx.ID_ANY, pos=(tx4, ty4), size=(self.t_w - bdx - self.bar_w, th4),
                                       style=wx.TE_LEFT | wx.TE_MULTILINE)
        self.result_text.SetValue("")
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.result_text.SetFont(font)


        # t2 = wx.StaticText(self.ctr_panel, wx.ID_ANY, '図表作成', pos=(bdx + bw * 0.75, bdy*4 + (4 // 2) * (bdy + bh) + th1))
        # font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        # t2.SetFont(font)
        # t2.SetForegroundColour('#0000FF')

        menu_calc = wx.Menu()
        menu_graph = wx.Menu()
        menu_pdf = wx.Menu()
        self.check_box = []

        self.pdf_program_name = [
            [[self.pdf_read], '１．PDFファイル読み込み\n（pdfファイル）', '\tCtrl+J'],
            [[self.pdf_write], '２．PDFファイル書き出し\n（pdfファイル）', '\tCtrl+K'],
            [[self.before_page], '前のページ\n←', '\tCtrl+B'],
            [[self.next_page], '次のページ\n→', '\tCtrl+N']
        ]

        bn1 = len(self.pdf_program_name)
        self.calc_dic = {}          # ボタンのラベルと関数名を記録する辞書の初期化
        self.menu_dic = {}

        # ボタンの配置とメニューの配置
        for i in range(bn1):
            if self.pdf_program_name[i][1] != "":
                bx = bdx + (i % 2) * (bdx + bw)
                by = bdy + (i // 2) * (bdy + bh) + th1
                # ボタンを配置
                b1 = wx.Button(self.ctr_panel, wx.ID_ANY, self.pdf_program_name[i][1], pos=(bx, by), size=(bw, bh))
                self.Bind(wx.EVT_BUTTON, self.exec_button_handler, b1)  # イベントを設定
                self.calc_dic[self.pdf_program_name[i][1]] = self.pdf_program_name[i][0]

                s = self.pdf_program_name[i][1].find('\n')
                title = self.pdf_program_name[i][1][0:s] + self.pdf_program_name[i][2]
                menu_no = 301 + i
                menu_calc.Append(menu_no, title)
                self.menu_dic[menu_no] = self.pdf_program_name[i][0]

        # クローズボタンが押された場合の処理を設定(self.ExitHandlerの実行）
        self.Bind(wx.EVT_CLOSE, self.ExitHandler)

        # メニューの設定
        # 「ファイル」バーのメニューの作成
        menu_file = wx.Menu()
        # menu_file.Append(ID_READ_PARA, '応答計算パラメータ読込' + '\t' + 'Ctrl+O')
        # menu_file.Append(ID_CALC_RESPONSE, '応答解析' + '\t' + 'Ctrl+R')
        # menu_file.AppendSeparator()
        menu_file.Append(ID_EXIT, '終了' + '\t' + 'Ctrl+Q')
        # 「編集」バーのメニューの作成
        # menu_edit = wx.Menu()
        # menu_edit.Append(ID_COPY, 'コピー')
        # menu_edit.Append(ID_PASTE, '貼り付け')
        # メニューの作成

        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, 'ファイル')
        # menu_bar.Append(menu_edit, '編集')
        menu_bar.Append(menu_calc, '処理')
        # menu_bar.Append(menu_graph, '画面表示')
        # menu_bar.Append(menu_pdf, 'PDF作図')
        # メニューの貼り付け
        self.SetMenuBar(menu_bar)
        # メニューの選択が行われた場合の処理(self.selectMenuの実行）
        self.Bind(wx.EVT_MENU, self.selectMenu)

        self.GraphDataExist = False     # 起動時はグラフデータはなし
        self.pageMax = 0                 # 起動時はグラフページ数はゼロ

        self.page = 1
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        # from os.path import expanduser
        # self.home = expanduser("~") + "\\Desktop\\PDF_DATA"
        if os.path.exists(self.home) == False:
            os.mkdir(self.home)
    # self.timer.Start(1000)  # 1 second interval

    def OnTimer(self, event):
        # t1 = time.time()
        h1 = self.graph_panel1.GetScrollPos(wx.VERTICAL)
        print('\r{}'.format(h1),end="")
        p1 = 0
        for i in range(self.pageMax):
            if h1 < (self.page_pos[i] + self.page_heigth[i]-10):
                p1 = i + 1
                break
        if p1 == 0 :
            p1 = self.page
        # p1 = int((self.graph_panel1.GetScrollPos(wx.VERTICAL) + 10)/ SCROLL_PAGE_HEIGHT) + 1
        if self.page != p1:
            self.page = p1
            self.text_change(p1)

        if self.new_text[self.page - 1] != self.ocr_text.Value:
            self.ocr_text_save_button.Enable()
        else:
            self.ocr_text_save_button.Disable()

        if self.result_text_data[self.page - 1] != self.result_text.Value:
            self.result_save_button.Enable()
        else:
            self.result_save_button.Disable()

        # p2 = self.graph_panel1.GetScrollRange(wx.VERTICAL)
        # print('\r' ,p1 ," " ,p2 ,end="")

    # def OnChildFocus(self, event):
    #     print(event)
    #     # self.graph_panel1.Scroll(0,10)
    #     pass

    def mainExit(self):
        '''
        プログラムの終了処理
        :return:
        '''
        dlg = wx.MessageDialog(self, message=u"終了します。よろしいですか？", caption=u"終了確認", style=wx.YES_NO)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            wx.Exit()

    def dummy(self):
        pass

    def selectMenu(self, event):
        '''
        メニューが選択された場合の処理
        :param event:
        :return: なし
        '''
        id1 = event.GetId()
        # print('MenuSelected! ' + str(id))
        if id1 == ID_EXIT or id1 == wx.ID_EXIT:
            self.mainExit()
        elif id1 == ID_READ_PARA:
            self.read_para()
        elif id1>=300 and id1<400:
            button_kind = self.menu_dic[id1]
            button_kind[0]()
        # elif id1 >= 400 and id1 < 600:
        #     button_kind = self.menu_dic[id1]
        #     para = button_kind[1]  # 関数に送るパラメータ
        #     fname = button_kind[2]
        #     if self.page_init(para, fname):
        #         for func in button_kind[0]:
        #             self.page_n += func()  # 関数の実行
        #         self.page_i = 1
        #         self.page_close()

    def exec_button_handler(self, event):
        '''
        ボタン処理（押されたボタンのラベルを取得して、辞書から関数を探して実行）
        :param event:
        :return:
        '''
        # 押されたボタンのラベルの取得
        button_label = event.EventObject.Label
        # 辞書から該当する関数名を検索し、(パラメータ)をつけて実行
        self.calc_dic[button_label][0]()

    def ExitHandler(self, event):
        '''
        クロースボタンが押された場合のイベント処理
        :param event:
        :return: なし
        '''
        self.mainExit()

    def pdf_read(self):

        # 1.インストール済みのTesseractのパスを通す
        # path_tesseract = "C:\\Program Files\\Tesseract-OCR"
        # if path_tesseract not in os.environ["PATH"].split(os.pathsep):
        #     os.environ["PATH"] += os.pathsep + path_tesseract

        # 2.OCRエンジンの取得
        tools = pyocr.get_available_tools()
        tool = tools[0]

        # ファイルダイアログの表示
        fTyp = [("", "*.pdf")]  # 拡張子の指定
        # iDir = os.path.abspath(os.path.dirname(__file__))  # ダイアログの表示ディレクトリー
        iDir = self.data_dir
        filter = "Pdf files (*.pdf)|*.pdf"
        dlg = wx.FileDialog(None, 'select files', iDir,filter, style=wx.FD_OPEN | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPaths()
        else:
            file = []

        list2 = list(file)  # 複数のファイル名を取得
        fn = len(list2)
        if fn > 0:
            for file_name in list2:
                dirname = os.path.dirname(file_name)
                self.name = os.path.splitext(os.path.basename(file_name))[0]
                # (self.name, extention) = os.path.splitext(file_name)
                self.new_dir_path = dirname + '/' +self.name
                over_write_flag = True
                if os.path.exists(self.new_dir_path):  # すでに同じ名のディレクトリーが存在する場合、ファイル毎削除する
                    dialog = wx.MessageDialog(None, u'すでに同じ名前({})のデータが存在します。\n データを上書きしますか？'.format(self.name),
                                              u'確認', style=wx.YES_NO | wx.NO_DEFAULT)
                    result = dialog.ShowModal()
                    if result == wx.ID_YES:
                        shutil.rmtree(self.new_dir_path)
                        time.sleep(1.0)
                        # over_write_flag = True
                        os.mkdir(self.new_dir_path)
                    else:
                        over_write_flag = False
                else:
                    os.mkdir(self.new_dir_path)

                time1 = time.time()
                pdf_file_reader = PdfFileReader(file_name)  # (5)
                page_nums = pdf_file_reader.getNumPages()

                aa = ' pdf[{}] ページ {}/{}'.format(self.name, 0, page_nums)
                dialog = wx.ProgressDialog(u'PDFデータのOCR実行中 ', aa, page_nums,
                                           parent=None,
                                           style=wx.PD_APP_MODAL | wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT )
                dialog.Show()

                if page_nums>0:
                    self.new_file = []
                    self.new_image = []
                    self.new_text = []
                    self.analysis_text_data = []
                    self.result_text_data = []

                    for num in range(page_nums):  # (7)
                        aa = ' pdf[{}] ページ {}/{}'.format(self.name, num+1, page_nums) + \
                             '\n 経過時間={:.0f} sec'.format(time.time() - time1)
                        alive, skip = dialog.Update(num, aa)

                        file_object = pdf_file_reader.getPage(num)  # (7)
                        pdf_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(3) + '.pdf'  # (8)
                        self.new_file.append(pdf_file_name)
                        if over_write_flag:
                            # self.new_file.append(pdf_file_name)
                            pdf_file_writer = PdfFileWriter()  # (9)
                            with open(pdf_file_name, 'wb') as f:  # (10)
                                pdf_file_writer.addPage(file_object)  # (11)
                                pdf_file_writer.write(f)  # (12)

                        images = convert_from_path(pdf_file_name)

                        self.new_image.append(images[0])

                        # 4.ＯＣＲ実行
                        if over_write_flag:
                            builder = pyocr.builders.TextBuilder()
                            result = tool.image_to_string(images[0], lang="jpn", builder=builder)
                            result.replace(' ','')
                            result2 = result.splitlines()
                            result3 = ''
                            for t in result2:
                                t.replace(' ','')
                                if t != "" and t != " ":
                                    result3 += t + "\n"
                            result3 = result3.replace(' ', '')
                            self.new_text.append(result3)
                            text_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(3) + '.txt'
                            with open(text_file_name, mode='w') as f:
                                f.write(result3)

                        else:
                            text_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(3) + '.txt'
                            with open(text_file_name, mode='r') as f:
                                result3 = f.read()
                                self.new_text.append(result3)

                        self.ocr_text.SetValue(result3)

                        if over_write_flag:
                            t1, t2 = self.text_analysis()
                            self.analysis_text.SetValue(t1)
                            self.analysis_text_data.append(t1)
                            self.result_text.SetValue(t2)
                            self.result_text_data.append(t2)
                            analysis_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(
                                3) + '.dat'
                            with open(analysis_file_name, mode='w') as f:
                                f.write(t1)

                            result_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(
                                3) + '.csv'
                            with open(result_file_name, mode='w') as f:
                                f.write(t2.replace('\t', ','))

                        else:
                            analysis_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(3) + '.dat'
                            if os.path.exists(analysis_file_name):
                                with open(analysis_file_name, mode='r') as f:
                                    t1 = f.read()
                                    self.analysis_text_data.append(t1)
                                    self.analysis_text.SetValue(t1)
                            else:
                                self.analysis_text_data.append('')
                                self.analysis_text.SetValue('')

                            result_file_name = self.new_dir_path + '/' + self.name + '-' + str(num + 1).zfill(3) + '.csv'
                            if os.path.exists(result_file_name):
                                with open(result_file_name, mode='r') as f:
                                    t2 = f.read()
                                    t2 = t2.replace(',','\t')
                                    self.result_text_data.append(t2)
                                    self.result_text.SetValue(t2)
                            else:
                                self.result_text_data.append('')
                                self.result_text.SetValue('')


                    self.pageMax = page_nums
                    self.page = 1
                    self.page_set()



    def text_save_button_handler(self,event):
        if self.new_text[self.page-1] != self.ocr_text.Value:
            dialog = wx.MessageDialog(None, u'修正したテキストデータを保存しますか？',
                                      u'確認', style=wx.YES_NO | wx.NO_DEFAULT)
            result = dialog.ShowModal()
            t1 = time.time()
            if result == wx.ID_YES:
                text_file_name = self.new_dir_path + '/' + self.name + '-' + str(self.page).zfill(3) + '.txt'
                result3 = self.ocr_text.Value
                self.new_text[self.page - 1]=result3
                with open(text_file_name, mode='w') as f:
                    f.write(result3)

    def text_analysis_button_handler(self, event):
        t1,t2 = self.text_analysis()
        self.analysis_text.SetValue(t1)
        self.analysis_text_data[self.page - 1] = (t1)
        self.result_text.SetValue(t2)
        self.result_text_data[self.page - 1] = t2
        analysis_file_name = self.new_dir_path + '/' + self.name + '-' + str(self.page).zfill(3) + '.dat'
        with open(analysis_file_name, mode='w') as f:
            f.write(t1)

        result_file_name = self.new_dir_path + '/' + self.name + '-' + str(self.page).zfill(3) + '.csv'
        with open(result_file_name, mode='w') as f:
            f.write(t2.replace('\t',','))

    def text_result_button_handler(self, event):
        t2 = self.result_text.Value
        if self.result_text_data[self.page - 1] != t2:
            result_file_name = self.new_dir_path + '/' + self.name + '-' + str(self.page).zfill(3) + '.csv'
            with open(result_file_name, mode='w') as f:
                f.write(t2.replace('\t', ','))

    def text_analysis(self):
        if self.ocr_text.Value != '':
            # m = MeCab.Tagger(r'-Ochasen')
            # t1 = m.parse(self.ocr_text.Value)

            token_filters = []
            char_filters = []
            tokenizer = Tokenizer(self.user_dic, udic_enc="utf8")
            analyzer = Analyzer(char_filters, tokenizer, token_filters)
            t0 = self.ocr_text.Value
            t1 = ''
            for token in analyzer.analyze(t0):
                if token.base_form != '\n':
                    t1 += str(token).replace(',',' ').replace('\t',' ') + '\n'
            # self.analysis_text.SetValue(t1)
            day_list = self.day_find(self.ocr_text.Value)
            t2 = ''

            doc_list = self.doc_find(t1, '伺')
            if len(doc_list)>0 :
                for g in doc_list:
                    t2 += '書類\t' + g + '\n'

            if len(day_list)>0 :
                for d in day_list:
                    t2 += '日付\t' + d + '\n'

            bu_list = self.group_find(t1, '部')
            if len(bu_list)>0 :
                for g in bu_list:
                    t2 += '所属部\t' + g + '\n'

            sitsu_list = self.group_find(t1, '室')
            if len(sitsu_list)>0 :
                for g in sitsu_list:
                    t2 += '所属室\t' + g + '\n'

            na_list = self.name_find(t1)
            if len(na_list)>0 :
                for g in na_list:
                    t2 += '氏名\t' + g + '\n'

            # t2 += t1
            # self.result_text.SetValue(t2)
        else:
            t1 = ''
            t2 = ''

        return t1,t2

    def day_find(self, content):
        # import re
        pattern = ['\d{4}年\d+月\d+日',
                   '昭和\d+年\d+月\d+日', '昭和元年\d+月\d+日',
                    '平成\d+年\d+月\d+日', '平成元年\d+月\d+日',
                   '令和\d+年\d+月\d+日', '令和元年\d+月\d+日'
                   ]
        day_list = []
        for p1 in pattern:
            search_result = re.findall(p1, content, re.S)
            if len(search_result)>0:
                for d1 in search_result:
                    day_list.append(d1)

        return set(day_list)

    def doc_find(self, content, part):
        # import re
        doc_list = []
        if content!='' and part != '':
            pattern = '\D+' + part
            content2 = content.splitlines()
            for c1 in content2:
                c2 = c1.split()
                if len(c2)>3:
                    # if c2[3] == '名詞-固有名詞-一般':
                    if c2[1] == '名詞' and c2[2] == '固有名詞' and c2[3] == '一般':
                        search_result = re.findall(pattern, c2[0], re.S)
                        if len(search_result)>0:
                            for d1 in search_result:
                                doc_list.append(d1)

        return set(doc_list)

    def group_find(self, content, part):
        # import re
        group_list = []
        if content!='' and part != '':
            pattern = '\D+' + part
            content2 = content.splitlines()
            for c1 in content2:
                c2 = c1.split()
                if len(c2)>3:
                    if c2[1] == '名詞' and c2[2] == '固有名詞' and c2[3] == '組織':
                    # if c2[3] == '名詞-固有名詞-組織':
                        search_result = re.findall(pattern, c2[0], re.S)
                        if len(search_result)>0:
                            for d1 in search_result:
                                group_list.append(d1)

        return set(group_list)

    def name_find(self, content):
        # import re
        name_list = []
        if content!='' :
            content2 = content.splitlines()
            for c1 in content2:
                c2 = c1.split()
                if len(c2)>3:
                    if c2[1] == '名詞' and c2[2] == '固有名詞' and c2[3] == '人名' and c2[4] == '一般':
                    # if c2[3] == '名詞-固有名詞-人名-一般':
                        name_list.append(c2[0])

        return set(name_list)   # 重複データを削除

    def page_set(self):
        self.v_layout = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.page_heigth = []
        self.page_pos = []
        h1 = 0
        for p1 in range(self.pageMax):
            text = wx.StaticText(self.graph_panel1, wx.ID_ANY, '\n  [ page {}/{} ]'.format(p1 + 1, self.pageMax))
            text.SetFont(font)
            self.v_layout.Add(text)
            s = self.new_image[p1].size
            if s[1]>s[0] :
                image2 = self.new_image[p1].resize((self.gx, int(self.gx * 1.4142)), Image.BICUBIC)
                wximage = wx.Image(image2.size[0], image2.size[1])
                wximage.SetData(image2.convert('RGB').tobytes())

                self.pdf_panel = wx.Panel(self.graph_panel1, wx.ID_ANY, pos=(0, 0),
                                          size=(self.gx, int(self.gx * np.sqrt(2.0))))
                # self.pdf_panel.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
                bitmap = wximage.ConvertToBitmap()
                wx.StaticBitmap(self.pdf_panel, -1, bitmap, pos=(0, 0), size=wximage.GetSize())
                h = SCROLL_PAGE_HEIGHT
            else:
                image2 = self.new_image[p1].resize((self.gx, int(self.gx / 1.4142)), Image.BICUBIC)
            # wximage = wx.EmptyImage(image2.size[0], image2.size[1])
                wximage = wx.Image(image2.size[0], image2.size[1])
                wximage.SetData(image2.convert('RGB').tobytes())

                self.pdf_panel = wx.Panel(self.graph_panel1, wx.ID_ANY, pos=(0, 0), size=(self.gx, int(self.gx / np.sqrt(2.0)+7)))
                # self.pdf_panel.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
                bitmap = wximage.ConvertToBitmap()
                wx.StaticBitmap(self.pdf_panel, -1, bitmap, pos=(0, 0), size=wximage.GetSize())
                h = int(SCROLL_PAGE_HEIGHT/2)+1

            self.page_heigth.append(h)
            self.page_pos.append(h1)
            h1 += h
            self.v_layout.Add(self.pdf_panel)

        self.graph_panel1.SetSizer(self.v_layout)
        self.graph_panel1.Update()
        self.graph_panel1.SetupScrolling()
        self.ocr_text.SetValue(self.new_text[self.page - 1])
        self.ocr_text_label.SetLabel('OCRテキストデータ（{}/{}ページ)\n [File Name={}]'.format(self.page, self.pageMax, self.name))
        self.analysis_text_label.SetLabel('形態解析テキストデータ({}/{})'.format(self.page, self.pageMax))
        self.result_text_label.SetLabel('認識テキストデータ({}/{})'.format(self.page, self.pageMax))
        self.analysis_text.SetValue(self.analysis_text_data[self.page - 1])
        self.result_text.SetValue(self.result_text_data[self.page - 1])

        self.Refresh()  # Windowを再描画する。これを実行しないと表示がおかしくなる。

        self.timer.Start(200)  # 1 second interval

    def text_change(self, p1):
        self.ocr_text.SetValue(self.new_text[p1 - 1])
        self.analysis_text.SetValue(self.analysis_text_data[p1 - 1])
        self.result_text.SetValue(self.result_text_data[p1 - 1])
        self.ocr_text_label.SetLabel('OCRテキストデータ（{}/{}ページ)'.format(self.page, self.pageMax))
        self.analysis_text_label.SetLabel('形態解析テキストデータ({}/{})'.format(self.page, self.pageMax))
        self.result_text_label.SetLabel('認識テキストデータ({}/{})'.format(self.page, self.pageMax))

    # def pdf_show(self,p1):
    #
    #     image2 = self.new_image[p1 - 1].resize((self.gx, int(self.gx * 1.4142)), Image.BICUBIC)
    #     wximage = wx.EmptyImage(image2.size[0], image2.size[1])
    #     wximage.SetData(image2.convert('RGB').tobytes())
    #
    #     self.v_layout = wx.BoxSizer(wx.VERTICAL)
    #     self.pdf_panel = wx.Panel(self.graph_panel1, wx.ID_ANY, pos=(0, 0), size=(self.gx, int(self.gx * np.sqrt(2.0))))
    #     self.pdf_panel.Bind(wx.EVT_NAVIGATION_KEY,self.OnChildFocus)
    #     bitmap = wximage.ConvertToBitmap()
    #     wx.StaticBitmap(self.pdf_panel, -1, bitmap, pos=(0, 0), size=wximage.GetSize())
    #     self.v_layout.Add(self.pdf_panel)
    #     self.graph_panel1.SetSizer(self.v_layout)
    #     self.graph_panel1.Update()
    #     self.graph_panel1.SetupScrolling()
    #     self.text_2.SetValue(self.new_text[p1 - 1])
    #     self.t0.SetLabel('テキストデータ（{}/{}ページ)'.format(self.page, self.pageMax))

    def next_page(self):
        if self.pageMax>0:
            self.page += 1
            if self.page<=self.pageMax:
                # p1 = (self.page-1)*SCROLL_PAGE_HEIGHT - self.graph_panel1.GetScrollPos(wx.VERTICAL)
                p1 = self.page_pos[self.page-1] - self.graph_panel1.GetScrollPos(wx.VERTICAL)
                # self.graph_panel1.ScrollLines(p1)
                if "wxMSW" in wx.PlatformInfo:
                    self.graph_panel1.ScrollLines(p1)
                else:
                    sp = self.graph_panel1.GetScrollPos(wx.VERTICAL)
                    r1 = self.graph_panel1.GetScrollRange(wx.VERTICAL) - \
                            self.graph_panel1.GetScrollThumb(wx.VERTICAL)
                    e = wx.ScrollEvent(wx.wxEVT_SCROLLWIN_LINEDOWN,
                                       self.graph_panel1.GetId(),
                                       min(sp + 1, r1),
                                       wx.VERTICAL)
                    for i in range(p1):
                        self.graph_panel1.GetEventHandler().ProcessEvent(e)

                self.text_change(self.page)
            else:
                self.page = self.pageMax

    def before_page(self):
        if self.pageMax > 0:
            self.page -= 1
            if self.page >= 1:
                # p1 = (self.page - 1) * SCROLL_PAGE_HEIGHT - self.graph_panel1.GetScrollPos(wx.VERTICAL)
                p1 = self.page_pos[self.page - 1] - self.graph_panel1.GetScrollPos(wx.VERTICAL)
                # self.graph_panel1.ScrollLines(p1)

                if "wxMSW" in wx.PlatformInfo:
                    self.graph_panel1.ScrollLines(p1)
                else:
                    sp = self.graph_panel1.GetScrollPos(wx.VERTICAL)
                    e = wx.ScrollEvent(wx.wxEVT_SCROLLWIN_LINEUP,
                                       self.graph_panel1.GetId(),
                                       max(sp - 1, 0),
                                       wx.VERTICAL)
                    for i in range(abs(p1)):
                        self.graph_panel1.GetEventHandler().ProcessEvent(e)



                self.text_change(self.page)
            else:
                self.page = 1

    def pdf_write(self):
        '''
        パワースペクトル密度計算処理
        :return:
        '''

        pass


if __name__ == '__main__':
    app = wx.App()
    fx = FRAME_WIDTH
    fy = FRAME_HEIGHT
    s1 = wx.Size(fx,fy)
    frame = MainFrame(None, wx.ID_ANY, u'PDF読込プログラム', size=s1 )
    # frame.set_panel()

    frame.Show()
    app.MainLoop()
