FROM nvidia/cuda:10.1-runtime-ubuntu18.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get update \
  && apt-get install 'ffmpeg'\
  'libsm6'\ 
  'libxext6'  -y

WORKDIR /thesis

COPY requirements.txt .

RUN pip3 install -r requirements.txt


