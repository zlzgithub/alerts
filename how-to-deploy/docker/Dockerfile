FROM python:2

ARG SERVER_URL
ARG LISTEN_80_443

ENV APP_HOME=/var/opt/alerts \
    SERVER_URL=${SERVER_URL:-"http://alerts.keep.com/"} \
    LISTEN_80_443=${LISTEN_80_443:-no}

WORKDIR $APP_HOME
VOLUME data
COPY ./conf.d   .
COPY ./main     main

RUN mkdir -p $APP_HOME/logs && \
    mkdir -p $APP_HOME/pid && \
    mkdir -p $APP_HOME/data && \
    mkdir -p $APP_HOME/config/celery && \
    mkdir -p $APP_HOME/config/logs && \
    mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo "deb http://mirrors.aliyun.com/debian stretch main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security stretch/updates main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian stretch-updates main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev nginx supervisor vim -y && \
    apt-get clean && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -U pip && \
    cd $APP_HOME/main && \
    pip install -r requirements.txt && \
    cd $APP_HOME/main/vendor/django-celery-results-master && \
    python setup.py build && \
    python setup.py install && \
    cp $APP_HOME/nginx/*.conf /etc/nginx/conf.d/ && \
    cp $APP_HOME/supervisor/*.conf /etc/supervisor/conf.d/ && \
    chmod +x $APP_HOME/start.sh

EXPOSE 8080
CMD ["./start.sh"]
