import qs from 'qs'

import request from '@/utils/request'

export function loginReq(data) {
  return request({
    url: '/auth',
    data,
    method: 'post'
   })
}

export function getInfoReq() {
  return request({
    url: '/api/user/info',
    method: 'get',
  })
}

export function logoutReq() {
  return request({
    url: '/api/logout',
    method: 'post'
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

const getTopicList = () => {
    return request({
        url: '/api/topics',
        method: 'get'
    })
}

const updateTopicStatus = (id, method) => {
    return request({
        url: `/api/topic/${id}/status`,
        method: method
    })
}

const createTopic = (data) => {
    return request({
        url: '/api/topic/new',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'post',
        data: qs.stringify(data)
    })
}

const updateTopic = (id, data) => {
    return request({
        url: `/api/topic/${id}`,
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        method: 'put',
        data: qs.stringify(data)
    })
}

const fetchTopic = (id) => {
    return request({
        url: `/api/topic/${id}`,
        method: 'get'
    })
}

const createStatus = (data) => {
  return request({
    url: '/api/status',
    method: 'post',
    data
  })
}

const getUrlInfo = (url) => {
  const data = {
    url
  }
  return request({
    url: '/api/get_url_info',
    method: 'post',
    data
  })
}

const getActivities = (page) => {
    return request({
        url: '/j/activities',
        method: 'get',
        params: {page}
    })
}

const reactActivity = (id, method, reaction_type=2) => {
    const data = {
        reaction_type
    }
    return request({
        url: `/j/activity/${id}/react`,
        headers: {'content-type': 'application/x-www-form-urlencoded'},
        method: method,
        data: qs.stringify(data)
    })
}

const commentActivity = (id, content, ref_id=0) => {
    const data = {
        content, ref_id
    }
    return request({
        url: `/j/activity/${id}/comment`,
        headers: {'content-type': 'application/x-www-form-urlencoded'},
        method: 'post',
        data: qs.stringify(data)
    })
}

const getActivityCommentList = (id) => {
    return request({
        url: `/j/activity/${id}/comments`,
        method: 'get'
    })
}

export {getUserList, createPost,
        getPostList, createUser, updatePost, updatePostStatus, updateUser,
        deletePost, fetchUser, fetchPost, userSearch, fetchTags,
        getTopicList, updateTopicStatus, createTopic, updateTopic,
        fetchTopic, createStatus, getUrlInfo, getActivities, reactActivity,
        commentActivity, getActivityCommentList}
