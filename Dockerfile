FROM python:3.8-slim

WORKDIR /var/app
ADD Pipfile /var/app/Pipfile
ADD Pipfile.lock /var/app/Pipfile.lock

ENV FETCH_PACKAGES="wget gnupg2" \
    BUILD_PACKAGES="build-essential gcc linux-headers-amd64 libffi-dev libgeos-c1v5 libpq-dev libssl-dev" \
    PACKAGES="postgresql-client"


RUN apt update && \
    apt install -y ${FETCH_PACKAGES}

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt update && apt upgrade -y
RUN apt install -y --no-install-recommends ${BUILD_PACKAGES} ${PACKAGES}
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -U pipenv

RUN pipenv install --deploy --system
RUN apt purge -y ${BUILD_PACKAGES} && \
    apt purge -y ${FETCH_PACKAGES} && \
    apt autoremove -y

ADD . /var/app
ENV PYTHONPATH "${PYTHONPATH}:/var/app/app"