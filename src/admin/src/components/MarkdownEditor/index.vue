<template>
  <div id="editor">
    <textarea v-model="value" @input="update" v-bind:style="{ height: editorHeight}" @keyup="$emit('update:value', value);"></textarea>
    <div v-html="compiledMarkdown"></div>
  </div>
</template>

<script>
// import _ from 'lodash'
import marked from 'marked'
import debounce from 'lodash/debounce'

export default {
  name: 'MarddownEditor',
  emits: ['update:value'],
  props: {
    value: {
      type: String,
      default: ''
    },
    height: {
      type: String,
      required: false,
      default: '300px'
    }
  },
  computed: {
    compiledMarkdown() {
      return marked(this.value)
    },
    editorHeight() {
      return this.height
    },
  },
  methods: {
    update() {
      debounce((e) => {
        this.value = e.target.value
      }, 300)
    }
  }
}
</script>
<style>
#editor {
  margin: 0;
  color: #333;
}

textarea, #editor div {
  display: inline-block;
  width: 49%;
  height: 100%;
  vertical-align: top;
  box-sizing: border-box;
  padding: 0 20px;
}

textarea {
  border: none;
  resize: none;
  outline: none;
  background-color: #f6f6f6;
  font-size: 14px;
  font-family: 'Monaco', courier, monospace;
  padding: 20px;
}

code {
  color: #f66;
}
</style>
