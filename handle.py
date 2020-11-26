import binascii
from datetime import datetime

import requests
from PyQt5.QtWidgets import QMessageBox
from pyDes import des, CBC, PAD_PKCS5

SERVER = "https://smya.cn/client/login"


def encrypt(s, k):
    """
    :param s: your safe_code + device_id, eg:3023337AB72ED12FAE11EBAD2AF4D108A7BF2B
    :param k: your safe_code + current hour(16:00),eg:30233316
    :return: encrypt str
    """
    k = k + str(datetime.now().hour)
    k = des(k, CBC, k, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return str(binascii.b2a_hex(en), encoding='utf8')


def login_to_server(device_id, safe_code):
    """
    :param device_id:
    :param safe_code:
    :return: tcp server_name, tcp client_id
    """
    data = {
        "device_id": device_id,
        "str": encrypt(safe_code + device_id, safe_code)
    }
    res = requests.post(SERVER, data=data).json()
    if res['code'] != 0: return None
    server_name = res['server_name']
    client_id = res['client_id']
    return server_name, client_id


class Handle(object):
    def __init__(self, window):
        self.w = window
    
    def login(self):
        """
        登陆到服务器
        :return:
        """
        device_id = self.w.device_id.text().strip()
        safe_code = self.w.safe_code.text().strip()
        self.w.login.setDisabled(True)
        self.w.device_id.setDisabled(True)
        self.w.safe_code.setDisabled(True)
        if len(device_id) != 30:
            QMessageBox.warning(self.w, "错误！", "你的设备ID错误！")
            return
        if len(safe_code) != 6:
            QMessageBox.warning(self.w, "错误！", "你的安全码错误！")
            return
        print("ok")
