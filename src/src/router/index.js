import { createRouter, createWebHistory } from 'vue-router'

import Activity from '../views/Activity.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/activities',
      name: 'activities',
        component: Activity
    }
  ]
})

export default router
