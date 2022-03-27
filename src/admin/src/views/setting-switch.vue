<template>
  <div class="scroll-y">
    <h3 class="mb-2">props operate demo of settings.js</h3>
    <div class="rowSS">
      <div class="mb-1">
        page layout related
        <div class="mt-2">
          sidebarLogo：
          <el-switch v-model="store.state.app.settings.sidebarLogo" />
        </div>
        <div class="mt-3">
          ShowDropDown：
          <el-switch v-model="store.state.app.settings.ShowDropDown" />
        </div>
        <div class="mt-3">
          showHamburger：
          <el-switch v-model="store.state.app.settings.showHamburger" />
        </div>
        <div class="mt-3">
          showLeftMenu：
          <el-switch v-model="store.state.app.settings.showLeftMenu" />
        </div>
        <div class="mt-3">
          showTagsView：
          <el-switch v-model="store.state.app.settings.showTagsView" />
        </div>
        <div class="mt-3">
          showTopNavbar：
          <el-switch v-model="store.state.app.settings.showTopNavbar" />
        </div>
      </div>

      <div class="mb-1 ml-6">
        page animation related
        <div class="mt-2">
          mainNeedAnimation：places to "settings file" for setting
          <!-- <el-switch v-model="store.state.app.settings.mainNeedAnimation" />-->
        </div>
        <div class="mt-3">
          isNeedNprogress：
          <el-switch v-model="store.state.app.settings.isNeedNprogress" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// import { computed, getCurrentInstance, ref } from 'vue'
// import { useStore } from 'vuex'
const store = useStore()
let settings = computed(() => {
  return store.state.app.settings || {}
})

let source = ref(false)
const sourceFun = () => {
  source.value = !source.value
}

const handle = () => {
  new Promise((resolve, reject) => {
    reject('reject promise')
  }).then((res) => {
    console.log('ok')
  })
}

let flag = ref(null)

const consoleErrorFun = () => {
  console.error('console.error')
}

const normalError = () => {
  throw new Error(' throw new Error("")\n')
}
</script>

<style scoped lang="scss"></style>
