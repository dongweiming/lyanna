import Vue from 'vue'
import Vuex from 'vuex'

import app from './modules/app'
import user from './modules/user'
import getters from './getters'
import tagsView from './modules/tagsView'

Vue.use(Vuex)

const store = new Vuex.Store({
    modules: {
        app,
        user,
        tagsView
    },
    getters
})

export default store
