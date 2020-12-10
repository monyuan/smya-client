# 如何自行编译

安装 python 3.6+

```
https://npm.taobao.org/mirrors/python/3.7.0/python-3.7.0a4-amd64.exe
```

克隆此代码
```
git clone https://github.com/monyuan/smya-client.git

或是直接下载解压
https://github.com/monyuan/smya-client/archive/main.zip

```

安装依赖

```
pip install pyqt5 -i https://pypi.douban.com/simple
pip install pydes -i https://pypi.douban.com/simple
pip install rquests -i https://pypi.douban.com/simple
pip install paho-mqtt -i https://pypi.douban.com/simple
pip install pyinstaller -i https://pypi.douban.com/simple

```

打包

```
进入 smya-client 目录

pyinstaller --clean -y -w -i icon.ico --add-data "img;img" --add-data "icon.ico;./" SmyaService.py
```

运行

```
打包完成后，进入dist/SmyaService目录
运行 SmyaService.exe 即可
```