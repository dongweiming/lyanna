<template>
  <user-detail :is-edit="false"/>
</template>

<script>
import UserDetail from './components/user-detail.vue'

export default {
  name: 'CreateForm',
  components: { UserDetail }
}
</script>
