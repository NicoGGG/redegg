# pull official base image
FROM python:3.11-alpine

# set work directory
WORKDIR /usr/src/app
COPY ./requirements.txt /usr/src/app/requirements.txt

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./scripts/django-entrypoint.sh /usr/src/app/django-entrypoint.sh
COPY ./scripts/celery-entrypoint.sh /usr/src/app/celery-entrypoint.sh

# copy project
COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/django-entrypoint.sh"]