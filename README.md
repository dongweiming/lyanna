# lyanna

[![Build Status](https://travis-ci.org/dongweiming/lyanna.svg?branch=master)](https://travis-ci.org/dongweiming/lyanna)

My Blog Using Sanic

[查看文档 📖](https://dongweiming.github.io/lyanna/)

## Overview

这是一个使用asyncio生态开发的个人技术博客。具体如下：

* Web框架: Sanic
* 模板: Mako/Sanic-Mako
* 数据库: TortoiseORM/aiomysql
* 缓存: aiomcache
* KV数据库: aioredis
* 任务队列: arq

其他aio扩展: Sanic-Auth、Sanic-wtf、sanic-session、aiotask-context、asyncblink、sanic-sentry、sanic-jwt、aiosmtplib

<p align="center">
  <img width="600" src="./screenshot/blog.png" >
</p>

管理后台使用 ElementUI + Vue-CLI + Vue-Router + Vuex

<p align="center">
  <img width="600" src="./screenshot/admin.png" >
</p>

Inspired by [vue-element-admin](https://github.com/PanJiaChen/vue-element-admin)

## Features

* 可以通过后台对文章、标签等做增删改查
* 后台支持Markdown编辑/预览
* 支持代码语法高亮
* 支持TOC
* 支持文章搜索
* 支持Github登录评论
* 支持Github登录对文章和平台表态
* 可以分享文章到微信/微博/豆瓣/印象笔记/Linkedin
* 支持Hexo等其他Markdown源文件的导入
* 支持文章的语法高亮
* 可以增加个人设置(设置头像，个人介绍，添加Github等链接)
* 支持定制导航栏
* 支持RSS/Sitemap
* 相关文章推荐(根据相似标签)
* 响应式设计
* 支持评论提及邮件
* 支持 Github Cards. 具体用法请看 [这里](#github-cards)
* 文章内容(除代码部分之外)自动「盘古之白」

## Github Cards

文章中支持引用Github User/Repo Card，代码源于[Github Cards](https://github.com/lepture/github-cards)，对样式做了微调，感恩~

效果: [我的博客](https://www.dongwm.com/page/about-blog)

在文章中可以这么用:

<pre>
```card
{
  'user': 'dongweiming',
  'repo': 'lyanna',
  'right': 1
}
```
</pre>

card是lang，内容是json数据，你需要确保它可以作为参数让`ast.literal_eval`正常执行。其中`user`是必选键值对，包含`repo`会从`user`里面搜索这个`repo`，找不到的话会「Not Found」。`right`项是为了让Card向右对齐(默认向左对齐)

## Showcase

这些博客使用了Lyanna:

- [薄荷盐的博客](https://www.boheyan.cn/)
- [Yaoyao's Blog](http://www.liu-yao.com/)
- [熊清亮的博客](https://seealso.cn/)
- [Vimiix's Blog](https://vimiix.com)

## Video

[My blog](https://youtu.be/rHYvrefjZwg)

[My blog's Admin page](https://youtu.be/iZCGTvC1NPo)
