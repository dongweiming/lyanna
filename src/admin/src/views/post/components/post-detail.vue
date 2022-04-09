<template>
  <div class="createPost-container">
    <el-form ref="postForm" :model="postForm" :rules="rules" class="form-container">

      <sticky class-name='sub-navbar draft'>
        <Dropdown v-model:value="postForm.is_page" enabled-text="Page页面" disabled-text="Post页面" />
        <Dropdown v-model:value="postForm.can_comment" enabled-text="评论打开" disabled-text="评论关闭" />
        <Dropdown v-model:value="postForm.status" enabled-text="发布" disabled-text="草稿" enabled-label="1" disabled-label="0" />
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm"> {{ isEdit ? '更新' : '发布' }}
        </el-button>
      </sticky>

      <div class="createPost-main-container">
        <el-card v-if="postForm.target_title">
          <img :src="cover" class="image" />
          <div style="padding: 14px">
            <span>{{ postForm.target_title }}</span>
            <div class="abstract">{{ postForm.target_abstract }}</div>
          </div>
        </el-card>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="title">
              <MDinput v-model:value="postForm.title" :maxlength="100" name="title" required>
                Title
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="slug">
              <MDinput v-model:value="postForm.slug" :maxlength="100" name="slug" required>
                Slug
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="summary">
              <MDinput v-model:value="postForm.summary" name="summary" required>
                Summary
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="target_url">
              <MDinput v-model:value="postForm.target_url" name="target_url" required>
                Target URL
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label-width="45px" label="标签:" class="postInfo-container-item">
              <el-select v-model="postForm.tags" multiple filterable allow-create placeholder="搜索标签">
                <el-option v-for="(item,index) in tagListOptions" :key="item+index" :label="item" :value="item"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <markdown-editor ref="markdownEditor" v-model:value="postForm.content" height="500px" />
        </el-row>
      </div>
    </el-form>

  </div>
</template>

<script>
import MarkdownEditor from '@/components/MarkdownEditor/index.vue'
import MDinput from '@/components/MDinput/index.vue'
import Sticky from '@/components/Sticky/index.vue'
import Dropdown from '@/components/Dropdown/index.vue'
import { fetchPost, updatePost, createPost, fetchTags, getUrlInfo } from '@/api'

const defaultForm = {
    id: undefined,
    title: '',
    slug: '',
    summary: '',
    content: '',
    is_page: false,
    can_comment: true,
    tags: [],
    status: '1',
    target_title: '',
    target_abstract: '',
    target_url: '',
    target_basename: ''
}

export default {
    name: 'PostDetail',
    components: { MarkdownEditor, MDinput, Sticky, Dropdown },
    props: {
        isEdit: {
            type: Boolean,
            default: false
        }
    },
    watch: {
      'postForm.target_url'(dst, ast) {
        this.getLinkInfo()
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
            postForm: Object.assign({}, defaultForm),
            loading: false,
            cover: '',
            tagListOptions: [],
            rules: {
                title: [{ validator: validateRequire }],
                content: [{ validator: validateRequire }]
            },
            tempRoute: {}
        }
    },
    created() {
        if (this.isEdit) {
            const id = this.$route.params && this.$route.params.id
            this.fetchData(id)
        } else {
            this.postForm = Object.assign({}, defaultForm)
        }

        this.tempRoute = Object.assign({}, this.$route)

        fetchTags().then(response => {
            this.tagListOptions = response.data.items
        }).catch(err => {
            console.log(err)
        })
    },
    methods: {
        fetchData(id) {
            fetchPost(id).then(response => {
                this.postForm = response.data
                this.setTagsViewTitle()
            }).catch(err => {
                console.log(err)
            })
        },
        setTagsViewTitle() {
            const title = '编辑文章'
            const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.postForm.id}` })
            this.$store.dispatch('updateVisitedView', route)
        },
        submitForm() {
            this.$refs.postForm.validate(valid => {
                if (valid) {
                    this.loading = true
                    let promise
                    let form = Object.assign({}, this.postForm)

                    if (this.isEdit) {
                        let id = form.id
                        promise = updatePost(id, form)
                    } else {
                        promise = createPost(form)
                    }
                    let self = this;
                    promise.then(() => {
                        self.$notify({
                            title: '成功',
                            message: '文章处理成功',
                            type: 'success',
                            duration: 2000
                        })
                        this.loading = false
                        this.$router.push('/post/list?refresh=1')
                    }).catch(err => {
                        console.log(err)
                    })
                } else {
                    console.log('error submit!!')
                    return false
                }
            })
        },
        getLinkInfo() {
          if (!this.postForm.target_url.startsWith('http')) {
            this.urlError = '这不是一个网址'
            return false
          }
          this.urlLoading = true
          getUrlInfo(this.postForm.target_url).then(response => {
            if (response.data.r == 1) {
              this.urlError = response.data.msg
            } else {
              this.cover = response.data.info.cover
              this.postForm.target_title = response.data.info.title
              this.postForm.target_abstract = response.data.info.abstract
              this.postForm.target_basename = response.data.info.basename
            }
            this.urlLoading = false
          }).catch(() => {
            this.urlError = '超时了，请重试'
            this.urlLoading = false
          })
        }
    }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "@/styles/mixin.scss";
.createPost-container {
  position: relative;
  .createPost-main-container {
    padding: 40px 45px 20px 50px;
  }
}
.el-card {
  float: right;
  margin-top: 2em;
  width: 300px;
}
.image {
  width: 100%;
}
</style>
