<template>
  <div class="createPost-container">
    <el-form ref="userForm" :model="userForm" :rules="rules" class="form-container">

      <sticky class-name='sub-navbar draft'>
        <el-checkbox v-model="userForm.active">Active</el-checkbox>
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm"> {{ isEdit ? '更新' : '新增' }}
        </el-button>
      </sticky>

      <div class="createPost-main-container">
        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 40px;" prop="name">
              <MDinput v-model="userForm.name" :maxlength="100" name="name" required :disabled="isEdit">
                Name
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

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
            <el-form-item style="margin-bottom: 40px;" prop="email">
              <MDinput v-model="userForm.email" :maxlength="100" name="email" required>
                Email
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 40px;" prop="password">
              <MDinput v-model="userForm.password" :maxlength="100" name="password" required>
                Password
              </MDinput>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-form>

  </div>
</template>

<script>
import MDinput from '@/components/MDinput'
import Sticky from '@/components/Sticky'
import ImageCropper from '@/components/ImageCropper'
import { fetchUser, updateUser, createUser } from '@/api'

const defaultForm = {
  active: true,
  name: '',
  email: '',
  password: '',
  id: undefined,
  avatar: '/static/img/default-avatar.jpg'
}

export default {
  name: 'UserDetail',
  components: { MDinput, Sticky, ImageCropper },
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
      userForm: Object.assign({}, defaultForm),
      loading: false,
      rules: {
        name: [{ validator: validateRequire }],
        email: [{ validator: validateRequire }]
      },
      tempRoute: {},
      imagecropperShow: false,
      imagecropperKey: 0,
      image: '',
    }
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params && this.$route.params.id
      this.fetchData(id)
    } else {
      this.userForm = Object.assign({}, defaultForm)
    }

    this.tempRoute = Object.assign({}, this.$route)
  },
  methods: {
    fetchData(id) {
      fetchUser(id).then(response => {
        this.userForm = response.data
        this.userForm.password = ''
        if (this.userForm.avatar) {
          this.image = this.userForm.avatar_url
        }
        this.setTagsViewTitle()
      }).catch(err => {
        console.log(err)
      })
    },
    setTagsViewTitle() {
      const title = '编辑用户'
      const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.userForm.id}` })
      this.$store.dispatch('updateVisitedView', route)
    },
    cropSuccess(resData) {
      this.imagecropperShow = false
      this.imagecropperKey = this.imagecropperKey + 1
      this.image = resData.files.avatar
      this.userForm.avatar = resData.avatar_path
    },
    submitForm() {
      this.$refs.userForm.validate(valid => {
        if (valid) {
          this.loading = true
          let promise
          if (this.isEdit) {
            let id = this.userForm.id
            promise = updateUser(id, this.userForm)
          } else {
            promise = createUser(this.userForm)
          }
          let self = this;
          promise.then(() => {
            self.$notify({
              title: '成功',
              message: '用户发布成功',
              type: 'success',
              duration: 2000
            })
            this.loading = false
            if (!this.isEdit) {
              this.$router.push('/user/list?refresh=1')
            }
            this.$store.dispatch('SetNewAvatar', [this.userForm.name, self.image])
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
