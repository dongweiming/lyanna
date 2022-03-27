<template>
  <post-detail :is-edit="true"/>
</template>

<script>
import PostDetail from './components/post-detail.vue'

export default {
  name: 'EditPostForm',
  components: { PostDetail }
}
</script>
