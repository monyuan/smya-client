import router from './router'
import Performance from '@/tools/performance'

var end = null
const whiteList = ['/login'] // 不重定向白名单
router.beforeEach(async (to, from, next) => {
  end = Performance.startExecute(`${from.path} => ${to.path} 路由耗时`) /// 路由性能监控
  let token = localStorage.getItem("token")
  console.log(token)
  if (token && token.length > 2) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      console.log("ok2")
      next()
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
      next('/login')
    }
  }

  setTimeout(() => {
    end()
  }, 0)
})

router.afterEach(() => { })