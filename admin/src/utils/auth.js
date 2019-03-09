import Cookies from 'js-cookie'

const TokenKey = 'Lyanna-Token'
const oneHour = 1/24;


export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
    return Cookies.set(TokenKey, token, {
        expires: oneHour})
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}
