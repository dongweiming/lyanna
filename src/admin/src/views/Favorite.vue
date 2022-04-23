<template>
  <div class="createFavorite-container">
    <el-form ref="favoriteForm" :model="favoriteForm" :rules="rules" class="form-container">

      <sticky class-name='sub-navbar draft'>
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">更新</el-button>
      </sticky>

      <div class="createFavorite-main-container">
        <el-form-item label="Type" prop="type">
          <el-select v-model="favoriteForm.type" class="m-2" placeholder="Select" size="large" @change="changeType">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="IDS" prop="ids">
          <el-input
            v-model="favoriteForm.ids"
            :rows="5"
            type="textarea"
            placeholder="Please input douban subject ids. Use commas to separate (don't use Chinese commas)"
          />
        </el-form-item>
      </div>
    </el-form>

  </div>
</template>

<script>
import Dropdown from '@/components/Dropdown/index.vue'
import Sticky from '@/components/Sticky/index.vue'
import { updateFavorite, getFavoriteData } from '@/api'

const defaultForm = {
    type: 'movie',
    ids: '',
}

const options = [
  {
    value: 'movie',
    label: 'Movie',
  },
  {
    value: 'book',
    label: 'Book',
  },
  {
    value: 'game',
    label: 'Game',
  }
]

export default {
  name: 'Favorite',
  components: { Sticky, Dropdown },
  data() {
    const validateRequire = (rule, value, callback) => {
      if (value === '') {
        this.$message({
          message: rule.field + '为必传项',
          type: 'error'
        })
        callback(new Error(rule.field + '为必传项'))
      } else {
        callback()
      }
    }

    return {
      loading: false,
      favoriteForm: Object.assign({}, defaultForm),
      rules: {
        type: [{ validator: validateRequire }],
        ids: [{ validator: validateRequire }]
      },
      dataMap: {
        'movie': '',
        'book': '',
        'game': ''
      },
      options: options,
      tempRoute: {}
    }
  },
  created() {
    this.tempRoute = Object.assign({}, this.$route)
    getFavoriteData().then(response => {
        this.dataMap = response.data.data
        this.favoriteForm.ids = this.dataMap[this.favoriteForm.type]
      })
  },
  methods: {
    setTagsViewTitle() {
      const title = '编辑收藏'
      const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.type}` })
      this.$store.dispatch('updateVisitedView', route)
    },
    changeType(val) {
      this.favoriteForm.ids = this.dataMap[val]
    },
    submitForm() {
      this.$refs.favoriteForm.validate((valid, fields) => {
        if (valid) {
          this.loading = true
          let self = this;
          let data = Object.assign({}, this.favoriteForm)
          updateFavorite(data).then(() => {
            self.$notify({
              title: '成功',
              message: '发布成功',
              type: 'success',
              duration: 2000
            })
            this.loading = false
          }).catch(err => {
            console.log(err)
          })
        } else {
          console.log('error submit!', fields)
          return false
        }
      })
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "@/styles/mixin.scss";
.createFavorite-container {
  position: relative;
  padding: 20px;
}
.m-2 {
    margin: 20px 0 20px 0;
}
</style>