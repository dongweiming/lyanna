# 后端开发

首先需要新建一个 local_settings.py 文件，至少设置`DEBUG=True`，可以实现autoreload:

```bash
➜ cat local_settings.py
DEBUG = True
```

启动后调试应用即可:

```bash
python app.py
```
