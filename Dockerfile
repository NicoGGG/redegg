# pull official base image
FROM python:3.11-slim-bookworm

# install nodejs
RUN set -uex; \
    apt-get update; \
    apt-get install -y ca-certificates curl gnupg; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
    | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
    NODE_MAJOR=18; \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
    > /etc/apt/sources.list.d/nodesource.list; \
    apt-get -qy update; \
    apt-get -qy install nodejs;

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

RUN python manage.py tailwind install --no-input

ENTRYPOINT ["/usr/src/app/django-entrypoint.sh"]