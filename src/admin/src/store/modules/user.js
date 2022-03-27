import { loginReq, logoutReq, getInfoReq } from '@/api'
import { setToken, getToken, removeToken, setUser, removeUser } from '@/utils/auth'

import router, { constantRoutes, asyncRoutes } from '@/router'

//当路由被删除时，所有的别名和子路由也会被同时删除
//https://router.vuejs.org/zh/guide/advanced/dynamic-routing.html#%E5%88%A0%E9%99%A4%E8%B7%AF%E7%94%B1
const resetRouter = () => {
  let asyncRouterNameArr = asyncRoutes.map((mItem) => mItem.name)
  asyncRouterNameArr.forEach((name) => {
    if (router.hasRoute(name)) {
      router.removeRoute(name)
    }
  })
}

const getDefaultState = () => {
  return {
    token: getToken(),
    username: '',
    avatar: '',
    roles: []
  }
}

const state = getDefaultState()

const mutations = {
  M_username: (state, username) => {
    state.username = username
  },
  M_roles: (state, roles) => {
    state.roles = roles
  },
    SET_TOKEN: (state, token) => {
      state.token = token
    },
    SET_NAME: (state, name) => {
      state.name = name
    },
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar
    }
}

const actions = {
  // user login
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  login({ commit }, data) {
    return new Promise((resolve, reject) => {
        loginReq(data)
            .then((res) => {
              if (res.data.access_token) {
                commit('SET_TOKEN', res.data.access_token)
                setToken(res.data.access_token)
                resolve()
            } else {
                reject(res)
            }
            })
            .catch((error) => {
          reject(error)
        })
    })
  },
  // get user info
  getInfo({ commit }) {
    return new Promise((resolve, reject) => {
      getInfoReq()
        .then((response) => {
          const { data } = response
          if (!data) {
            return reject('Verification failed, please Login again.')
          }
          //此处模拟数据
          const rolesArr = localStorage.getItem('roles')
          if (rolesArr) {
            data.roles = JSON.parse(rolesArr)
          } else {
            data.roles = ['admin']
            localStorage.setItem('roles', JSON.stringify(data.roles))
          }
          const { roles, username } = data
          commit('M_username', username)
          commit('M_roles', roles)
          commit('SET_NAME', data.name)
          commit('SET_AVATAR', data.avatar)
          setUser(data)
          resolve(data)
        })
        .catch((error) => {
          reject(error)
        })
    })
  },
  // user logout
  logout({ dispatch }) {
    return new Promise((resolve, reject) => {
      logoutReq()
        .then(() => {
          dispatch('resetState')
          resolve()
        })
        .catch((error) => {
          reject(error)
        })
    })
  },
  resetState({ commit, dispatch }) {
    return new Promise((resolve) => {
      commit('M_username', '')
      commit('M_roles', [])
      removeToken() // must remove  token  first
      resetRouter() // reset the router
      removeUser()

      // reset visited views and cached views
      dispatch('tagsView/delAllViews', null, { root: true })
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
