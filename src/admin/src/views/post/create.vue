<template>
  <post-detail :is-edit="false"/>
</template>

<script>
import PostDetail from './components/PostDetail.vue'

export default {
  name: 'CreatePost',
  components: { PostDetail }
}
</script>
