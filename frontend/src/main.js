import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 在挂载前验证用户身份
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()

console.log('开始初始化用户认证...')
console.log('Token:', userStore.token ? '存在' : '不存在')

userStore.initAuth().then(() => {
  console.log('用户认证初始化完成')
  console.log('登录状态:', userStore.isLoggedIn)
  console.log('用户信息:', userStore.userInfo)
}).finally(() => {
  app.mount('#app')
})
