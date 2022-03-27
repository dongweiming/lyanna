<template>
  <user-detail :is-edit="true"/>
</template>

<script>
import UserDetail from './components/user-detail.vue'

export default {
  name: 'EditForm',
  components: { UserDetail }
}
</script>
