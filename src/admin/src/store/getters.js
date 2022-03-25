const getters = {
  device: (state) => state.app.device,
  cachedViews: (state) => state.app.cachedViews,
  token: state => state.user.token,
  avatar: state => state.user.avatar,
  name: state => state.user.name
}
export default getters
