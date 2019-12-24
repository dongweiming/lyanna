# 快速开始

## 安装

首先确保要使用的CPython版本>=3.6，接着克隆项目:

```bash
git clone https://github.com/dongweiming/lyanna
cd lyanna
```

安装依赖:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 准备环境

[重要]你需要确保安装并启动如下软件：

1. MySQL
2. Memcached
3. Redis

### 初始化

安装依赖后，需要做一些初始化工作：

```bash
python manage.py initdb  # 初始化数据库，创建表结构和索引
python manage.py adduser --name YOUR_NAME --password YOUR_PASS --email YOUR_EMAIL  # 创建可登录后台的管理员账号
# 可选，如果你之前已经有博客，想把之前写的Markdown文章导入，如果是Hexo，灰常好，
# 用下面脚本就可以，如果是其他系统可以按对应逻辑自己写写
python hexo-exporter.py Markdown文件目录1 Markdown文件目录1 --uid=1  # uid是上面创建的管理员账号ID
```

添加自己的配置项到local_settings.py文件中，具体选项可以看👉 [配置项](configuration.md)

最后启动应用就好啦:

```bash
python app.py
```

如果你要部署到自己的服务器上，可以参考 [部署](deploying.md)

## v3.0不兼容问题

在v3.0添加了动态功能，如果之前你已经使用的版本>2.7，可以通过如下命令完成迁移:

```bash
python manage.py migrate-for-v30
```

如果版本<=2.7看下面👇

## v2.7不兼容问题

在v2.5时有做了很多修改，如果之前你已经使用的版本>=2.5，可以通过如下命令完成迁移:

```bash
python manage.py migrate-for-v27
```

如果版本<2.5看下面👇

## v2.5不兼容问题

在v2.5时修改了`posts`表结构，如果之前你已经使用了lyanna，升级后会找不到新加的字段，报错如下:

```python
...
tortoise.exceptions.OperationalError: (1054, "Unknown column 'pageview' in 'field list'")
```

可以通过如下命令修改:

```bash
python manage.py migrate-for-v25
```

## 联系我

> - [GitHub](https://github.com/dongweiming "github")
> - [ciici123@gmail.com](mailto:ciici123@gmail.com)

[![QQ群](https://img.shields.io/badge/QQ%E7%BE%A4-522012167-yellowgreen.svg)](https://jq.qq.com/?_wv=1027&k=5RS89BW)
