import Vue from 'vue'
import Toasted from 'vue-toasted'
import VuePlyr from 'vue-plyr'

import App from './App.vue'
import router from './router'
import store from './store'

import '../../static/css/pure-min.css'
import '../../static/css/base.css'
import '../../static/css/iconfont.css'

Vue.config.productionTip = false
Vue.use(Toasted, {duration: 3000})
Vue.use(VuePlyr, {
  plyr: {
    captions: {
      defaultActive: false
    },
    controls: ["play", "progress", "current-time", "duration", "mute", "volume", "fullscreen"]
  }
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
