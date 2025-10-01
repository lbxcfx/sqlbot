// import { ElMessage } from 'element-plus-secondary'
import { useCache } from '@/utils/useCache'
import { useAppearanceStoreWithOut } from '@/stores/appearance'
import { useUserStore } from '@/stores/user'
// import { request } from '@/utils/request'
import type { Router } from 'vue-router'

const appearanceStore = useAppearanceStoreWithOut()
const userStore = useUserStore()
const { wsCache } = useCache()
const whiteList = ['/login']
const assistantWhiteList = ['/assistant', '/embeddedPage', '/401']
export const watchRouter = (router: Router) => {
  router.beforeEach(async (to: any, from: any, next: any) => {
    // 开源版本：绕过 license 验证
    try {
      await loadXpackStatic()
      await appearanceStore.setAppearance()
      if (typeof LicenseGenerator !== 'undefined') {
        LicenseGenerator.generateRouters(router)
      }
    } catch (error) {
      // 开源版本：静默处理XPack功能不可用的情况
      // console.warn('XPack features not available, continuing with open source mode:', error)
    }
    if (to.path.startsWith('/login') && userStore.getUid) {
      next('/')
      return
    }
    if (assistantWhiteList.includes(to.path)) {
      next()
      return
    }
    const token = wsCache.get('user.token')
    if (whiteList.includes(to.path)) {
      next()
      return
    }
    if (!token) {
      // ElMessage.error('Please login first')
      next('/login')
      return
    }
    if (!userStore.getUid) {
      await userStore.info()
    }
    if (to.path === '/' || accessCrossPermission(to)) {
      next('/chat')
      return
    }
    if (to.path === '/login') {
      console.info(from)
      next('/chat')
    } else {
      next()
    }
  })
}

const accessCrossPermission = (to: any) => {
  if (!to?.path) return false
  return (
    (to.path.startsWith('/system') && !userStore.isAdmin) ||
    (to.path.startsWith('/set') && !userStore.isSpaceAdmin)
  )
}
const loadXpackStatic = () => {
  // 开源版本：直接返回成功，不加载XPack脚本
  return Promise.resolve()
}
