<template>
<div>
  <div id="activities">
    <div class="create-activity" v-bind:class="{ active: OnFocus }">
      <form class="create-form" name="form" v-on:submit.prevent="onSubmit">
        <ul class="activity-tab">
          <li class="status active"><a data-action="status" href="javascript:void(0);"><i class="iconfont icon-dongtai icon-right"></i><span>发动态</span></a></li>
          <li class="pic"><a data-action="pic" href="javascript:void(0);"><i class="iconfont icon-photo icon-right"></i><span>发照片</span></a></li>
          <li class="video"><a data-action="video" href="javascript:void(0);"><i class="iconfont icon-video icon-right"></i><span>发视频</span></a></li>
          <li class="link"><a data-action="link" href="javascript:void(0);"><i class="iconfont icon-link icon-right"></i><span>推荐网页</span></a></li>
        </ul>
        <div class="activity-content">
          <label id="label" for="text" v-if="!OnFocus && !text">分享我的动态...</label>
          <textarea id="text" name="text" v-bind:style="{ height: textAreaHeight + 'px' }" v-model="text" rows="1"
                    @focus="OnFocus = true"></textarea>
        </div>
        <div class="upload-form">
          <div class="bd">
            <div class="upload-section">
              <p class="drag-tip"><i class="iconfont icon-Drag-Drop"></i>拖图到框里上传</p>
              <a href="javascript: void 0;" class="upload-btn">
                <i class="iconfont icon-photoadd icon-big"></i>
                <span class="upload-info">上传照片</span></a>
              <p>按住command键可最多选中<span class=""></span>张</p>
            </div>
          </div>
          <a href="javascript:void(0);" class="upload-cancel">×</a>
        </div>
        <div class="btn" v-if="OnFocus">
          <button type="submit" class="pure-button activity-btn">发布</button>
        </div>
      </form>
      <div class="pure-button-group btn-group">
        <form v-if="!showIcon" charset="utf-8" id="upload" data-action="pic" action="/j/upload" enctype="multipart/form-data" method="post">
          <input id="upload-inp" autocomplete="off" data-action="pic" name="image" title="可传多张照片" type="file" multiple="" accept="image/jpg,image/jpeg,image/bmp,image/gif,image/png,">
        </form>
        <a v-if="showIcon" href="javascript:void(0);" data-action="pic" class="iconfont icon-photo1" title="上传照片"><span class="ico">照片</span></a>
        <a v-if="showIcon" href="javascript:void(0);" data-action="video" class="iconfont icon-video1" title="上传视频"><span class="ico">视频</span></a>
      </div>
    </div>
  </div>
  <div id="aside"></div>
</div>
</template>

<script>
import Vue from 'vue'
import Component from 'vue-class-component'

export default @Component() class Main extends Vue {
  text = ''
  OnFocus = false
  showIcon = true

  onSubmit() {
    console.log(11)
  }


  get textAreaHeight () {
    if (this.OnFocus) {
      let rows = this.text.split(/\r\n|\r|\n/).length + 1
      return rows > 5 ? rows * 16 : 80
    } else {
      return 32
    }
  }
}
</script>

<style scoped>
ol, ul, dd, dl {
  padding-left: 0;
}
input[type=text]:focus, input[type=password]:focus, textarea:focus {
  outline: 0;
}
.activity-tab a:link {
  text-decoration: none;
}
.activity-tab a:hover span {
  color: #fff;
  background: #6699CC;
}

#activities {
  width: 675px;
  float: left;
  margin-top: 80px;
}

#aside {
  width: 300px;
  float: right;
  margin-top: 80px;
}

.create-activity {
  position: relative;
  padding: 0;
  margin: -5px 0 2em;
  *zoom: 1;
  z-index: 1;
}
.active .activity-content {
  border-color: #ccc;
}

.active .activity-content textarea {
  border-color: #bababa;
  margin-bottom: 20px;
  color: #666;
}
.active .btn-group {
  letter-spacing: 0;
  position: relative;
  text-align: left;
  margin-left: 7px;
  margin-top: -70px;
}

.activity-tab {
  font-size: 0;
  height: 30px;
  line-height: 30px;
  text-align: left;
}

.activity-tab li {
  font-size: 14px;
  display: inline-block;
  margin-right: 18px;
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
}
.activity-content label {
  position: absolute;
  color: #aaa;
  left: 7px;
  line-height: 34px;
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
  bottom: -3px;
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
.activity-content textarea {
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
}

.btn-group {
  position: absolute;
  top: 50%;
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
  color: #888;
  font-family: stheiti, tahoma, simsun, sans-serif;
}
.btn-group a {
  font-size: 13px;
}
#upload {
  position: absolute;
  width: 21px;
  height: 22px;
  padding: 0;
  overflow: hidden;
  right: 38px;
  top: -1px;
  opacity: 0;
}
#upload input {
  cursor: pointer;
  position: absolute;
  height: 22px;
  right: 0;
  margin: 0;
  filter: alpha(opacity=0);
  -ms-filter: alpha(opacity=0);
}
.activity-btn {
  background-color: #6699CC;
  color: #fff;
  padding: .3em .6em;
  font-size: 14px;

}
.upload-form {
  display: none;
  cursor: pointer;
  position: relative;
  background: #fff;
  margin-top: -5px;
  z-index: 1;
  padding: 8px;
  padding: 5px 8px;
  border: 1px solid #ccc;
  border-top-color: #e6e6e6;
}
.acting {
  display: block;
}
.upload-form .bd {
  color: #999;
  margin: auto;
  font-weight: 400;
}

.upload-section {
  position: relative;
  width: 651px;
  height: 94px;
  border: 3px dashed #eee;
  margin: 3px 0;
  text-align: center;
  color: #ccc;
  background: #fafafa;
}
.upload-section p {
  margin-top: -4px;
  line-height: 2;
  font-size: 13px;
}
.upload-section .drag-tip {
  position: absolute;
  top: 0;
  z-index: 1;
  margin: 0;
  text-align: left;
  text-indent: 7px;
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
</style>
