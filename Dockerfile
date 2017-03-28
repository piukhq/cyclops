FROM ubuntu:xenial
MAINTAINER Chris Pressland <cp@bink.com>

ADD . /usr/local/src/cyclops

RUN addgroup --gid 1550 apps && \
 adduser --system --no-create-home --uid 1550 --gid 1550 apps && \
 apt-get update && \
 apt-get -y install rsync python3 python3-pip curl && \
 curl -L 'https://github.com/just-containers/s6-overlay/releases/download/v1.18.1.5/s6-overlay-amd64.tar.gz' -o /tmp/s6-overlay-amd64.tar.gz && \
 tar xzf /tmp/s6-overlay-amd64.tar.gz -C / && \
 rsync -a --remove-source-files /usr/local/src/cyclops/docker_root/ / && \
 pip3 install --upgrade pip && \
 pip3 install -r /usr/local/src/cyclops/requirements.txt && \
 chown apps:apps /usr/local/src -R && \
 apt-get -y autoremove rsync curl && \
 apt-get clean && \
 rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["/init"]
