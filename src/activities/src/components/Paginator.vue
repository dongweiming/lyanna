<template>
  <div class="paginator">
    <span class="prev">
      <a :href="'?p=' + (page - 1)" v-if="page != 1">&lt;前页</a><span v-else>&lt;前页</span>
    </span>
    <div v-for="(p, index) in pages" :key="index" class="paginator-item">
      <a :href="'?p=' + p" v-if="page != p">{{ p }}</a>
      <span class="current" v-else>{{ p }}</span>
    </div>
    <span class="break" v-if="maxPage > 5">...</span>
    <span class="next">
        <a :href="'?p=' + (page + 1)" v-if="page != maxPage">后页&gt;</a><span v-else>后页&gt;</span>
    </span>
  </div>
</template>
<script setup>
import { ref, computed, defineProps } from 'vue'

const props = defineProps({
    page: Number,
    total: Number
})

const perPage = 10
const maxPage = computed(() => {
    get: () => {
        Math.ceil(this.total / this.perPage.value)
    }
})

const pages = computed(() => {
    get: () => {
        [...Array(this.maxPage.value).keys()].map(i => i + 1)
    }
})
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
.paginator {
  width: 675px;
  zoom: 1;
  font: 14px Arial, Helvetica, sans-serif;
  color: #aaa;
  margin: 20px 0;
  line-height: 150%;
  text-align: center;
    .paginator-item {
        display: inline-block;
    }
  a, .current, .break {
    padding: 0px 4px;
    margin: 2px;
  }
  .prev {
    margin-right: 20px;
  }
  .current {
    color: #fff;
    background: #7094b7;
  }
  .next {
    margin-left: 20px;
  }
  a:hover {
    color: #fff;
    text-decoration: none;
    background: #7094b7;
  }
}
</style>
