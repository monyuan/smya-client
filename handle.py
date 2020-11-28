import _thread
import binascii
import json
import sys
from datetime import datetime
from time import sleep
import os
import re
import subprocess
import paho.mqtt.client as mqtt
import requests
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QImage, QPixmap, QDesktopServices
from PyQt5.QtWidgets import QMessageBox
from pyDes import des, CBC, PAD_PKCS5

SERVER = "http://127.0.0.1:7777"
SERVER_VERSION = 1
SERVER_TAG = 1


def log_info(text):
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    return '<span>{} {}</span>'.format(time, text)


def log_success(text):
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    return '<span style="color: green">{} {}</span>'.format(time, text)


def log_error(text):
    time = datetime.strftime(datetime.now(), '%H:%M:%S')
    return '<span style="color: red">{} {}</span>'.format(time, text)


def encrypt(s, k):
    """
    为了安全，进行简单的DES加密传输
    :param s: 要加密的字符串：你的设备安全码加上设备ID, eg:3023337AB72ED12FAE11EBAD2AF4D108A7BF2B
    :param k: 你的密钥：你的设备安全码加上当前时(16:00),eg:30233316
    :return: 加密后的字符串
    """
    current_hour = str(datetime.now().hour)
    if len(current_hour) == 1: current_hour += "0"
    k = str(k) + current_hour
    k = des(k, CBC, k, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return str(binascii.b2a_hex(en), encoding="utf8")


def decrypt(s, k):
    """解密"""
    current_hour = str(datetime.now().hour)
    if len(current_hour) == 1: current_hour += "0"
    iv = str(k) + current_hour
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
    res = requests.post(SERVER + "/client/login", data=json.dumps(data), headers=headers).json()
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
        self.jump = SERVER

    def ad(self):
        res = requests.get(SERVER + "/server_ad").json()
        self.jump = res['data']['url']
        img_url = requests.get(res['data']['image'])
        img = QImage.fromData(img_url.content)
        self.w.ad1.setPixmap(QPixmap.fromImage(img))
        self.w.ad1.setOpenExternalLinks(True)

    def jump_ad(self, data):
        QDesktopServices.openUrl(QUrl(self.jump))

    def app_update(self):
        """
        检测是否有新版本，有就升级，不然后导致无法使用,无论如何请保留此功能
        重大BUG、安全风险等都会进行升级
        :return:
        """
        res = requests.get(SERVER + "/app_update?server_tag=%s" % SERVER_TAG).json()
        if res['code'] != 0: return
        server_version = res['data']['version']
        update_url = res['data']['update_url']
        update_type = res['data']['type']
        update_message = res['data']['message']
        if int(server_version) > int(SERVER_VERSION):  # 可升级
            if update_type == 1:  # 不向下兼容，必须要升级
                QMessageBox.information(self.w, "发现新版本！版本号：{}".format(server_version), "{}".format(update_message),
                                        QMessageBox.Ok)
                QDesktopServices.openUrl(QUrl(update_url))
                sys.exit()
            else:  # 可选是否升级
                reply = QMessageBox.information(self.w, "发现新版本！", "{}".format(update_message),
                                                QMessageBox.Ok, QMessageBox.No)
                if reply == QMessageBox.Ok:
                    QDesktopServices.openUrl(QUrl(update_url))
                    sys.exit()
                else:
                    # 如果忽略升级
                    pass
        return

    def login(self):
        """
        登陆到服务器
        :return:
        """
        device_id = self.w.device_id.text().strip()
        self.safe_code = self.w.safe_code.text().strip()
        if len(device_id) != 32:
            QMessageBox.critical(self.w, "错误！", "你的设备ID错误！")
            return
        if len(self.safe_code) != 6:
            QMessageBox.critical(self.w, "错误！", "你的安全码错误！")
            return

        try:
            self.input_status(True)
            self.connect_message = 0
            self.w.textBrowser.append(log_info("开始连接服务器..."))
            res = login_to_server(device_id, self.safe_code)
            if res["code"] == 0:
                server = res["data"]["server"]  # this is subscribe server addr
                subscribe = res["data"]["subscribe"]  # this is subscribe topic
                self.subscribe = subscribe
                self.server = server
                self.device_id = device_id
                _thread.start_new_thread(self.connect_server, ())
            else:
                self.w.textBrowser.append(log_error(res["msg"]))
                self.input_status(False)
        except Exception as E:
            print(E)
            self.input_status(False)
            self.w.textBrowser.append(log_error("连接异常，请检查网络后重试！"))

    def mqtt_on_connect(self, client, userdata, flags, rc):
        """与服务端建立连接"""
        if rc == 0:
            client.subscribe('client/{}'.format(self.subscribe), qos=1)
            self.w.textBrowser.append(log_success("连接成功，初始化..."))
            sleep(2)
            self.w.textBrowser.append(log_success("初始化完成！"))
        else:
            self.connect_message += 1
            self.w.textBrowser.append(log_error("掉线重连，第{}次...".format(self.connect_message)))

    def mqtt_on_message(self, client, userdata, msg):
        """服务端下发指令"""
        self.w.textBrowser.append(log_info("服务端下发了指令..."))
        try:
            en_data = str(msg.payload, encoding="utf-8")
            de_data = decrypt(en_data, self.safe_code)
            json_data = json.loads(de_data)
            command_name = json_data['command_name']
            self.w.textBrowser.append(log_info("执行[{}]指令...".format(command_name)))
            Execute(self.w, json_data['command'], json_data['type']).do()
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

    def input_status(self, status):
        """
        按钮及输入框的状态
        :param status:
        :return:
        """
        self.w.login.setDisabled(status)
        self.w.device_id.setDisabled(status)
        self.w.safe_code.setDisabled(status)


class Execute:
    def __init__(self, w, command, command_type):
        self.w = w
        self.command = command
        self.type = command_type

    def do(self):
        """执行脚本"""
        dic = {1: self.open_any,
               2: self.del_any,
               3: self.add_any,
               4: self.kill_any,
               5: self.run_any,
               }
        dic[self.type]()

    def open_any(self):
        """打开文件或程序"""
        try:
            os.startfile(self.command)
            self.w.textBrowser.append(log_success("执行成功！"))
        except Exception as E:
            self.w.textBrowser.append(log_error("执行失败：{}".format(E)))

    def del_any(self):
        """删除文件"""
        try:
            if os.path.isdir(self.command):
                os.rmdir(self.command)
            if os.path.isfile(self.command):
                os.remove(self.command)
            self.w.textBrowser.append(log_success("执行成功！"))
        except Exception as E:
            self.w.textBrowser.append(log_error("执行失败：{}".format(E)))

    def add_any(self):
        """创建文件"""
        try:
            try:
                file = re.findall(r'\.[^.\\/:*?"<>|\r\n]+$', self.command)
                n = file[0]
                with open(self.command, "w") as f:
                    f.write("")
            except:
                os.mkdir(self.command)
            self.w.textBrowser.append(log_success("执行成功！"))
        except Exception as E:
            self.w.textBrowser.append(log_error("执行失败：{}".format(E)))

    def kill_any(self):
        """结束进程"""
        try:
            if os.sep == "/":
                subprocess.Popen("pkill -9 {}".format(self.command), close_fds=True)
            else:
                subprocess.Popen("taskkill /f /im {}".format(self.command), close_fds=True)
            self.w.textBrowser.append(log_success("执行成功！"))
        except Exception as E:
            self.w.textBrowser.append(log_error("执行失败：{}".format(E)))

    def run_any(self):
        """执行任意脚本"""
        try:
            subprocess.Popen("{}".format(self.command), close_fds=True)
            self.w.textBrowser.append(log_success("执行成功！"))
        except Exception as E:
            self.w.textBrowser.append(log_error("执行失败：{}".format(E)))
