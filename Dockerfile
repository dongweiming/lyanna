FROM python:3.7-alpine AS build
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk add git gcc musl-dev libffi-dev openssl-dev make
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn -r /requirements.txt \
    && mkdir -p /install/lib/python3.7/site-packages \
    && cp -rp /usr/local/lib/python3.7/site-packages /install/lib/python3.7

FROM python:3.7-alpine
COPY --from=build /install/lib /usr/local/lib
COPY --from=build /install/src /usr/local/src
WORKDIR /app
COPY . /app
COPY --from=build /usr/local/bin/gunicorn /app/gunicorn
COPY --from=build /usr/local/bin/arq /app/arq