<template>
  <upload-form/>
</template>

<script>
import Vue from 'vue'
import Component from 'vue-class-component'
import UploadForm from '../components/UploadForm'

export default @Component({components: {UploadForm}}) class Main extends Vue {
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
::selection {
  background: #42b983;
  color: #fff;
}
body {
  font-family: 'Source Sans Pro', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: none;
  position: relative;
  height: 100%;
  margin: 0;
  color: #34495e;
  font-size: 16px;
}
@media screen and (max-width: 480px) {
  body {
    font-size: 15px;
  }
}
ol,ul,form,p {
  margin: 0;
}
a {
  text-decoration: none;
  color: #42b983;
  cursor: pointer;
}
p {
  word-spacing: 0.05em;
  line-height: 1.6em;
}
pre {
  overflow-x: auto;
}
blockquote {
    margin: 1em 0;
    padding: 15px 20px;
    border-left: 4px solid #42b983;
    background: #f8f8f8;
    border-bottom-right-radius: 2px;
    border-top-right-radius: 2px;
}
.hljs {
  background: none !important;
}
</style>