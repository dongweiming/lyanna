<template>
  <div class="createFavorite-container">
    <el-form ref="favoriteForm" :model="favoriteForm" :rules="rules" class="form-container">

      <sticky class-name='sub-navbar draft'>
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">更新</el-button>
      </sticky>

      <div class="createFavorite-main-container">
        <el-form-item label="" prop="type">
          <label for="type" class="el-form-item__label type-label">Type</label>
          <el-select v-model="favoriteForm.type" class="m-2" placeholder="Select" size="large" @change="changeType">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>

          <el-button type="primary" class="btn-add" @click="add">Add</el-button>
        </el-form-item>
      </div>
    </el-form>
    <div class="app-container">
            <el-table v-loading="loading" :data="favoriteForm.items" border fit highlight-current-row style="width: 100%">
              <el-table-column align="center" label="ID" width="80">
                <template #default="scope">
                  <span>{{ scope.row.id }}</span>
                </template>
              </el-table-column>

              <el-table-column width="180px" align="center" label="Title">
                <template #default="scope">
                  <span v-if="scope.row.url" class="subject-link"><a :href="scope.row.url" target="_blank">{{ scope.row.title }}</a></span>
                  <span v-else>{{ scope.row.title }}</span>
                </template>
              </el-table-column>

              <el-table-column width="180px" align="center" label="Rating">
                <template #default="scope">
                  <span><el-rate v-model="scope.row.rating" allow-half disabled /></span>
                </template>
              </el-table-column>

              <el-table-column align="center" label="Comment">
                <template #default="scope">
                  <span>{{ scope.row.comment }}</span>
                </template>
              </el-table-column>

              <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="edit(scope.row)"><svg-icon icon-class="edit"/>Edit</el-button>
                </template>
              </el-table-column>
            </el-table>
      </div>


    <el-dialog
      v-model="dialogVisible"
      title="Favorite"
      width="30%"
      :before-close="handleClose"
    >

      <el-form
      ref="dialogFormRef"
      :model="dialog"
      status-icon
      label-width="120px"
      class="dialogForm"
    >
        <el-form-item label="ID" prop="id">
          <el-input v-model="dialog.id" placeholder="Please input" />
        </el-form-item>
        <el-form-item label="Title" prop="title">
          <el-input v-model="dialog.title" placeholder="Please input" />
        </el-form-item>
        <el-form-item label="Comment" prop="comment">
          <el-input v-model="dialog.comment" :rows="3" type="textarea" placeholder="Please input"/>
        </el-form-item>
        <el-form-item label="Rating" prop="rating">
          <el-rate v-model="dialog.rating" allow-half />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">Cancel</el-button>
          <el-button type="primary" @click="confirm">Confirm</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref } from 'vue'
import Dropdown from '@/components/Dropdown/index.vue'
import Sticky from '@/components/Sticky/index.vue'
import { updateFavorite, getFavoriteData } from '@/api'

const defaultForm = {
    type: 'movie',
    items: [],
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

const dialogFormRef = ref()

export default {
  name: 'favorite',
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
      tempRoute: {},
      dialogVisible: false,
      dialog: {
        id: '',
        title: '',
        rating: 0,
        comment: ''
      },
      isAdd: false
    }
  },
  created() {
    this.tempRoute = Object.assign({}, this.$route)
    getFavoriteData().then(response => {
        this.dataMap = response.data.data
        this.favoriteForm.items = this.dataMap[this.favoriteForm.type]
      })
  },
  methods: {
    setTagsViewTitle() {
      const title = '编辑收藏'
      const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.type}` })
      this.$store.dispatch('tagsView/updateVisitedView', route)
    },
    changeType(val) {
      this.favoriteForm.items = this.dataMap[val]
    },
    edit(row) {
      this.dialogVisible = true
      this.dialog = row
      this.isAdd = false
    },
    add() {
      this.dialogVisible = true
      this.isAdd = true
    },
    confirm() {
      if (this.isAdd) {
        this.favoriteForm.items.unshift(Object.assign({}, this.dialog))
      }
      this.handleClose()
    },
    handleClose() {
      this.dialogVisible = false
      this.dialog = {
        id: '',
        title: '',
        rating: 0,
        comment: ''
      }
      this.isAdd = false
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
.subject-link {
  color: var(--el-color-primary);
}
.type-label {
  line-height: 80px
}
.btn-add {
  margin-left: 12px;
}
</style>
