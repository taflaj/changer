#! /usr/bin/env bash

# Uncomment the next line for debugging
# set -x

if [ $# -ne 1 ]; then
    echo "Usage: $0 <target folder>"
    exit
fi

deploy() {
    mkdir -p $2
    diff $1 $2/$1 > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        cp -pv $1 $2
    fi
}

deploy changer.py $1
deploy modules/changer.py $1/modules
deploy modules/system.py $1/modules
deploy modules/models/models.py $1/modules/models
deploy modules/models/db/sqlite.py $1/modules/models/db
deploy scripts/desktop.sh $1/scripts
deploy scripts/sysinfo.sh $1/scripts
deploy scripts/wallpaper.sh $1/scripts
