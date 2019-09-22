FROM python:3.7-alpine AS build
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk add git gcc musl-dev libffi-dev openssl-dev make
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple -r /requirements.txt \
    && mkdir -p /install/lib/python3.7/site-packages \
    && cp -rp /usr/local/lib/python3.7/site-packages /install/lib/python3.7

FROM python:3.7-alpine
COPY --from=build /install/lib /usr/local/lib
COPY --from=build /install/src /app/src
WORKDIR /app
COPY . /app