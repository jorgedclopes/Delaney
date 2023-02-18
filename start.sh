#!/bin/bash

# docker container stop delaney && docker container rm delaney && ./start.sh 0.0
# docker logs -n 20 delaney

VERSION=$1
python3 -m src.google_client.bot
docker build . --file Dockerfile --tag carequinha/delaney:"$VERSION"
docker run -d --name delaney --restart always carequinha/delaney:"$VERSION"