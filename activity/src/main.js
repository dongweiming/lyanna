import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import '../../static/css/pure-min.css'
import '../../static/css/base.css'
import '../../static/css/iconfont.css'

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
