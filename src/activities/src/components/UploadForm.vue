<template>
  <div id="form">
    <div class="create-activity" v-bind:class="{ active: OnFocus }">
    <form class="create-form" name="form" v-on:submit.prevent="onSubmit">
      <ul class="activity-tab">
        <li class="status" @click="activate(1)" :class="{ active : activeLi == 1 }"><a href="javascript:void(0);"><i class="iconfont icon-dongtai icon-right"></i><span>发动态</span></a></li>
        <li class="pic" @click="activate(2)" :class="{ active : activeLi == 2 }"><a href="javascript:void(0);"><i class="iconfont icon-photo icon-right"></i><span>发照片</span></a></li>
        <li class="video" @click="activate(3)" :class="{ active : activeLi == 3 }"><a href="javascript:void(0);"><i class="iconfont icon-video icon-right"></i><span>发视频</span></a></li>
        <li class="link" @click="activate(4)" :class="{ active : activeLi == 4 }"><a href="javascript:void(0);"><i class="iconfont icon-link icon-right"></i><span>推荐网页</span></a></li>
      </ul>
      <div class="field link-act" v-if="activeLi == 4">
         <div class="hd" v-if="urlInfo">
           <p>{{ this.urlInfo.title }}</p>
         </div>
        <div class="bd">
          <div v-if="urlError" class="error"><span>{{ this.urlError }}</span><a href="javascript:void(0);" v-on:click="urlError = ''">重新输入</a></div>
          <input v-if="!urlError && !urlLoading && !urlInfo" type="text" class="link-text" name="url" v-model="url">
          <input v-if="!urlError && !urlLoading && !urlInfo" type="button" class="input-link" value="输入网址" v-on:click="getLinkInfo" :disabled="!url">
          <p v-if="urlLoading">正在获取网址信息...</p>
          <p v-if="urlInfo">{{ this.urlInfo.abstract }}</p>
        </div>
        <a href="javascript:void(0);" class="link-cancel" v-if="urlInfo" v-on:click="urlInfo = null">×</a>
      </div>
      <div class="activity-content">
        <label id="label" for="text" v-if="!OnFocus && !text">分享我的动态...</label>
        <textarea id="text" name="text" v-bind:style="{ height: textAreaHeight + 'px' }" v-model="text" rows="1"
                  @focus="OnFocus = true"></textarea>
      </div>
      <div class="upload-form" v-if="[2, 3].includes(activeLi)">
        <!--
        <file-upload v-if="!files.length"
          class="upload"
          :custom-action="customAction"
           post-action="/api/upload"
          :multiple="true"
          :size="1024 * 1024 * 500"
          :drop="true"
          :drop-directory="true"
          v-model="files"
          @input-file="inputFile"
          @input-filter="inputFilter"
        ref="upload">
        </file-upload>
        -->
        <div class="bd">
          <!--
          <div class="upload-section" v-if="!files.length">
            <p class="drag-tip"><i class="iconfont icon-Drag-Drop icon-right"></i>拖文件到框里上传</p>
            <a href="javascript: void 0;" class="upload-btn">
              <i class="iconfont icon-big" v-bind:class="{ 'icon-photoadd' : activeLi == 2, 'icon-video_add' : activeLi == 3  }"></i>
              <span class="upload-info">上传{{ activeLi == 2 ? '照片' : '视频' }}</span></a>
          </div>
          -->
          <ul class="file-list">
            <li v-for="file in files" :key="file.id" class="file-item">
              <img :src="file.thumb" class="thumb" v-if="file.thumb">
              <a v-else :title="file.name">
                  <img :src="getCover(file)" class="thumb">
                  <i class="iconfont icon-ziyuan player-btn"></i>
              </a>
              <a href="#" class="lnk-remove-photo" v-on:click="removeFile(file)">×</a>
            </li>
            <li class="file-item add-photo"><i>+</i>
              <file-upload v-if="[2, 3].includes(activeLi)"
                class="file-upload"
                :custom-action="customAction"
                post-action="/api/upload"
                :multiple="true"
                :size="1024 * 1024 * 50"
                :drop="true"
                :drop-directory="true"
                v-model="files"
                @input-file="inputFile"
                @input-filter="inputFilter"
                ref="upload">
              </file-upload>
            </li>
          </ul>
        </div>
      </div>
      <div class="btn" v-if="OnFocus || activeLi != 1">
        <button type="submit" class="pure-button activity-btn">发布</button>
      </div>
    </form>
    <div class="pure-button-group btn-group" v-if="activeLi == 1">
      <a v-if="showIcon" href="javascript:void(0);" class="iconfont icon-photo1" title="上传照片">
        <span class="ico">照片</span>
      </a>
      <a v-if="showIcon" href="javascript:void(0);" class="iconfont icon-video1" title="上传视频">
        <span class="ico">视频</span>
      </a>
    </div>
    </div>
  </div>
