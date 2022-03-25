<template>
  <div class="app-main" :class="{ 'show-tag-view': settings.showTagsView }">
    <router-view v-slot="{ Component }">
      <!--has transition  Judging by settings.mainNeedAnimation-->
      <transition v-if="settings.mainNeedAnimation" mode="out-in" name="fade-transform">
        <!--  根据路由的name进行的缓存       -->
        <keep-alive :include="cachedViews">
          <component :is="Component" :key="key" />
        </keep-alive>
      </transition>
      <!-- no transition -->
      <keep-alive v-else :include="cachedViews">
        <component :is="Component" :key="key" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
let store = useStore()
let route = useRoute()
let settings = computed(() => {
  return store.state.app.settings
})

const key = computed(() => route.path)

//从vuex 取cachedViews
const cachedViews = computed(() => {
  return store.state.app.cachedViews
})

/*listen the component name changing, then to keep-alive the page*/

// cachePage: is true, keep-alive this Page
// leaveRmCachePage: is true, keep-alive remote when page leave

//保存的是上一次访问的路由信息
let oldRoute = null

//三级路由的上一级的父元素的路由信息
let deepOldRouter = null

//移除二级路由下的三级的children的vuex
const removeDeepChildren = (deepOldRouter) => {
  deepOldRouter.children?.forEach((fItem) => {
    store.commit('app/M_DEL_CACHED_VIEW_DEEP', fItem.name)
  })
}

watch(
  () => route.name,
  () => {
    //判断几级路由
    const routerLevel = route.matched.length
    //二级路由处理
    if (routerLevel === 2) {
      /*移除缓存*/
      if (deepOldRouter?.name) {
        //三级路由->二级路由
        if (deepOldRouter.meta?.leaveRmCachePage && deepOldRouter.meta?.cachePage) {
          store.commit('app/M_DEL_CACHED_VIEW', deepOldRouter.name)
          //remove the deepOldRouter‘s children component
          removeDeepChildren(deepOldRouter)
        }
      } else {
        //二级路由->二级路由
        if (oldRoute?.name) {
          if (oldRoute.meta?.leaveRmCachePage && oldRoute.meta?.cachePage) {
            store.commit('app/M_DEL_CACHED_VIEW', oldRoute.name)
          }
        }
      }

      /*添加缓存*/
      if (route.name) {
        //添加二级路由
        if (route.meta?.cachePage) {
          store.commit('app/M_ADD_CACHED_VIEW', route.name)
        }
      }
      deepOldRouter = null
    }

    //三级理由处理
    if (routerLevel === 3) {
      //三级路由->三级路由
      //如果路由等级为3级处理流程
      //三级时存储当前路由对象的上一级
      /*移除缓存*/
      //二级路由
      const parentRoute = route.matched[1]
      //deepOldRouter不为空，且deepOldRouter不是当前路由的父对象，则需要清除deepOldRouter缓存
      //一般为三级路由跳转三级路由的情况
      //不同父级
      if (deepOldRouter?.name && deepOldRouter.name !== parentRoute.name) {
        //不同二级之间的三级跳转
        //三级路由->三级级路由
        if (deepOldRouter.meta?.leaveRmCachePage && deepOldRouter.meta?.cachePage) {
          store.commit('app/M_DEL_CACHED_VIEW', deepOldRouter.name)
          //remove the deepOldRouter‘s children component
          removeDeepChildren(deepOldRouter)
        }
      } else {
        //同一 二级之间的三级跳转
        //三级路由->二级路由
        //否则走正常两级路由处理流程
        //同一父级
        if (oldRoute?.name) {
          if (oldRoute.meta?.leaveRmCachePage && oldRoute.meta?.cachePage) {
            store.commit('app/M_DEL_CACHED_VIEW_DEEP', oldRoute.name)
          }
        }
      }

      /*添加缓存*/
      if (route.name) {
        //route.name&&route.name.cachePage
        if (route.meta?.cachePage) {
          //保存之前的三级路由
          deepOldRouter = parentRoute
          //取的是第二级的name和第三级的name进行缓存
          store.commit('app/M_ADD_CACHED_VIEW', deepOldRouter.name)
          //添加三级路由
          store.commit('app/M_ADD_CACHED_VIEW_DEEP', route.name)
        }
      }
    }
    //保存之前的二级路由
    oldRoute = JSON.parse(JSON.stringify({ name: route.name, meta: route.meta }))
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.app-main {
  padding: $appMainPadding;
  /*50 = navbar  */
  position: relative;
  overflow: hidden;
}
.show-tag-view {
  height: calc(100vh - #{$navBarHeight} - #{$tagViewHeight}) !important;
}
.fixed-header + .app-main {
  padding-top: 50px;
}
</style>

<style lang="scss">
.el-popup-parent--hidden {
  .fixed-header {
    padding-right: 15px;
  }
}
</style>
