import { createApp } from 'vue'
import { createStore } from 'vuex'
import Toast from "vue-toastification";
import VuePlyr from 'vue-plyr'
import "vue-toastification/dist/index.css";

import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)

app.use(router)
app.use(store)
app.use(Toast)
app.use(VuePlyr, {
    plyr: {
        captions: {
            defaultActive: false
        },
        controls: ["play", "progress", "current-time", "duration", "mute", "volume", "fullscreen"]
    }
})

app.mount('#app')
