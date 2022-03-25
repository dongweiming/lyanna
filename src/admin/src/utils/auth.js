//to fix js-token issue for electron so replace js-cookie to localStorage
const TokenKey = 'Admin-Token'
const userNameKey = 'Username-Token'
const userAvatarKey = 'UserAvatarToken'

export function getToken() {
  return localStorage.getItem(TokenKey)
}

export function setToken(token) {
  return localStorage.setItem(TokenKey, token)
}

export function removeToken() {
  return localStorage.removeItem(TokenKey)
}

export function getUser() {
  return {
    name: localStorage.getItem(userNameKey),
    avatar: localStorage.getItem(userAvatarKey),
  }
}

export function setUser(data) {
  localStorage.setItem(userNameKey, data.name)
  localStorage.setItem(userAvatarKey, data.avatar)
}

export function removeUser() {
  localStorage.removeItem(userNameKey)
  localStorage.removeItem(userAvatarKey)
}
