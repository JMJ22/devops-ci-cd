#!/bin/bash

set -e

IMAGE_NAME=meuapp:dev

case "$1" in
  build)
    docker build -t $IMAGE_NAME .
    ;;
  run)
    docker run --rm -it $IMAGE_NAME
    ;;
  test)
    docker run --rm -it $IMAGE_NAME pytest
    ;;
  shell)
    docker run --rm -it $IMAGE_NAME /bin/bash
    ;;
  full)
    $0 build
    $0 test
    $0 run
    ;;
  *)
    echo "Uso: $0 {build|run|test|shell|full}"
    exit 1
    ;;
esac
