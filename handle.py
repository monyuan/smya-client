import _thread
import binascii
import json
from datetime import datetime
from time import sleep

import paho.mqtt.client as mqtt
import requests
from PyQt5.QtWidgets import QMessageBox
from pyDes import des, CBC, PAD_PKCS5

SERVER = "http://127.0.0.1:7777/client/login"


def log_info(text):
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    return '<p>{} {}</p>'.format(time, text)


def log_success(text):
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    return '<p style="color: green">{} {}</p>'.format(time, text)


def log_error(text):
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    return '<p style="color: red">{} {}</p>'.format(time, text)


def encrypt(s, k):
    """
    为了安全，进行简单的DES加密传输
    :param s: 要加密的字符串：你的设备安全码加上设备ID, eg:3023337AB72ED12FAE11EBAD2AF4D108A7BF2B
    :param k: 你的密钥：你的设备安全码加上当前时(16:00),eg:30233316
    :return: 加密后的字符串
    """
    k = k + str(datetime.now().hour)
    k = des(k, CBC, k, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return str(binascii.b2a_hex(en), encoding="utf8")


def decrypt(s, k):
    """解密"""
    iv = str(k) + str(datetime.now().hour)
    k = des(iv, CBC, iv, pad=None, padmode=PAD_PKCS5)
    s = bytes(s, encoding="utf8")
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return str(de, encoding="utf-8")


def login_to_server(device_id, safe_code):
    """
    :param device_id: 设备ID
    :param safe_code: 安全码
    :return: 将返回服务器地址、订阅节点
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "device_id": device_id,
        "str": encrypt(safe_code + device_id, safe_code)
    }
    res = requests.post(SERVER, data=json.dumps(data), headers=headers).json()
    return res


class Handle(object):
    def __init__(self, window):
        self.w = window
        self.subscribe = None
        self.server = None
        self.device_id = None
        self.server_port = 5201  # 不要修改这个端口，他很特别
        self.connect_message = 0
        self.client = None
        self.safe_code = 0
    
    def login(self):
        """
        登陆到服务器
        :return:
        """
        device_id = self.w.device_id.text().strip()
        self.safe_code = self.w.safe_code.text().strip()
        self.w.login.setDisabled(True)
        self.w.device_id.setDisabled(True)
        self.w.safe_code.setDisabled(True)
        if len(device_id) != 32:
            QMessageBox.warning(self.w, "错误！", "你的设备ID错误！")
            return
        if len(self.safe_code) != 6:
            QMessageBox.warning(self.w, "错误！", "你的安全码错误！")
            return
        
        try:
            self.connect_message = 0
            self.w.textBrowser.append(log_info("开始连接服务器..."))
            res = login_to_server(device_id, self.safe_code)
            if res["code"] == 0:
                server = res["data"]["server"]  # this is subscribe server addr
                subscribe = res["data"]["subscribe"]  # this is subscribe topic
                print(subscribe)
                self.subscribe = subscribe
                self.server = server
                self.device_id = device_id
                _thread.start_new_thread(self.connect_server, ())
            else:
                QMessageBox.warning(self.w, "错误！", "{}".format(res["msg"]))
        except Exception as E:
            print(E)
            self.w.login.setDisabled(False)
            self.w.device_id.setDisabled(False)
            self.w.safe_code.setDisabled(False)
            self.w.textBrowser.append(log_error("连接异常，请检查网络后重试！"))
    
    def mqtt_on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(self.subscribe)
            client.subscribe('client/{}'.format(self.subscribe), qos=1)
            self.w.textBrowser.append(log_success("连接成功，初始化..."))
            sleep(2)
            self.w.textBrowser.append(log_success("初始化完成！"))
        
        else:
            self.connect_message += 1
            self.w.textBrowser.append(log_error("掉线重连，第{}次...".format(self.connect_message)))
    
    def mqtt_on_message(self, client, userdata, msg):
        self.w.textBrowser.append(log_info("服务端下发了指令..."))
        try:
            en_data = str(msg.payload, encoding="utf-8")
            de_data = decrypt(en_data + "444", self.safe_code)
        except:
            self.w.textBrowser.append(log_error("指令解密失败！"))
    
    def connect_server(self):
        """
        client_id -  你可以自定义
        :return:
        """
        self.client = mqtt.Client(client_id=self.device_id)
        self.client.username_pw_set(self.device_id, password=self.subscribe)
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.connect(self.server, self.server_port, 60)
        self.client.loop_forever()
