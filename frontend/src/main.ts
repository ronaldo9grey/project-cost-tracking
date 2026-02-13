import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

console.log('🔧 开始创建Vue应用...')

const app = createApp(App)
const pinia = createPinia()

console.log('🔧 注册插件...')
app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

console.log('🔧 挂载应用...')
app.mount('#app')

console.log('✅ Vue应用挂载完成')