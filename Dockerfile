FROM selenium/standalone-chrome:4.7.0-20221202

USER seluser

WORKDIR /opt/

RUN sudo sed -i "s@http://.*archive.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && \
    sudo sed -i "s@http://.*security.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && \
    sudo apt-get -y update && sudo apt-get -y --no-install-recommends install python3-pip && \
    sudo rm -rf /var/lib/apt/lists/* /var/cache/apt/*

ADD requirements.txt /opt/requriements.txt

RUN sudo pip config set global.index-url  https://pypi.doubanio.com/simple && \
    sudo pip install -r requriements.txt 

ADD simple-cookieApi.py /opt/simple-cookieApi.py
COPY simple-cookieApi.conf /etc/supervisor/conf.d/

ENV DEVELOPMENT=False

EXPOSE 8000
