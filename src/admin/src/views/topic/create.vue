<template>
  <topic-detail :is-edit="false"/>
</template>

<script>
import TopicDetail from './components/TopicDetail.vue'

export default {
  name: 'CreateForm',
  components: { TopicDetail }
}
</script>
