<template>
  <div class="dashboard-container">
    <div class="dashboard-text">Welcome: {{ username }}</div>
  </div>
</template>

<script setup>
import { getUser } from '@/utils/auth'
let store = useStore()
const username = computed(() => {
  name = store.state.user.name || ''
  if (name) {
    return name
  }
  let user = getUser() || ''
  if (user) {
    return user.name
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    //margin: 30px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
}
</style>
