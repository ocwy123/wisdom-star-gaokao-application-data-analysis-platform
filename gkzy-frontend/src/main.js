import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
<<<<<<< HEAD
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.use(router)  // 注册路由
app.use(ElementPlus)  // 注册 Element Plus
app.mount('#app')
=======

const app = createApp(App)
app.use(router)  // 注册路由

app.mount('#app')
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
