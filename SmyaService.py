import _thread
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from os.path import abspath, dirname, join, exists
from time import sleep

import requests
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon, QCursor
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect,
                             QSystemTrayIcon, QMenu, QAction, QMainWindow, QApplication, QMessageBox)

from handle import APP_VERSION
from qss import style
from ui import *

BACKGROUND_COLOR = "#ffffff"
# 按钮高度
BUTTON_HEIGHT = 25
# 按钮宽度
BUTTON_WIDTH = 20
TITLE_COLOR = "#ffffff"  # 头部颜色

from handle import Handle


def resource_path(*relative_path):
    base_path = getattr(sys, '_MEIPASS', abspath(join(dirname(__file__))))
    return join(base_path, *relative_path).replace("\\", "/")


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        ti = TrayIcon(self)
        ti.show()
        self.handler = Handle(self)
        self.m_flag = None
        self.m_Position = None
        self.setupUi(self)
        self.init_ui()
        self.click_handler()
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 255))
        self.shadow.setOffset(0, 0)
        self.shadow1 = QGraphicsDropShadowEffect()
        self.shadow1.setBlurRadius(15)
        self.shadow1.setOffset(0, 0)
        self.shadow1.setColor(QColor(0, 0, 0, 255))
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(15)
        self.shadow2.setOffset(0, 0)
        self.shadow2.setColor(QColor(0, 0, 0, 255))
        self.widget_2.setGraphicsEffect(self.shadow)
        self.widget.setGraphicsEffect(self.shadow1)  # 加阴影，更立体

    def init_ui(self):
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 去边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.centralwidget.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置pyqt自动生成的centralwidget背景透明
        self.centralwidget.setAutoFillBackground(True)
        self.pushButton.setFixedSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))  # 设置按钮大小
        self.pushButton_2.setFixedSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))  # 设置按钮大小
        btn_close_normal = resource_path(join("img", "btn_close_normal.png"))
        btn_close_down2 = resource_path(join("img", "btn_close_down2.png"))
        btn_close_down = resource_path(join("img", "btn_close_down.png"))
        btn_set_normal = resource_path(join("img", "btn_set_normal.png"))
        btn_min_normal = resource_path(join("img", "btn_min_normal.png"))
        Qss = 'QWidget#widget_2{background-color: %s;}' % BACKGROUND_COLOR
        Qss += 'QWidget#widget{background-color: %s;border-top-right-radius:5 ;border-top-left-radius:5 ;}' % TITLE_COLOR
        Qss += 'QWidget#widget_3{background-color: %s;}' % TITLE_COLOR
        Qss += 'QPushButton#pushButton{margin-top:6;background-color: %s;border-image:url(%s);border-top-right-radius:5 ;}' % (
            TITLE_COLOR, btn_close_normal)
        Qss += 'QPushButton#pushButton:hover{border-image:url(%s); border-top-right-radius:5 ;}' % btn_close_down2
        Qss += 'QPushButton#pushButton:pressed{border-image:url(%s);border-top-right-radius:5 ;}' % btn_close_down
        Qss += 'QPushButton#pushButton_2{margin-top:8;background-color: %s;border-image:url(%s);}' % (
            TITLE_COLOR, btn_min_normal)
        Qss += 'QPushButton#pushButton_2:hover{background-color: %s;border-image:url(%s);}' % (BACKGROUND_COLOR,
                                                                                               btn_min_normal)
        Qss += 'QPushButton#pushButton_2:pressed{background-color: %s;border-top-left-radius:5 ;}' % BACKGROUND_COLOR
        Qss += 'QPushButton#pushButton_3{border-image:url(%s);background-color: %s;border-top-left-radius:5}' % (
            btn_set_normal, TITLE_COLOR)
        Qss += '#label{background-color:rbga(0,0,0,0);color:#111111;}'
        self.setStyleSheet(Qss)  # 边框部分qss重载
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setWindowTitle('神秘鸭')
        self.textBrowser.append("欢迎使用神秘鸭 smya.cn")
        self.read_login_info()
        _thread.start_new_thread(self.handler.ad, ())
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "神秘鸭 v{}".format(APP_VERSION)))
        self.progressBar.setHidden(True)

    def click_handler(self):
        """
        按钮点击事件
        :return:
        """
        self.pushButton.clicked.connect(self.exit_app)  # 关闭
        self.pushButton_2.clicked.connect(self.ButtonMinSlot)  # 最小化
        self.login.clicked.connect(self.handler.login)
        self.video_script.clicked.connect(self.start_script)
        self.ad1.mousePressEvent = self.handler.jump_ad
        _thread.start_new_thread(self.info_window_scroll, ())

    def exit_app(self):
        box = QMessageBox(QMessageBox.Information, "提示！", "你是要退出还是最小化？")
        yes = box.addButton(self.tr("退出"), QMessageBox.YesRole)
        no = box.addButton(self.tr("最小化"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() == yes:
            self.close()
        else:
            self.hide()

    def read_login_info(self):
        login_file = join(os.path.expanduser('~'), 'smya.json')
        _thread.start_new_thread(self.check_old_script, ())
        try:
            if exists(login_file) is True:
                with open(login_file, 'r') as f:
                    info = json.loads(f.readline())
                    device_id = info['device_id']
                    safe_code = info['safe_code']

                    if len(device_id) and len(safe_code) > 5:
                        self.device_id.setText(device_id)
                        self.safe_code.setText(safe_code)
                        self.handler.login()
        except:
            pass

    def check_old_script(self):
        """下个版本可以删掉"""
        new_path = os.path.join(os.path.expanduser('~'), 'smyascript')
        old_path = resource_path('scripts')
        if os.path.exists(new_path) is False and os.path.exists(old_path) is True:
            shutil.copytree(old_path, new_path)

    def send_key_event(self, data):
        self.show()

    def start_script(self):
        try:
            tools_path = os.path.join(os.path.expanduser('~'), 'smyatoolsv2')
            if os.path.exists(join(tools_path, "smyatools.exe")) is True:
                subprocess.Popen(join(tools_path, "smyatools.exe"))
            else:
                if os.path.exists(tools_path) is True:
                    os.rmdir(tools_path)
                box = QMessageBox(QMessageBox.Warning, "提示！", "神秘鸭录制工具未安装或需要更新，现在是否安装！")
                yes = box.addButton(self.tr("安装"), QMessageBox.YesRole)
                no = box.addButton(self.tr("取消"), QMessageBox.NoRole)
                box.exec_()
                if box.clickedButton() == yes:
                    self.progressBar.setHidden(False)
                    self.progressBar.setValue(0)
                    f = requests.get("https://cdn.monyuan.com/smya/smyatoolsv2.zip", stream=True)
                    length = float(f.headers['content-length'])
                    count = 0
                    time1 = time.time()
                    down_file = join(tools_path, "smyatoolsv2.zip")
                    os.mkdir(tools_path)
                    with open(down_file, "wb") as F:
                        for chunk in f.iter_content(chunk_size=1024):
                            if chunk:
                                F.write(chunk)
                                count += len(chunk)
                                if time.time() - time1 > 2:
                                    p = int(count / length * 100)
                                    self.progressBar.setValue(p)
                                    if p == 100:
                                        self.progressBar.setHidden(True)
                    F.close()
                    zipFile = zipfile.ZipFile(down_file)
                    for file in zipFile.namelist():
                        zipFile.extract(file, os.path.expanduser('~'))
                    zipFile.close()
                    os.remove(down_file)
                    QMessageBox.information(self, '提示！', '你已下载完成，可以使用啦！')
        except Exception as E:
            self.textBrowser.append(
                '<span style="color: red">{} {}</span>'.format(datetime.strftime(datetime.now(), '%H:%M:%S'),
                                                               E))
            QMessageBox.warning(self, '错误！', '出现问题，请看运行日志！')

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(QtCore.Qt.OpenHandCursor))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_flag = False
            self.setCursor(QCursor(QtCore.Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        """
        拖动事件
        :param event:
        :return:
        """
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(event.globalPos() - self.m_Position)  # 更改窗口位置
            event.accept()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.hide()

    def ButtonMinSlot(self):
        self.showMinimized()

    def info_window_scroll(self):
        sleep(3.5)
        while True:
            self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
            sleep(0.5)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.showMenu()
        self.other()

    def showMenu(self):
        "设计托盘的菜单，这里我实现了一个二级菜单"
        self.menu = QMenu()
        self.menu1 = QMenu()
        self.showAction1 = QAction("显示窗口", self, triggered=self.showM)
        self.quitAction = QAction("退出程序", self, triggered=self.quit)

        self.menu1.addAction(self.showAction1)

        self.menu.addAction(self.showAction1)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def other(self):
        self.activated.connect(self.iconClied)
        self.setIcon(QIcon(resource_path("icon.ico")))
        self.icon = self.MessageIcon()
        # 设置图标

    def iconClied(self, reason):
        "鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击"
        if reason == 2 or reason == 3:
            pw = self.parent()
            if pw.isVisible():
                pw.hide()
            else:
                pw.show()

    def showM(self):
        pw = self.parent()
        pw.show()

    def quit(self):
        sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.setStyleSheet(style())
    if 'min' in sys.argv:
        w.hide()
    else:
        w.show()
    sys.exit(app.exec_())

# build
# pyinstaller --clean -y -w -i icon.ico --add-data "img;img" --add-data "icon.ico;./" SmyaService.py
