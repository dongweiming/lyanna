import { createApp } from 'vue'
import App from './App.vue'
const app = createApp(App)
import router from './router'
import '@/styles/index.scss' // global css
import '@/styles/detail.scss'
//import vuex
import store from './store'
app.use(store)

/*on demand element-plus look for app.vue and vite.config.js */
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
app.use(ElementPlus, { size: 'default', locale: zhCn })

//global mixin(can choose by you need )
// import elementMixin from '@/mixins/elementMixin'
// app.mixin(elementMixin)
// import commonMixin from '@/mixins/commonMixin'
// app.mixin(commonMixin)
// import routerMixin from '@/mixins/routerMixin'
// app.mixin(routerMixin)

//svg-icon
//import svg-icon doc in  https://github.com/anncwb/vite-plugin-svg-icons/blob/main/README.zh_CN.md
import 'virtual:svg-icons-register'
import svgIcon from '@/icons/SvgIcon.vue'
app.component('SvgIcon', svgIcon)


//element svg icon
import ElSvgIcon from "@/components/ElSvgIcon.vue"
app.component("ElSvgIcon",ElSvgIcon)

// import $momentMini from 'moment-mini'
// app.config.globalProperties.$momentMini = $momentMini


//global mount moment-mini
// import $momentMini from 'moment-mini'
// app.config.globalProperties.$momentMini = $momentMini

app.use(router).mount('#app')
