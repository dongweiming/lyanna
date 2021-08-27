# lyanna

[![Build Status](https://app.travis-ci.com/dongweiming/lyanna.svg?branch=master)](https://app.travis-ci.com/github/dongweiming/lyanna)
![Tag](https://img.shields.io/github/v/tag/dongweiming/lyanna)
![Python Version](https://img.shields.io/badge/python-3.8-blue)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

My Blog Using Sanic

[查看文档 📖](https://dongweiming.github.io/lyanna/)

## 版本提示

3.0版本开始已经使用了最新的Python3.8语法，所以如果你不方便升级CPython请使用2.X版本

## Overview

这是一个使用asyncio生态开发的个人技术博客。具体如下：

* Web框架: Sanic
* 模板: Mako/Sanic-Mako
* 数据库: TortoiseORM/aiomysql
* 缓存: aiomcache
* KV数据库: aioredis
* 任务队列: arq
* 代码质量: mypy/flake8/isort/bandit

其他aio扩展: Sanic-Auth、Sanic-wtf、sanic-session、aiotask-context、asyncblink、sanic-sentry、sanic-jwt、aiosmtplib

<p align="center">
  <img width="600" src="./docs/widget.png" >
</p>

管理后台使用: ElementUI + Vue-CLI + Vue-Router + Vuex

<p align="center">
  <img width="600" src="./screenshot/admin.png" >
</p>

Inspired by [vue-element-admin](https://github.com/PanJiaChen/vue-element-admin)

[动态](https://www.dongwm.com/activities) 使用: Vue-CLI + Vue-Router + Vuex

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
* 支持个人设置(如设置头像，个人介绍)
* 支持定制导航栏
* 支持RSS/Sitemap
* 相关文章推荐(根据相似标签)
* 响应式设计
* 支持评论提及邮件
* 支持 Github Cards. 具体用法请看 [这里](#github-cards)
* 文章内容(除代码部分之外)自动「盘古之白」
* 支持「文章专题」
* 支持「动态」
* 可对评论回应
* 支持用Docker Compose本地开发
* 支持kubernetes上运行
* Widget系统，内置aboutme、blogroll、most\_viewed、latest\_comments、tagcloud、html等widget
* 导航栏项可以设置icon和颜色(如RSS)
* 支持配置CDN域名服务静态文件

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
- [榕树下](https://www.ams.pub)
- [读书笔记](http://www.chenvq.cn/)

PS: 如果博主不希望自己的博客出现在此列表中可以各种渠道私信我或者提PR去掉~

## Video

[My blog](https://youtu.be/rHYvrefjZwg)

[My blog's Admin page](https://youtu.be/iZCGTvC1NPo)

## Thanks

[![PyCharm](docs/pycharm.svg)](https://www.jetbrains.com/?from=lyanna)
