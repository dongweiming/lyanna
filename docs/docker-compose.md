为了方便本地开发和起demo体验效果，可以使用[Docker Compose](https://docs.docker.com/compose/)在Docker里面开发。在这种模式下数据库、Nginx、Memcached、Redis、lyanna应用等都在独立的容器中，一个命令全部启动:

```bash
❯ docker-compose up  # 可以加 -d 后台运行
Starting lyanna_memcached_1 ...
Starting lyanna_memcached_1 ... done
Starting lyanna_redis_1     ... done
Starting lyanna_web_1       ... done
Attaching to lyanna_db_1, lyanna_redis_1, lyanna_memcached_1, lyanna_web_1
...
web_1        | Init Finished!
web_1        | User admin created!!! ID: 1
web_1        | [2019-11-25 20:59:26 +0000] [1] [DEBUG]
web_1        |
web_1        |                  Sanic
web_1        |          Build Fast. Run Fast.
web_1        |
web_1        |
web_1        | [2019-11-25 12:59:26 +0000] [1] [INFO] Goin' Fast @ http://0.0.0.0:8000
web_1        | [2019-11-25 12:59:27 +0000] [19] [INFO] Starting worker [19]
```

容器可以随意创建和销毁，不会对本机环境有影响。这样访问 http://localhost:8000 就可以访问开发服务器了，本地修改代码会同步进容器直接生效。

## 相关文章

文章不是Docker和Docker compose的教程，你需要看官方文档，也推荐看下面列出的文章:

1. [Python项目容器化实践(一) - Docker Compose](https://www.dongwm.com/post/use-docker-compose/)
