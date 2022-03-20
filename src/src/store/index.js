import { createStore } from 'vuex'

import app from './modules/app'
import user from './modules/user'
import getters from './getters'
import tagsView from './modules/tagsView'

const store = createStore({
    modules: {
        app,
        user,
        tagsView
    },
    getters
})

export default store
