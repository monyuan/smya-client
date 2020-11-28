import _thread
import sys
from time import sleep
from os.path import abspath, dirname, join

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon, QCursor
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect,
                             QSystemTrayIcon, QMenu, QAction, QMainWindow, QApplication)

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


print(resource_path())


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
        _thread.start_new_thread(self.handler.ad, ())
        self.handler.app_update()

    def click_handler(self):
        """
        按钮点击事件
        :return:
        """
        self.pushButton.clicked.connect(self.close)  # 关闭
        self.pushButton_2.clicked.connect(self.ButtonMinSlot)  # 最小化
        self.login.clicked.connect(self.handler.login)
        self.ad1.mousePressEvent = self.handler.jump_ad
        _thread.start_new_thread(self.info_window_scroll, ())

    def send_key_event(self, data):
        self.show()

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
        self.hide()

    def info_window_scroll(self):
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
        "保险起见，为了完整的退出"
        self.setVisible(False)
        self.parent().exit()
        sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.setStyleSheet(style())
    w.show()
    sys.exit(app.exec_())

# build
# pyinstaller --clean -F -w app.py -i icon.ico --add-data "img;img" --add-data "icon.ico;./"
