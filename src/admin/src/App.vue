<template>
  <router-view />
</template>
<script setup>
// import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { setToken } from '@/utils/auth'
const store = useStore()
let settings = computed(() => {
  return store.state.app.settings
})
onBeforeMount(() => {
  //set tmp token when setting isNeedLogin false
  if (!settings.value.isNeedLogin) setToken(settings.value.tmpToken)
})
</script>
