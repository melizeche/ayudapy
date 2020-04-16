FROM python:3.7-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
apt-get install gdal-bin postgresql-client -y

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8000
