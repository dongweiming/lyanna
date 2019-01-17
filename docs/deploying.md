# 部署

我的部署方案是使用 Ansbile:

```bash
ansible-playbook deploy.yml --ask-sudo-pass
```

启动应用的方式：

```
gunicorn app:app --bind unix:/XXX/lyanna.sock --worker-class sanic.worker.GunicornWorker --log-file /XXX/lyanna.log
```

通过 Ansbile 剧本把 local_settings.py, nginx.conf, supervisor.conf 部署到服务器上
