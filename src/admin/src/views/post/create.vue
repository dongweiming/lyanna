<template>
  <post-detail :is-edit="false"/>
</template>

<script>
import PostDetail from './components/post-detail.vue'

export default {
  name: 'CreatePost',
  components: { PostDetail }
}
</script>
