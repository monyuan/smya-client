import { BrowserWindow, Menu, app } from 'electron'
import { platform } from "os"
import menuconfig from '../config/menu'
import config from '@config'
import setIpc from './ipcMain'
import { winURL, loadingURL } from '../config/StaticPath'
import path from "path";
var loadWindow = null
var mainWindow = null
setIpc.Mainfunc(config.IsUseSysTitle)
console.log(path.join(__dirname, "preload.js"))
function createMainWindow() {
  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    height: 450,
    width: 350,
    show: false,
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
      devTools: process.env.NODE_ENV === 'development' || config.build.openDevTools,
      // 在macos中启用橡皮动画
      scrollBounce: process.platform === 'darwin',
      preload: path.join(__dirname, "preload.js")
    }
  })
  // 这里设置只有开发环境才注入显示开发者模式
  // if (process.env.NODE_ENV === 'development' || config.build.openDevTools) {
  //   menuconfig.push({
  //     label: '开发者设置',
  //     submenu: [{
  //       label: '切换到开发者模式',
  //       accelerator: 'CmdOrCtrl+I',
  //       role: 'toggledevtools'
  //     }]
  //   })
  // }
  // 载入菜单
  Menu.buildFromTemplate(menuconfig)
  Menu.setApplicationMenu(null)
  mainWindow.loadURL(winURL)

  mainWindow.webContents.once('dom-ready', () => {
    mainWindow.show()
    if (process.env.NODE_ENV === 'development' || config.build.devTools) mainWindow.webContents.openDevTools(true)
    if (config.UseStartupChart) loadWindow.destroy()
  })
  mainWindow.on('maximize', () => {
    mainWindow.webContents.send("w-max", true)
  })
  mainWindow.on('unmaximize', () => {
    mainWindow.webContents.send("w-max", false)
  })
  mainWindow.on('closed', () => {
    mainWindow = null
    app.quit();
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
