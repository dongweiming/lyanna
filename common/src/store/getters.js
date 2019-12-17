const getters = {
    token: state => state.user.token,
    avatar: state => state.user.avatar,
    name: state => state.user.name,
    sidebar: state => state.app.sidebar,
    device: state => state.app.device,
    visitedViews: state => state.tagsView.visitedViews,
    cachedViews: state => state.tagsView.cachedViews,
    size: state => state.app.size,
}

export default getters
