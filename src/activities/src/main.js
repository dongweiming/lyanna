import { createApp } from 'vue'

import Toast from "vue-toastification"
import VuePlyr from 'vue-plyr'
import VueUploadComponent from 'vue-upload-component'
import "vue-toastification/dist/index.css"
import 'vue-plyr/dist/vue-plyr.css'

import router from './router'
import App from './App.vue'
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
app.component('file-upload', VueUploadComponent)

app.mount('#app')
