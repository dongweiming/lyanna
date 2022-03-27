<template>
  <topic-detail :is-edit="true"/>
</template>

<script>
import TopicDetail from './components/topic-detail.vue'

export default {
  name: 'EditForm',
  components: { TopicDetail }
}
</script>
