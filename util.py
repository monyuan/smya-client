from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal as Signal


class Util(QThread):
    signal = Signal(str)
    finish = Signal()
    
    def __init__(self):
        super(Util, self).__init__()
    
    def do(self):
        pass
