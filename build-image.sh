#!/bin/bash

version=$1

[ -f "fr-compare-$version.tar" ] && rm "fr-compare-$version.tar"
[ -f "fr-compare-$version.tar.bz2" ] && rm "fr-compare-$version.tar.bz2"

if [ x$1 != x ] ; then
  echo "build v$1"
else
  echo "Incorrect Usage : Arguments mismatch."
  echo "Usage:"
  echo "  ./build-image.sh 2.0.0"
  exit 2
fi

echo "[1/4] rmi old image"
sudo docker rmi -f fr-compare:$1
echo "[2/4] build image"
sudo docker build -t fr-compare:$1 .
echo "[3/4] export image"
sudo docker save fr-compare:$version > fr-compare-$version.tar
echo "[4/4] compression image"
tar zcvf fr-compare-"$version".tar.bz2 fr-compare-"$version".tar
echo "[info] build success"
