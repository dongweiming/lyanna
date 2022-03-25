<template>
  <topic-detail :is-edit="true"/>
</template>

<script>
import TopicDetail from './components/TopicDetail.vue'

export default {
  name: 'EditForm',
  components: { TopicDetail }
}
</script>
