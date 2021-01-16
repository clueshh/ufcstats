FROM alpine:latest

RUN apk add --update \
 build-base \
 python3 python3-dev py3-setuptools py3-pip \
 libffi libffi-dev \
 libxml2 libxml2-dev \
 libxslt libxslt-dev \
 openssl openssl-dev \
 postgresql-dev

COPY requirements.txt /ufcstats/
WORKDIR /ufcstats

RUN pip3 install Cython wheel
RUN pip3 install -r requirements.txt
