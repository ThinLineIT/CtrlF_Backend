FROM ubuntu:20.04

# home dir 설정
ENV DOCK_ROOT='/home/ubuntu'
ENV DOCK_SRC=$DOCK_ROOT/ctrl-f-be
ENV DOCK_WSGI=$DOCK_ROOT/uwsgi
ENV DEBIAN_FRONTEND noninteractive
ENV PROJECT_ENV production

RUN apt-get -qq update && apt-get -y -qq --no-install-recommends upgrade

# 필수 라이브러리 설치
RUN apt-get install -qq -y --no-install-recommends apt-utils \
    fonts-dejavu \
    gfortran \
    gcc \
    vim \
    git \
    nginx \
    supervisor \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools && \
    pip3 install --upgrade pip && \
    pip install uwsgi && \
    pip install poetry

# 프로젝트 구조 잡기
RUN mkdir $DOCK_ROOT && \
    mkdir $DOCK_SRC && \
    mkdir $DOCK_WSGI

# 필요한 내용 복사 후 라이브러리 설치
#COPY requirements.txt manage.py $DOCK_SRC/
COPY poetry.lock pyproject.toml $DOCK_SRC/
#$(test "$PROJECT_ENV" == production && echo "--no-dev")
RUN cd $DOCK_SRC && poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN cd $DOCK_SRC && pip3 install -r requirements.txt


# 필요한 파일들 옮기기
COPY v2/src $DOCK_SRC/src
RUN cd $DOCK_SRC/src && python3 manage.py migrate

# 웹 서버 설정
RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    cd $DOCK_WSGI
COPY system_settings/uwsgi_params system_settings/uwsgi.ini $DOCK_WSGI/
COPY system_settings/nginx.conf /etc/nginx/sites-available/default
COPY system_settings/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
CMD ["supervisord", "-n"]
