import Vue from 'vue'
import VueRouter from 'vue-router'
import Main from '../views/Main.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'main',
    component: Main
  }
]

const router = new VueRouter({
    mode: 'history',
    base: '/activities',
    routes: routes
})

export default router
