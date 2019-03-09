<template>
  <post-detail :is-edit="true"/>
</template>

<script>
import PostDetail from './components/PostDetail'

export default {
  name: 'EditPostForm',
  components: { PostDetail }
}
</script>
