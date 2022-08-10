let ver = "0.1"

localStorage.setItem("os", process.platform)
localStorage.setItem("ver", ver)

import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import Store from 'electron-store'
// 引用element
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import './permission'
// 日志
import './error'
import './icons'
import '@/styles/index.scss'
import '@/styles/dark-mode.scss'

// 引入 i18n 语言包
import VueI18n from 'vue-i18n'
import loadLanguage from "./i18n"
const languages = loadLanguage()

import {
	ipcRenderer
} from 'electron'
import {
	ebtRenderer
} from 'electron-baidu-tongji'
const BAIDU_SITE_ID = 'd1bfbcb101d1ae6e390cc32d4896ece9'

//本地数据存储
const localData = new Store()
Vue.prototype.$local = localData
Vue.use(localData)
if (!process.env.IS_WEB) {
	if (!require('../../config').IsUseSysTitle) {
		require('@/styles/custom-title.scss')
	}
}

// 创建 i18n
Vue.use(VueI18n) // 新版本必须要这个，不知道为什么
const i18n = new VueI18n({
	locale: 'zh-CN', // 设置默认语言
	messages: languages, // 设置语言包
});

Vue.use(ElementUI, {
	i18n: (key, value) => i18n.t(key, value)
})

Vue.config.productionTip = false
/* eslint-disable no-new */
ebtRenderer(ipcRenderer, BAIDU_SITE_ID, router)
const vue = new Vue({
	components: {
		App
	},
	router,
	store,
	i18n,
	template: '<App/>'
}).$mount('#app')

export default vue
