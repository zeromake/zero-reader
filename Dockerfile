FROM alpine:3.7

ENV TZ Asia/Shanghai
ENV PYTHONIOENCODING utf8

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN apk --no-cache add gcc g++ make python3 py3-pip python3-dev py3-psycopg2 py3-psutil py3-lxml tzdata

RUN mkdir -p /data/config/
RUN mkdir -p ~/.pip && echo -e "[global]\ntimeout = 6000\nindex-url = https://pypi.doubanio.com/simple\n\n[install]\nuse-mirrors = true\nmirrors = https://pypi.doubanio.com/simple\ntrusted-host = pypi.doubanio.com" > ~/.pip/pip.conf
# RUN pip install pipenv

WORKDIR /data/
COPY requirements.txt /data/
RUN pip3 install -r ./requirements.txt

COPY ./web_app/ /data/web_app/
COPY ./dist/ /data/dist/
COPY ./form/ /data/form/
COPY main.py /data/

CMD [ "python3", "./main.py" ]
