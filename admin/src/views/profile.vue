<template>
  <div class="createPost-container">
    <el-form ref="form" :model="form" :rules="rules" class="form-container" v-if="isShow">
      <sticky class-name='sub-navbar draft'>
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">更新
        </el-button>
      </sticky>

      <div class="createPost-main-container">
        <el-row>
          <div class="avatar">
            <img :src="image" class="avatar">
            <el-button type="primary" icon="upload" style="position: absolute;bottom: 15px;margin-left: 40px;" @click="imagecropperShow=true">改变头像</el-button>
            <image-cropper
              v-show="imagecropperShow"
              :width="300"
              :height="300"
              :key="imagecropperKey"
              url="/api/upload"
              lang-type="en"
              @close="close"
              @crop-upload-success="cropSuccess"/>
          </div>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="intro">
              <MDinput v-model="form.intro" :maxlength="100" name="intro" required>
                Intro
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="github_url">
              <MDinput v-model="form.github_url" :maxlength="100" name="github_url" required>
                Github URL
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 20px;" prop="linkedin_url">
              <MDinput v-model="form.linkedin_url" :maxlength="100" name="linkedin_url" required>
                Linkedin URL
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-form>
    <div class="createPost-main-container" v-else>
      <code>config.py里面的 SHOW_PROFILE 项的值为True才能设置用户Profile页面哟！👉
      <a target="_blank" href=" https://dongweiming.github.io/lyanna/#/configuration?id=show_profile">
        文档 </a>
    </code>
    </div>
  </div>
</template>

<script>
import MDinput from '@/components/MDinput'
import Sticky from '@/components/Sticky'
import ImageCropper from '@/components/ImageCropper'
import { getProfile, updateProfile } from '@/api'

const defaultForm = {
    intro: '',
    github_url: '',
    linkedin_url: '',
    avatar: '',
    avatar_url: ''
}

export default {
    name: 'Profile',
    components: { MDinput, Sticky, ImageCropper },
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
            isShow: true,
            loading: false,
            form: Object.assign({}, defaultForm),
            imagecropperShow: false,
            imagecropperKey: 0,
            image: '',
            rules: {
                intro: [{ validator: validateRequire }]
            },
            tempRoute: {}
        }
    },
    created() {
        this.loading = true
        getProfile().then(response => {
            if (!response.data.on) {
                this.isShow = false
            }
            let { profile } = response.data
            if (profile) {
                this.form = response.data.profile
                this.image = this.form.avatar_url || '/static/img/default-avatar.jpg'
            }
            this.loading = false
            this.setTagsViewTitle()
        }).catch(err => {
            console.log(err)
        })
        this.tempRoute = Object.assign({}, this.$route)
    },
    methods: {
        cropSuccess(resData) {
            this.imagecropperShow = false
            this.imagecropperKey = this.imagecropperKey + 1
            this.image = resData.files.avatar
            this.form.avatar = resData.avatar_path
        },
        close() {
            this.imagecropperShow = false
        },
        setTagsViewTitle() {
            const title = 'Profile'
            const route = Object.assign({}, this.tempRoute, { title })
            this.$store.dispatch('updateVisitedView', route)
        },
        submitForm() {
            this.$refs.form.validate(valid => {
                if (valid) {
                    this.loading = true
                    let self = this;
                    updateProfile(this.form).then(() => {
                        self.$notify({
                            title: '成功',
                            message: '更新成功',
                            type: 'success',
                            duration: 2000
                        })
                        this.loading = false
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
@import "~@/styles/mixin.scss";
.createPost-container {
  position: relative;
  .createPost-main-container {
    padding: 40px 45px 20px 50px;
  }
}
.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
}
</style>
