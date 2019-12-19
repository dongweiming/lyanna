<template>
  <div>
    <upload-form/>
    <div id="activities" v-if="activities.length">
      <div v-for="activity in activities" :key="activity.id" class="activity-item">
        <div class="mod">
          <div class="hd">
            <div class="avatar">
              <a href="javascript:void(0);" title="dd">
                <img :src="activity.user.avatar" v-if="activity.user.avatar" :alt="activity.user.name">
              </a>
            </div>
            <div class="text">
              <a href="javascript:void(0);" class="bold">{{activity.user.name}}</a>{{ activity.action }}:
              <div class="content">
                <div class="html" v-html="activity.target.html_content"></div>
              </div>
            </div>
          </div>
          <div class="bd">
            <div class="lnk" v-if="activity.attachments.length && activity.layout == 0">
              <div v-for="(attachment, index) in activity.attachments" :key="index" class="blockquote">
                <div class="title">
                  <a :href="attachment.url" target="_blank">{{ attachment.title }}</a>
                </div>
                <p>{{ attachment.abstract }}</p>
              </div>
            </div>
            <div class="pics" :class="{ 'pics-big' : activity.big }" @click="toggleActivitySize(activity)" v-else-if="activity.attachments.length && activity.layout == 1">
              <div v-for="(attachment, index) in activity.attachments" :key="index" class="pic">
                <img :src="attachment.url">
              </div>
            </div>
            <div class="videos" v-else-if="activity.attachments.length && activity.layout == 2">
              <div v-for="(attachment, index) in activity.attachments" :key="index" class="video"
                   v-bind:style="{ width: attachment.size[0] * 172 * (activity.big ? 2 : 1) / attachment.size[1]  + 'px' }"
                   :class="{ 'video-big' : activity.big }" @click="toggleActivitySize(activity)">
                <vue-plyr class="screen">
                  <video :poster="attachment.cover_url">
                  <source :src="attachment.url" type="video/mp4">
                  </video>
                  <i class="iconfont icon-ziyuan video-overlay"></i>
                </vue-plyr>
              </div>
            </div>
            <div class="actions">
              <span class="time" :title="moment(activity.created_at).format('YYYY-MM-D HH:mm:ss')"><a :href="activity.target.url || 'javascript:void(0);'">
                {{ moment(activity.created_at).fromNow()}}</a></span>
              <a href="javascript:void(0);" class="btn reply">1回应</a>
              <a href="javascript:void(0);" class="btn heart">2赞</a>
            </div>
            <div class="comments" v-if="activity.showComment">
              <div class="comments-items"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Moment from 'moment'
import Component from 'vue-class-component'
import UploadForm from '../components/UploadForm'
import { getActivities } from '#/api'

Moment.locale('zh-cn');

export default @Component({components: {UploadForm}}) class Main extends Vue {
  page = 1
  listLoading = false
  activities = []

  getActivityList() {
    this.listLoading = true
    getActivities(this.page).then(response => {
        this.activities = response.data.items.map(i => {
          i.big = false
          return i
        })
        this.total = response.data.total
        this.listLoading = false
      })
  }
  moment(value) {
    return Moment(value * 1000)
  }
  created() {
    return this.getActivityList()
  }
  toggleActivitySize(activity) {
    if (activity.layout == 2 && activity.big) {
      return
    }
    activity.big = !activity.big
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
::selection {
  background: #63B5F5;
  color: #fff;
}
body {
  font-family: Helvetica,Arial,sans-serif;
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
  cursor: pointer;
  color: #7094b7;
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
.bold {
  font-weight: bold;
}
.text {
  margin-left: 10%;
  color: #9d9d9d;
  a {
    margin-right: 2px;
  }
}
#activities {
  clear: both;
  text-align: left;
  font-size: 14px;
  width: 675px;
  padding-top: 30px;
}
.activity-item {
  padding: 20px 0;
  border-bottom: 1px solid #e5e5e5;
  &:first-child {
    padding-top: 0;
  }
}
.bd {
    zoom: 1;
    padding-left: 10%;
}
.avatar {
  float: left;
  position: relative;
  z-index: 1;
  margin-right: 20px;
  img {
    width: 48px;
    height: 48px;
  }
}
.actions {
  line-height: 1;
  clear: both;
  margin: 20px 0 0;
  color: #aaa;
  .time {
    margin-right: 1em;
    a {
      color: #999
    }
  }
  .btn {
    color: #7094b7;
    margin-left: .5em;
  }
}
.lnk {
  overflow: hidden;
  zoom: 1;
  padding: 16px 20px;
  background: #f9f9f9;
  .blockquote {
    overflow: hidden;
    zoom: 1;
    word-wrap: break-word;
  }
  .title {
    margin-bottom: 4px;
    font-size: 15px;
  }
}
.content * {
  padding: 0 18px 0 0;
  color: #555;
  overflow: hidden;
  word-wrap: break-word;
}
.html /deep/ p {
  margin: 0;
}
.html /deep/ .highlight {
  margin: 0;
  display: grid !important;
}
.pics {
  font-size: 0;
  display: inline-block;
  overflow: hidden;
  .pic {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    max-width: 230px;
    max-height: 230px;
    margin: 6px 6px 0 0;
    overflow: hidden;
    vertical-align: top;
    float: left;
    img {
      height: 172px;
      width: auto;
      max-width: initial;
      object-fit: contain;
      cursor: pointer;
    }
  }
}
.pics-big {
  .pic {
    font-size: 100%;
    white-space: normal;
    width: auto;
    height: auto;
    max-height: initial;
    overflow: hidden;
    border: none;
    margin-top: 0;
    float: left;
    clear: both;
    min-width: 32px;
    min-height: 32px;
    margin: 0 0 10px 0;
    line-height: 0;
    position: relative;
    display: inline-block;
    zoom: 1;
    vertical-align: top;
    max-width: inherit;
    img {
      max-width: 526px;
      width: auto !important;
      height: initial;
    }
  }
}
.video /deep/ .plyr--video {
  height: 172px;
  cursor: pointer;
  .plyr__controls {
    display: none;
  }
}
.screen {
  position: relative;
}
.video-overlay {
  position: absolute;
  top: calc(50% - 18px);
  left: calc(50% - 18px);
  cursor: pointer;
  font-size: 36px;
}
.video-big .video-overlay {
  display: none;
}
.video-big /deep/ .plyr--video {
  height: 344px;
  .plyr__controls {
    display: flex;
  }
}
</style>