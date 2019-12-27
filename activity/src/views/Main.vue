<template>
  <div>
    <upload-form v-on:insertNewActivity="insertNewActivity" v-if="token"/>
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
            <div class="pics" :class="{ 'pics-big' : activity.big }" @click="toggleActivitySize(activity)"
                 v-else-if="activity.attachments.length && activity.layout == 1">
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
              <a v-if="activity.can_comment" href="javascript:void(0);" class="btn reply" @click="toggleShowComments(activity)">{{ activity.showComments ? ' 隐藏' : activity.n_comments || ''}}评论</a>
              <a href="javascript:void(0);" class="btn heart" :class="{ 'liked' : activity.liked }" @click="react(activity)">{{ activity.liked ? '已' : '' }}赞{{ activity.n_likes == 0 ? '' : `(${activity.n_likes})` }}</a>
            </div>
            <div class="comments" v-if="activity.showComments">
              <div class="comments-items">
                <div v-for="(comment, index) in activity.comments" :key="index" class="comment-item"
                     @mouseover="comment.showReply = true" @mouseleave="comment.showReply = false">
                  <span class="comment-item-content">{{ comment.content }}</span>
                  <i class="comment-item-spliter">-</i>
                  <a class="comment-item-author" :href="comment.user.link">{{ comment.user.username }}</a>
                  <div class="comment-item-action" v-if="comment.showReply">
                    <a class="reply" @click="reply(activity, comment)">回复</a>
                  </div>
                </div>
              </div>
              <form class="comment-reply" v-on:submit.prevent="commentTo(activity)">
                <div class="comment-text">
                  <span class="reply-target">{{ replyTo }}</span>
                  <input type="text" v-model="commentContent" class="reply-input" maxlength="280" autocomplete="off">
                </div>
                <button class="comment-btn" type="submit">发表回应</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    <paginator :total="total" :page="page"/>
    <div id="aside"></div>
  </div>
</template>

<script>
import Vue from 'vue'
import Moment from 'moment'
import Component from 'vue-class-component'
import { getToken } from '#/utils/auth'
import UploadForm from '../components/UploadForm'
import Paginator from '../components/Paginator'
import { getActivities, reactActivity, commentActivity, getActivityCommentList } from '#/api'

Moment.locale('zh-cn');

export default @Component({components: {UploadForm, Paginator}}) class Main extends Vue {
  page = 1
  total = 10
  listLoading = false
  activities = []
  refId = 0
  replyTo = ''
  commentContent = ''

  patchActivity(activity) {
    activity.big = false
    activity.showReply = false
    activity.showComments = false
    activity.commentFetched = false
    activity.comments = []
    return activity
  }

  getActivityList() {
    this.listLoading = true
    this.page = this.$route.query.p || this.page
    getActivities(this.page).then(response => {
        this.activities = response.data.items.map(i => {
          return this.patchActivity(i)
        })
        this.total = response.data.total
        this.listLoading = false
      })
  }
  get token() {
    return getToken()
  }
  insertNewActivity(activity) {
    this.activities.unshift(this.patchActivity(activity))
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
  fetchCommentList(activity) {
    getActivityCommentList(activity.id).then(response => {
      activity.comments = response.data.items.map(i => {
          i.showReply = false
          return i
        })
      activity.commentFetched = true
    })
  }
  toggleShowComments(activity) {
    activity.showComments = !activity.showComments
    if (activity.showComments && activity.commentFetched) {
      return
    }
    if (activity.showComments) {
      this.fetchCommentList(activity)
    }
  }

  react(activity) {
    reactActivity(activity.id, activity.liked ? 'delete': 'post').then(response => {
      if (response.data.r != 0) {
        this.$toasted.show(`点赞失败: ${response.data.msg}`)
        if (response.data.r == 403) {
          this.$toasted.show(`登录中...`)
          window.location =  '/oauth/activities'
        }
      } else {
        activity.n_likes = response.data.n_reacted
        activity.liked = !activity.liked
      }
    })
  }
  commentTo(activity) {
    if (!this.commentContent) {
      return
    }
    commentActivity(activity.id, `${this.replyTo} ${this.commentContent}`, this.refId).then(response => {
      if (response.data.r != 0) {
        this.$toasted.show(`评论失败: ${response.data.msg}`)
        if (response.data.r == 403) {
          this.$toasted.show(`登录中...`)
          window.location =  '/oauth/activities'
        }
      } else {
        this.$toasted.show('评论成功')
        this.replyTo = ''
        this.commentContent = ''
        let comment = response.data.comment
        comment.showReply = false
        activity.comments.unshift(comment)
      }
    })
  }
  reply(activity, comment) {
    this.refId = comment.id
    this.replyTo = `回应 @${comment.user.username}`
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "../../../static/css/dracula.css";
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
#aside {
  width: 300px;
  float: right;
  margin-top: 80px;
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
  margin-top: 30px;
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
  .liked {
    color: #999;
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
  background: #3C4556;
  padding: 0 10px;
  border-radius: 2px;
  margin: 20px 0;
  overflow: auto;
  position: relative;
}
.html /deep/ .hljs {
  background: #3C4556;
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
  .plyr__controls, .plyr__control--overlaid {
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
.comment-reply {
  display: flex;
  margin-top: 5px;
  .comment-text {
    flex: 1;
    width: 520px;
    padding: 2px 4px;
    border-radius: 2px;
    font-size: 13px;
    vertical-align: middle;
    border: 1px solid #c9c9c9;
    display: flex;
    .reply-target {
      display: inline-block;
      line-height: 20px;
    }
    .reply-input {
      flex: 1;
      line-height: 20px;
      padding: 0px 0px 0px 5px;
      border: none;
      outline: 0;
    }
  }
  .comment-btn {
    font-size: 12px;
    margin-left: 10px;
    height: 26px;
    line-height: 24px;
    padding: 0 3px;
    border-radius: 2px;
    border: 1px solid #c0c0c0;
    background-image: -webkit-gradient(linear, left top, left bottom, color-stop(0, #fcfcfc), color-stop(1, #e9e9e9));
    outline: none;
  }
}
.comments {
  margin-top: 7px;
}
.comment-item {
  position: relative;
  margin: 3px 10px 3px 0px;
  padding-right: 60px;
  line-height: 1.62em;
  overflow: hidden;
  word-wrap: break-word;
  .comment-item-content {
    color: #666;
  }
  .comment-item-spliter {
    color: #666;
    margin-left: 5px;
    margin-right: 5px;
  }
  .comment-item-action {
    position: absolute;
    right: 0;
    top: 0;
    a {
      color: #bbb;
      margin-left: 5px;
    }
  }
}
@media (max-width: 768px) {
  #aside {
    display: none
  }
  #activities, .paginator {
    margin: 0 auto;
    margin-top: 30px;
  }
  .paginator {
    margin: 30px;
  }
}
@media screen and (max-width: 414px) {
  #activities {
    padding: 0 16px;
    width: 100%;
  }
  .pics {
    width: min-content;
  }
  .paginator {
    margin: 10px 0;
    width: 100%;
  }
  .bd {
    padding-left: 48px;
  }
  .avatar {
    margin-right: 10px;
    img {
      width: 36px;
      height: 36px;
      border-radius: 50%;
    }
  }
}
</style>