#!/usr/bin/env bash

# Check supervisor exists
running=`ps -ef | grep supervisor`

if [ $running -gt 0 ]; then
    supervisorctl stop $1
    exit 0
fi

apt update
apt install -y supervisor

cp ./supervisord.conf /etc/supervisor/
/etc/init.d/supervisor start
