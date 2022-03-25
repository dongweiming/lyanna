<template>
  <div class="createTopic-container">
    <el-form ref="topicForm" :model="topicForm" :rules="rules" class="form-container">

      <sticky class-name='sub-navbar draft'>
        <Dropdown v-model="topicForm.status" enabled-text="发布" disabled-text="草稿" enabled-label="1" disabled-label="0" />
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm"> {{ isEdit ? '更新' : '新增' }}
        </el-button>
      </sticky>

      <div class="createTopic-main-container">
        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 40px;" prop="title">
              <MDinput v-model:value="topicForm.title" :maxlength="100" name="title" required :disabled="isEdit">
                Title
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="slug">
              <MDinput v-model:value="topicForm.slug" :maxlength="100" name="slug" required>
                Slug
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 40px;" prop="intro">
              <MDinput v-model:value="topicForm.intro" :maxlength="100" name="intro" required>
                Intro
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="post-container">
          <dnd-list :list1="topicForm.posts" :list2="allPosts" list1-title="ArticleList" list2-title="Article Pool" />
        </div>
      </div>
    </el-form>

  </div>
</template>

<script>
import MDinput from '@/components/MDinput/index.vue'
import Dropdown from '@/components/Dropdown/index.vue'
import Sticky from '@/components/Sticky/index.vue'
import DndList from '@/components/DndList/index.vue'
import { fetchTopic, updateTopic, createTopic, getPostList } from '@/api'

const defaultForm = {
    status: '1',
    title: '',
    intro: '',
    slug: '',
    id: undefined,
    posts: []
}

export default {
  name: 'TopicDetail',
  components: { MDinput, Sticky, Dropdown, DndList },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
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
      topicForm: Object.assign({}, defaultForm),
      loading: false,
      rules: {
        name: [{ validator: validateRequire }],
        email: [{ validator: validateRequire }]
      },
      tempRoute: {},
      allPosts: []
    }
  },
  created() {
    let params = {page: 1, limit: 1000}
    if (this.isEdit) {
      const id = this.$route.params && this.$route.params.id
      this.fetchData(id)
      params['special_id'] = id
    } else {
      // FIXME
      this.topicForm.posts = []
    }

    getPostList(params).then(response => {
            this.allPosts = response.data.items.map(p => {
              return {'id': p.id, 'title': p.title}
            })
        }).catch(err => {
            console.log(err)
        })

    this.tempRoute = Object.assign({}, this.$route)
  },
  methods: {
    fetchData(id) {
      fetchTopic(id).then(response => {
        this.topicForm = response.data
        this.setTagsViewTitle()
      }).catch(err => {
        console.log(err)
      })
    },
    setTagsViewTitle() {
      const title = '编辑专题'
      const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.topicForm.id}` })
      this.$store.dispatch('updateVisitedView', route)
    },
    submitForm() {
      this.$refs.topicForm.validate(valid => {
        if (valid) {
          this.loading = true
          let promise
          let form = Object.assign({}, this.topicForm)
          delete form.n_posts
          if (this.isEdit) {
            let id = form.id
            promise = updateTopic(id, form)
          } else {
            promise = createTopic(form)
          }
          let self = this;
          promise.then(() => {
            self.$notify({
              title: '成功',
              message: '发布成功',
              type: 'success',
              duration: 2000
            })
            this.loading = false
            if (!this.isEdit) {
              this.$router.push('/topic/list?refresh=1')
            }
          }).catch(err => {
            console.log(err)
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "@/styles/mixin.scss";
.createTopic-container {
  position: relative;
  .createTopic-main-container {
    padding: 40px 45px 20px 50px;
  }
}
</style>
