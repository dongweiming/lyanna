# 配置项

全部配置项都在 config.py 中可以找到。但是从3.0版本开始不再使用`local_settings.py`存放配置，统一使用`config.yaml`，具体可以看`config.yaml.tmpl`样板文件中的设置项

## DB_URL

- 默认值：`mysql://root:@localhost:3306/test?charset=utf8`

设置数据库的URL，另外也支持从环境变量读取

## DEBUG

- 默认值：`False`

是否开启DEBUG模式，开启后可以看到详细错误，修改代码后不用重启就可以autoreload。另外也支持从环境变量读取

## REDIS_URL

- 默认值: `redis://localhost:6379`

Redis服务器地址，另外也支持从环境变量读取

## WTF_CSRF_SECRET_KEY

- 默认值：`123`

Sanic-wtf 需要的 CSRF KEY

## MEMCACHED_HOST

- 默认值: `127.0.0.1`

Memcached的主机名或者IP，另外也支持从环境变量读取

## MEMCACHED_PORT

- 默认值: `11211`

Memcached的端口

## redirect_uri

- 默认值: `http://127.0.0.1:8000/oauth`

在Github申请的应用的回调地址，如果只是使用默认的 http://127.0.0.1:8000 不需要改变

## client_id

- 默认值: `098a2e6da880878e05da`

Github申请的应用client_id，如果只是使用默认的 http://127.0.0.1:8000 不需要改变

## client_secret

- 默认值: `854cc0d86e61a83bb1dd00c3b23a3cc5b832d45c`

Github申请的应用client_secret，如果只是使用默认的 http://127.0.0.1:8000 不需要改变

## REACT_PROMPT

- 默认值: `喜欢这篇文章吗? 记得给我留言或订阅哦`

文章下的默认提示语

## SHOW_PROFILE

- 默认值: `False`

是否显示个人设置项，开启后需要通过后台配置

注意: 这会改变主要的布局！

## OWNER

- 默认值: `xiaoming`

指定博客作者名字

## SITE_TITLE

- 默认值: `My Blog`

指定博客标题

## PER_PAGE

- 默认值: `10`

首页文章列表每页文章数量

## GOOGLE_ANALYTICS

- 默认值: `''`

指定GA，为空表示不开启

## SENTRY_DSN

- 默认值: `''`

指定Sentry的DSN(Data Source Name)，为空表示不追踪错误堆栈

## SITE_NAV_MENUS

可以定制导航栏，每项参数最少2个(Endpoint, Name)，最多5个(Endpoint, Name, FontAwesome icon, 颜色)，具体默认值可以看 config.py

## BEIAN_ID

可以设置ICP备案号

## JWT_SECRET

- 默认值: `lyanna`

JWT的秘钥

## EXPIRATION_DELTA

- 默认值: `3600(秒)`

JWT的超时时间

## MAIL_SERVER

- 默认值: `smtp.qq.com`

用来发邮件的SMTP服务器主机，为空将不会发邮件

## MAIL_PORT

- 默认值: `465`

用来发邮件的SMTP服务端口

## MAIL_USERNAME

- 默认值: `''`

用来发邮件的账号，为空将不会发邮件

## MAIL_PASSWORD

- 默认值: `''`

用来发邮件的账号密码，为空将不会发邮件

## BLOG_URL

- 默认值: `https://example.com`

博客的地址，在提及邮件中可以直接访问博客对应文章页面

## SHOW_PAGEVIEW

- 默认值: `False`

是否显示文章阅读量(PV)，建议有一定访问量后再显示出来

## PERMALINK_TYPE

- 默认值: `slug`

文章页面URL的类型。可选值: id、slug、title。举个例子, PERMALINK_TYPE为id时，首页、分类页、标签页等页面都会使用`https://example.com/post/{id}`这样效果的URL，帮助SEO。

## REDIS_SENTINEL_SERVICE_HOST

- 默认值: `None`

除了用上面提到的`REDIS_URL`指定Redis服务器，还可以用分布式的Redis Sentinel集群架构，本项指定主机地址，默认不开启。另外也支持从环境变量读取

## REDIS_SENTINEL_SERVICE_PORT

- 默认值: `26379`

Redis Sentinel集群架构，本项指定主机端口号。另外也支持从环境变量读取

## SHOW_AUTHOR

- 默认值: `False`

文章页可以显示发布文章的用户信息(名字、头像)，目前还不提供链接到用户详情页

## USE_FFMPEG

动态可以上传视频，如果服务器上安装了ffmpeg可以在上传后自动截取封面并且获得视频大小，这样让用户访问体验更好。本项会自动根据是否安装ffmpeg决定，为了在启动时给博主提示，改变此项无意义

## CDN_DOMAIN

- 默认值: `''`

为了更好地访问效果，博客内的静态文件(Javascript/css/img/fonts等)地址可以使用CDN的域名，默认不开启
