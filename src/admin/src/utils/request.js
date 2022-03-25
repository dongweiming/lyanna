import axios from 'axios'
import store from '@/store'
import router from '@/router'
import { getToken } from './auth'

// create an axios instance
const service = axios.create({
  baseURL: import.meta.env.BASE_URL,
  timeout: 5000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // Do something before request is sent
    if (store.getters.token) {
      config.headers['authorization'] = `Bearer ${getToken()}`
    }
    return config
  },
  error => {
    // Do something with request error
    console.log(error) // for debug
    Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
    response => response,
    error => {
        console.log('err' + error)
        if (error.message === "Request failed with status code 401") {
            store.dispatch('user/resetState').then(() => {
                router.push({ path: '/login' })
            })
        }
        return Promise.reject(error)
    }
)

export default service
