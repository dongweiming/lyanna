<template>
  <topic-detail :is-edit="false"/>
</template>

<script>
import TopicDetail from './components/topic-detail.vue'

export default {
  name: 'CreateForm',
  components: { TopicDetail }
}
</script>
