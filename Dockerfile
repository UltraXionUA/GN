FROM ubuntu

MAINTAINER ULTRA XION <ultra25813@gmail.com>

RUN apt-get update && apt-get install -y cowsay && ln -s /usr/games/cowsay /usr/bin/cowsay

ENTRYPOINT ["cowsay"]