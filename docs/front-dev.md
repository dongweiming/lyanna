# 前端开发

博客的前端分2部分

## 后台和博客的Javascript

使用 Webpack+ES6+Sass ，首先需要安装依赖:

```bash
yarn install
```

接着启动开发环境:

```bash
yarn run start
```

修改src目录下代码即可看到效果

## 博客的CSS

修改static/css下非`min.css`后缀的CSS文件，然后执行如下命令合并和压缩:

```
python manage.py build-css
```
