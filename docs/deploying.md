# 部署

```bash
ansible-playbook deploy.yml --ask-sudo-pass
```

Python应用服务器用了gunicorn(木有用ASGI因为不支持)：

```bash
gunicorn app:app --bind unix:/XXX/lyanna.sock --worker-class sanic.worker.GunicornWorker
```

部署方案是使用 Ansbile:

```bash
ansible-playbook deploy.yml --ask-sudo-pass
```

通过 Ansbile 剧本把 local_settings.py, nginx.conf, supervisor.conf 部署到服务器上。如果要回滚到某个commit，可以这样：

```bash
ansible-playbook deploy.yml --ask-sudo-pass --extra-vars="git_commit_version=THE_COMMIT_VERSION"
```

具体详见 [srv目录](https://github.com/dongweiming/lyanna/tree/master/srv)
