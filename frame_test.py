#! /usr/bin/env python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-

"""
画像ファイルをドラッグアンドドロップしてダブルバッファで表示。
マウスドラッグで画像表示位置を移動してみるテスト

Windows7 x64 + Python 2.7.10 + wxPython 3.0.2.0 で動作確認。
"""

import wx

USE_BUFFERED_DC = True


class MyObj():
    """マウスドラッグで移動できるオブジェクト用のクラス"""

    def __init__(self, bmp, x=0, y=0):
        """コンストラクタ"""
        self.bmp = bmp  # bitmapを記録
        self.pos = wx.Point(x, y)  # 表示位置を記録
        self.diff_pos = wx.Point(0, 0)

    def HitTest(self, pnt):
        """与えられた座標とアタリ判定して結果を返す"""
        rect = self.GetRect()  # 矩形領域を取得
        return rect.Contains(pnt.x, pnt.y)  # 座標が矩形内に入ってるか調べる

    def GetRect(self):
        """矩形領域を返す"""
        return wx.Rect(self.pos.x, self.pos.y,
                       self.bmp.GetWidth(), self.bmp.GetHeight())

    def SavePosDiff(self, pnt):
        """
        マウス座標と自分の座標の相対値を記録。
        この情報がないと、画像をドラッグした時の表示位置がしっくりこない
        """
        self.diff_pos.x = self.pos.x - pnt.x
        self.diff_pos.y = self.pos.y - pnt.y

    def Draw(self, dc, select_enable):
        """与えられたDCを使って画像を描画する"""
        if self.bmp.IsOk():
            r = self.GetRect()  # 矩形領域を取得

            # ペンを設定しないと何故か描画できない
            dc.SetPen(wx.Pen(wx.BLACK, 4))
            dc.DrawBitmap(self.bmp, r.x, r.y, True)  # 画像を描画

            if select_enable:
                # 画像枠を描画
                dc.SetBrush(wx.TRANSPARENT_BRUSH)  # 透明塗り潰し
                dc.SetPen(wx.Pen(wx.RED, 1))  # 赤い線を指定
                # 矩形を描画
                dc.DrawRectangle(r.x, r.y, r.width, r.height)

            return True
        else:
            return False


class MyFileDropTarget(wx.FileDropTarget):
    """ドラッグアンドドロップ担当クラス"""

    def __init__(self, obj):
        """コンストラクタ"""
        wx.FileDropTarget.__init__(self)
        self.obj = obj  # ファイルのドロップ対象を覚えておく

    def OnDropFiles(self, x, y, filenames):
        """ファイルをドロップした時の処理"""
        self.obj.LoadImage(filenames)  # 親？の画像読み込みメソッドを呼ぶ
        return True


class MyFrame(wx.Frame):
    """ダブルバッファで表示するFrame"""

    def __init__(self, parent=None, title=""):
        """コンストラクタ"""

        wx.Frame.__init__(self, parent=parent, title=title, size=(800, 600))

        # PAINTイベント、SIZEイベントで呼ばれるメソッドを割り当てる
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # マウスボタンを押した時に呼ばれるメソッドを割り当てる
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)

        # マウスカーソルを動かした時に呼ばれるメソッドを割り当てる
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

        # 画像格納用リストを初期化
        self.objs = []

        # マウスドラッグ処理用の変数を確保
        self.drag_obj = None
        self.drag_start_pos = wx.Point(0, 0)

        # 描画用バッファ初期化のために一度 OnSize() を呼ぶ
        self.OnSize()

        # ファイルドロップの対象をフレーム全体に
        self.droptarget = MyFileDropTarget(self)

        # ファイルドロップ受け入れを設定
        self.SetDropTarget(self.droptarget)

    def LoadImage(self, files):
        """D&Dされた画像をロードして描画"""
        x, y = 0, 0
        for filepath in files:
            b = wx.Bitmap(filepath)
            obj = MyObj(b, x, y)
            self.objs.append(obj)
            x += 32
            y += 32

        self.UpdateDrawing()  # 描画更新

    def OnSize(self, event=None):
        """ウインドウサイズが変更された時に呼ばれる処理"""
        size = self.ClientSize  # クライアントのウインドウサイズを取得

        # ウインドウサイズで、空の描画用バッファ(bitmap)を作成
        self._buffer = wx.EmptyBitmap(*size)

        self.UpdateDrawing()  # 描画更新

    def UpdateDrawing(self):
        """描画更新"""
        dc = wx.MemoryDC()
        dc.SelectObject(self._buffer)

        self.Draw(dc)  # 実際の描画処理
        del dc  # Update()が呼ばれる前に MemoryDC を削除しておく必要がある

        # Falseを指定して背景を消さなくしたら画面のちらつきが出なくなった
        self.Refresh(eraseBackground=False)

        self.Update()

    def Draw(self, dc):
        """実際の描画処理"""
        dc.Clear()  # デバイスコンテキストでクリア
        for obj in self.objs:
            obj.Draw(dc, True)  # オブジェクトを描画

    def OnPaint(self, event=None):
        """画面書き換え要求があった時に呼ばれる処理"""
        if USE_BUFFERED_DC:
            # ダブルバッファを使う場合
            dc = wx.BufferedPaintDC(self, self._buffer)
        else:
            # ダブルバッファを使わない場合
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self._buffer, 0, 0, True)

    def FindObj(self, pnt):
        """マウス座標と重なってるオブジェクトを返す"""
        result = None
        for obj in self.objs:
            if obj.HitTest(pnt):
                result = obj
        return result

    def OnMouseLeftDown(self, event):
        """マウスの左ボタンが押された時の処理"""
        pos = event.GetPosition()  # マウス座標を取得
        obj = self.FindObj(pos)  # マウス座標と重なってるオブジェクトを取得
        if obj is not None:
            self.drag_obj = obj  # ドラッグ移動するオブジェクトを記憶
            self.drag_start_pos = pos  # ドラッグ開始時のマウス座標を記録
            self.drag_obj.SavePosDiff(pos)

    def OnMouseLeftUp(self, event):
        """マウスの左ボタンが離された時の処理"""
        if self.drag_obj is not None:
            pos = event.GetPosition()
            self.drag_obj.pos.x = pos.x + self.drag_obj.diff_pos.x
            self.drag_obj.pos.y = pos.y + self.drag_obj.diff_pos.y

        self.drag_obj = None
        self.UpdateDrawing()

    def OnMouseMotion(self, event):
        """マウスカーソルが動いた時の処理"""
        if self.drag_obj is None:
            # ドラッグしてるオブジェクトが無いなら処理しない
            return

        # ドラッグしてるオブジェクトの座標値をマウス座標で更新
        pos = event.GetPosition()
        self.drag_obj.pos.x = pos.x + self.drag_obj.diff_pos.x
        self.drag_obj.pos.y = pos.y + self.drag_obj.diff_pos.y
        self.UpdateDrawing()  # 描画更新


if __name__ == '__main__':
    # メイン処理
    app = wx.App(False)
    frame = MyFrame(None, "DnD Image display use Double Buffer")
    frame.Show()
    app.MainLoop()
