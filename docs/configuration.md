# 配置项

全部配置项都在 config.py 中可以找到

## DB_URL

- 默认值：`mysql://root:@localhost:3306/test?charset=utf8`

设置数据库的URL

## DEBUG

- 默认值：`False`

是否开启DEBUG模式，开启后可以看到详细错误，修改代码后不用重启就可以autoreload

## WTF_CSRF_SECRET_KEY

- 默认值：`123`

Sanic-wtf 需要的 CSRF KEY

## MEMCACHED_HOST

- 默认值: `127.0.0.1`

Memcached的主机名或者IP

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

## AUTHOR

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

可以定制导航栏，具体默认值可以看 config.py

## BEIAN_ID

可以设置ICP备案号
