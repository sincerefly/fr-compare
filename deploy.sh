#!/bin/bash

version=$1

if [ x$1 != x ] ; then
  echo "build v$1"
else
  echo "Incorrect Usage : Arguments mismatch."
  echo "Usage:"
  echo "  ./deploy.sh 2.0.0"
  exit 2
fi

echo "[1/4] rmi old image"
sudo docker rmi -f fr-compare:$1
echo "[2/4] unzip image"
tar xvf fr-compare-"$version".tar.bz2
echo "[3/4] load image"
sudo docker load --input fr-compare-$version.tar
echo "[4/4] start image"
sudo docker run --restart=always --name fr-compare -d -p 8726:8726 fr-compare:$version
echo "[info] deploy success"
