import qs from 'qs'
import request from '@/utils/request'

const loginByUsername = (username, password) => {
  const data = {
    username,
    password
  }
  return request({
    url: '/auth',
    method: 'post',
    data
  })
}

const getUserInfo = (token) => {
    return request({
        url: '/api/user/info',
        method: 'get',
        params: { token }
    })
}

const getPostList = (params) => {
  return request({
    url: '/api/posts',
    method: 'get',
    params: params
  })
}

const createPost = (data) => {
    return request({
        url: '/api/post/new',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'post',
        data: qs.stringify(data, { indices: false })
    })
}

const getUserList = () => {
    return request({
        url: '/api/users',
        method: 'get'
    })
}

const createUser = (data) => {
    return request({
        url: '/api/user/new',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'post',
        data: qs.stringify(data)
    })
}

const updatePost = (id, data) => {
    return request({
        url: `/api/post/${id}`,
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'put',
        data: qs.stringify(data, { indices: false })
    })
}

const updateUser = (id, data) => {
    return request({
        url: `/api/user/${id}`,
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'put',
        data: qs.stringify(data, { indices: false })
    })
}

const getProfile = () => {
    return request({
        url: '/api/profile',
        method: 'get'
    })
}

const updateProfile = (data) => {
    return request({
        url: '/api/profile',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'put',
        data: qs.stringify(data)
    })
}

const updatePostStatus = (id, method) => {
    return request({
        url: `/api/post/${id}/status`,
        method: method
    })
}

const deletePost = (id) => {
    return request({
        url: `/api/post/${id}`,
        method: 'delete'
    })
}

const fetchUser = (id) => {
    return request({
        url: `/api/user/${id}`,
        method: 'get'
    })
}

const fetchPost = (id) => {
  return request({
    url: `/api/post/${id}`,
    method: 'get'
  })
}

const userSearch = (name) => {
    return request({
        url: '/api/user/search',
        method: 'get',
        params: { name }
    })
}

const fetchTags = () => {
    return request({
        url: '/api/tags',
        method: 'get'
    })
}

export {loginByUsername, getUserInfo, getUserList, createPost, getProfile,
        getPostList, createUser, updatePost, updatePostStatus, updateUser,
        updateProfile, deletePost, fetchUser, fetchPost, userSearch, fetchTags}
