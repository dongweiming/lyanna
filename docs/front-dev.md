# 前端开发

博客的前端分3部分。首先确保已经安装了`yarn`

## 博客的Javascript

使用 Webpack+ES6+Sass ，首先需要安装依赖:

```bash
yarn install
```

接着启动开发环境:

```bash
yarn start
```

修改src目录下代码即可看到效果

生产环境需要构建：

```bash
yarn build
```

## 后台

使用 ElementUI+Vue-CLI+Vue-Router+Vuex+Webpack+ES6+Sass ，需要安装依赖：

```bash
cd admin  # 在 admin 子目录下
yarn install
```

接着启动开发环境:

```bash
yarn serve
```

修改src目录下代码即可看到效果

生产环境需要构建：

```
yarn build
```

## 博客的CSS

修改static/css下非`min.css`后缀的CSS文件，然后执行如下命令合并和压缩:

```
python manage.py build-css
```
