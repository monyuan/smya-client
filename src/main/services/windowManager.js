import { BrowserWindow, Menu, Tray, ipcMain,nativeImage  } from 'electron'
import { platform } from "os"
import menuconfig from '../config/menu'
import config from '@config'
import setIpc from './ipcMain'
import { winURL, loadingURL } from '../config/StaticPath'
import path from "path";
import log from "electron-log"

var loadWindow = null
var mainWindow = null
setIpc.Mainfunc(config.IsUseSysTitle)
// console.log(path.join(__dirname, 'static/icon.png'))
function createMainWindow() {
  log.error("33333")
  let timer = null
  let count = 0
  let tray = null
  let icon = path.join(__dirname, 'static/icon.png')
  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    height: 450,
    width: 350,
    show: false,
    icon: icon,
    resizable: false,
    titleBarStyle: platform().includes('win32') ? 'default' : 'hidden',
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
      webSecurity: false,
      skipTaskbar: true,
      transparent: true,
      backgroundColor: '#00000000',
      // 如果是开发模式可以使用devTools
      // devTools: process.env.NODE_ENV === 'development' || config.build.openDevTools,
      devTools: process.env.NODE_ENV === 'development' || config.build.openDevTools,
      // 在macos中启用橡皮动画
      scrollBounce: process.platform === 'darwin',
      preload: path.join(__dirname, "preload.js")
    }
  })

  Menu.buildFromTemplate(menuconfig)
  Menu.setApplicationMenu(null)
  mainWindow.loadURL(winURL)

  mainWindow.webContents.once('dom-ready', () => {
    mainWindow.show()
    if (process.env.NODE_ENV === 'development' || config.build.devTools) mainWindow.webContents.openDevTools(true)
    if (config.UseStartupChart) loadWindow.destroy()
  })


  tray = new Tray(path.join(__dirname, 'static/icon.png'))
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '神秘鸭',
      role: 'redo',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
        }
      }
    },
    { label: '退出神秘鸭', role: 'quit' }
  ])
  tray.setToolTip('微信')
  tray.setContextMenu(contextMenu)

  ipcMain.handle('haveMessage', (event,arg) => {
    timer = setInterval(() => {
      count += 1
      if (count % 2 === 0) {
        tray.setImage(icon)
      } else {
        tray.setImage(nativeImage.createEmpty()) // 创建一个空的nativeImage实例
      }
      tray.setToolTip('来自神秘鸭服务端消息')
    }, 500)
  })

  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide()
    } else {
      mainWindow.show()
      tray.setImage(icon)
      tray.setToolTip('神秘鸭-ORZ实验室')
      clearInterval(timer)
      timer = null
      count = 0
    }
  })

  mainWindow.on('minimize', ev => {
    // 阻止最小化
    ev.preventDefault();
    // 隐藏窗口
    mainWindow.hide();
  });

   // 托盘图标被双击
   tray.on('double-click', () => {
    // 显示窗口
    mainWindow.show();
  });

  mainWindow.on('close', ev => {
    ev.preventDefault();
    mainWindow.hide()
  })
}

function loadingWindow() {
  loadWindow = new BrowserWindow({
    width: 500,
    height: 120,
    frame: false,
    backgroundColor: '#222',
    skipTaskbar: true,
    transparent: true,
    resizable: false,
    webPreferences: { experimentalFeatures: true }
  })

  loadWindow.loadURL(loadingURL)

  loadWindow.show()

  setTimeout(() => {
    createMainWindow()
  }, 2000)

  loadWindow.on('closed', () => {
    loadWindow = null
  })
}

function initWindow() {
  if (config.UseStartupChart) {
    return loadingWindow()
  } else {
    return createMainWindow()
  }
}
export default initWindow
