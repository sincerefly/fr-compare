FROM keymetrics/pm2:latest-alpine

WORKDIR /opt

# Bundle APP files
COPY fr-compare-2.0.py .
COPY pm2.json .

RUN apk add --update \
    cmake \
    gcc \
    g++ \
    python \
    python-dev \
    py-pip \
    build-base \
    jpeg-dev \
    zlib-dev \
    && rm -rf /var/cache/apk/*

RUN pip install \
    gevent \
    flask \
    requests \
    face_recognition


# Show current folder structure in logs
RUN ls -al -R

#CMD [ "python", "detect-face-server-fr-2.0.py" ]
CMD [ "pm2-runtime", "start", "pm2.json" ]

EXPOSE 8726