</template>

<script>
// This component cannot use the Composition API of Vue 3,
// because the `vue-upload-component` used does not support use `$refs`
// TODO change to Vue 3 Composition API
import FileUpload from 'vue-upload-component'
import { useToast } from "vue-toastification";
import { createStatus, getUrlInfo } from '@/api'

const toast = useToast()

export default {

  data() {
    return {
      text: '',
      url: '',
      urlInfo: null,
      urlLoading: false,
      urlError: '',
      activeLi: 1,
      files: [],
      fids: new Map(),
      OnFocus: false,
      name: 'file'
    }
  },

  methods: {
    getLinkInfo() {
      if (!this.url.startsWith('http')) {
        this.urlError = '这不是一个网址'
        return false
      }
      this.urlLoading = true
      getUrlInfo(this.url).then(response => {
        if (response.data.r == 1) {
          this.urlError = response.data.msg
        } else {
          this.urlInfo = response.data.info
        }
        this.urlLoading = false
      }).catch(() => {
        this.urlError = '超时了，请重试'
        this.urlLoading = false
      })
    },

    async customAction(file, component) {
      let result = await component.uploadHtml5(file)
      const filename = JSON.parse(result.xhr.responseText)['filename']
      this.fids.set(file.id, filename)
      console.log(file, filename)
      return result
    },

    reset() {
      this.files = []
      this.fids = new Map()
      this.url = ''
      this.urlInfo = null
    },

    activate(num) {
      this.activeLi = num;
      if (!(this.activeLi == 1 && num != 1)) {
        this.reset()
      }
    },

    onSubmit() {
      const fids =[ ...this.fids.values() ];
      const data = {
        text: this.text,
        url: this.url,
        fids
      }
      if (this.url) {
        data['url_info'] = this.urlInfo
      }
      createStatus(data).then(response => {
        if (response.data.r == 1) {
          toast.error(`发布失败: ${response.data.msg}`)
        } else {
          this.text = ''
          this.url = ''
          toast.success('已发布')
          this.$emit('insertNewActivity', response.data.activity);
          this.reset()
        }
      }).catch(() => {
        toast.error('发布失败')
      })
    },

    getCover(file) {
      return file.id in this.fids && '/static/upload/' + this.fids.get(file.id).replace('.mp4', '.png') || ''
    },

    removeFile(file) {
      this.$refs.upload.remove(file)
      this.fids.delete(file.id)
    },

    inputFilter(newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        if (!/\.(jepg?|png?|mp4?|gif?|jpg?)$/i.test(newFile.name)) {
          toast.error(`不支持的文件类型`)
          return prevent()
        }
        let subtype = newFile.type.substr(0, 6)
        if (this.activeLi ==2 && subtype != 'image/') {
          toast.error(`照片Tab下不能放视频`)
          return prevent()
        }
        if (this.activeLi ==3 && subtype != 'video/') {
          toast.error(`视频Tab下不能放照片`)
          return prevent()
        }
      }
      if (newFile) {
        newFile.active = true
      }
      if (newFile && (!oldFile || newFile.file !== oldFile.file)) {
        newFile.blob = ''
        let URL = window.URL || window.webkitURL
        if (URL && URL.createObjectURL) {
          newFile.blob = URL.createObjectURL(newFile.file)
        }
        newFile.thumb = ''
        if (newFile.blob && newFile.type.substr(0, 6) === 'image/') {
          newFile.thumb = newFile.blob
        }
      }
    },

    inputFile(newFile, oldFile) {
      if (newFile && !oldFile) {
        if (this.files.length == 1) {
          let subtype = newFile.type.substr(0, 6)
          if (subtype === 'image/') {
            this.activeLi = 2;
          } else if (subtype === 'video/') {
            this.activeLi = 3;
          }
        }
      }
    }
  },

  computed: {
    textAreaHeight () {
      if (this.OnFocus || this.activeLi != 1) {
        let rows = this.text.split(/\r\n|\r|\n/).length + 1
        return rows > 5 ? rows * 16 : 80
      } else {
        return 32
      }
    },
    showIcon() {
      return this.activeLi == 1
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
ol, ul, dd, dl {
  padding-left: 0;
}
input[type=text]:focus, input[type=password]:focus, textarea:focus {
  outline: 0;
}
::selection {
  background: #63B5F5;
  color: #fff;
}
.activity-tab a:link {
  text-decoration: none;
}
.activity-tab a:hover span {
  color: #fff;
  background: #63B5F5;
}

#form {
  width: 675px;
  float: left;
  position: relative;
  padding: 0;
  padding-top: 40px;
  margin: -5px 0 2em;
  *zoom: 1;
  z-index: 1;
}

.active .activity-content {
  border-color: #ccc;
  textarea {
    border-color: #bababa;
    margin-bottom: 20px;
    color: #666;
  }
}
.active .btn-group {
  letter-spacing: 0;
  position: relative;
  text-align: left;
  margin-left: 7px;
  margin-top: -70px;
  padding-bottom: 40px;
}

.activity-tab {
  font-size: 0;
  height: 30px;
  line-height: 30px;
  text-align: left;

  li {
    font-size: 14px;
    display: inline-block;
    margin-right: 18px;
  }
}
.activity-tab .active a, .activity-tab .active a:link, .activity-tab .active a:visited,
.activity-tab .active a:active, activity-tab .active a:hover {
  color: #111;
  background-color: transparent;
}

.icon-right {
  margin-right: 4px;
}

.activity-content {
  border: 1px solid #d7d7d7;
  border-radius: 1px;
  position: relative;
  z-index: 0;
  margin-bottom: 0;
  overflow: hidden;
  font-size: 14px;
  label {
    position: absolute;
    color: #aaa;
    left: 7px;
    line-height: 34px;
  }
  textarea {
    background: transparent;
    resize:none;
    padding: 7px 25px 7px 7px;
    margin-top: -1px;
    overflow: hidden;
    vertical-align: bottom;
    border: none;
    font-family: tahoma;
    line-height: 1.3;
    position: relative;
    z-index: 1;
    -webkit-transition: all 0.1s;
  }
}
.activity-tab .active {
  position: relative;
}
.ico {
  margin-left: 2px;
  font-size: 0;
}
.active .ico {
  font-size: 13px;
}
.active .btn-group a {
  font-size: 14px;
  margin-right: 7px;
}
.activity-tab .active:after {
  content: "";
  position: absolute;
  bottom: -2px;
  z-index: 1;
  left: 30px;
  height: 7px;
  width: 7px;
  border: 1px solid #ccc;
  border-width: 1px 1px 0 0;
  background: #fff;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}
.activity-content textarea, .upload-form .bd {
  width: 675px;

}
.upload-cancel {
  border: 0;
  background: none;
  cursor: pointer;
  color: #bec3c3;
  background: transparent;
  font: 400 14px/0.9 tahoma;
  line-height: 0.9;
  position: absolute;
  right: 8px;
  top: 5px;
  display: none;
}

.btn {
  float: none;
  width: auto;
  margin-right: 0;
  text-align: right;
  background: #f4f4f4;
  padding: 8px;
  border: 1px solid #ccc;
  border-top: none;
  position: relative;
  z-index: 101
}

.btn-group {
  position: absolute;
  top: 72%;
  right: 0;
  white-space: nowrap;
  z-index: 1;
  font-size: 13px;
}
.btn-group a {
  height: 20px;
  width: 18px;
  margin-right: 12px;
  text-indent: 999em;
  overflow: hidden;
  line-height: 20px;
  font-size: 13px;
  color: #888;
  font-family: stheiti, tahoma, simsun, sans-serif;
}
.activity-btn {
  background-color: #63B5F5;
  color: #fff;
  padding: .3em .6em;
  font-size: 14px;

}
.field {
  cursor: pointer;
  position: relative;
  background: #fff;
  z-index: 1;
  padding: 8px;
  padding: 5px 8px;
  border: 1px solid #ccc;
}
.upload-form {
  position: relative;
  padding: 9px 0;
  cursor: pointer;
  border-left: 1px solid #d7d7d7;
  border-right: 1px solid #d7d7d7;
  .bd {
    color: #999;
    margin: auto;
    font-weight: 400;
  }
}
.upload {
  position: absolute;
  width: 675px;
  height: 94px;
  left: 0;
}

.upload-section {
  position: relative;
  width: 651px;
  height: 94px;
  border: 3px dashed #eee;
  margin: auto;
  text-align: center;
  color: #ccc;
  background: #fafafa;

  p {
    margin-top: -4px;
    line-height: 2;
    font-size: 13px;
  }
  .drag-tip {
    position: absolute;
    top: 0;
    z-index: 1;
    margin-top: 4px;
    text-align: left;
    text-indent: 7px;
  }
}
.icon-big {
  display: block;
  font-size: 28px;
  margin-top: 16px;
  margin-bottom: -6px;
}
.upload-info {
  font-size: 14px;
}
.link-act {
  border-bottom: 0;
}
.link-text {
  width: 540px;
  margin-right: 5px;
  height: 26px;
  margin-left: -36px;
  font-size: 13px;
  *zoom: 1;
  border: 1px solid #ccc;
  color: #999;
  border-radius: 1px;
  padding-left: 7px;
}
.input-link {
  border-color: #ccc;
  border-radius: 2px;
  font-size: 12px;
  padding: 0 6px 2px;
  line-height: 2.2em;
  height: 2.2em;
  display: inline-block;
  zoom: 1;
  overflow: hidden;
  vertical-align: middle;
  color: #444;
  border-width: 1px;
  border-style: solid;
  background-image: -webkit-linear-gradient(top, #fcfcfc, #e9e9e9);
  &:hover, &:focus {
    outline: 0;
   }
}
.error {
  text-align: left;
  font-size: 13px;
  span {
    color: #999;
  }
  a {
    color: #37a;
    margin-left: 7px;
  }
}
.bd p, .hd p {
  margin: 0;
  font-size: 13px;
  text-align: left;
  line-height: 20px;
}
.link-cancel {
  position: absolute;
  top: 0;
  right: 7px;
}
.center {
  text-align: center !important
}
.file-list {
  padding: 0 7px;
  text-align: left;
}
.file-item {
  position: relative;
  display: inline-block;
  *display: inline;
  zoom: 1;
  margin-right: 10px;
  width: 52px;
  height: 52px;
  vertical-align: middle;
  overflow: hidden;
  text-align: center;
  border: 1px solid #ccc;
  font-size: 12px;
  letter-spacing: normal;
  word-spacing: normal;
  img {
    width: 52px;
    height: 52px;
  }
}
.lnk-remove-photo {
  position: absolute;
  top: 2px;
  right: 2px;
  line-height: 1;
  padding: 0 2px;
  &:link, &:visited, &:hover, &:active {
    color: #fff;
    background-color: rgba(0,0,0,0.4);
    *background-color: #000;
    filter: alpha(opacity=40);
  }
}
.add-photo {
  border: 2px dashed #ccc;
  i {
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    text-align: center;
    line-height: 1;
    margin-top: -.56em;
    font-family: tahoma;
    font-style: normal;
    font-weight: normal;
    font-size: 3em;
  }
}
.file-upload {
  position: absolute;
  top: 0;
  left: 0;
  width: 52px;
  height: 52px;
}
.file-uploads label {
  cursor: pointer;
}
.file-upload-btn {
    height: 30px;
    width: 92px;
    position: absolute;
    top: 0;
    left: 0;
}
.player-btn {
  position: absolute;
  color: #fff;
  top: 12px;
  left: 13px;
  font-size: 24px;
}
@media (max-width: 768px) {
  #form {
    display: none;
  }
}
</style>
