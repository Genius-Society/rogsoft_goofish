#!/bin/sh
source /koolshare/scripts/base.sh

dbus set wemediamon_enable=0
sh /koolshare/scripts/wemediamon_config.sh
find /tmp/upload/ -name '*wemediamon*' -print0 | xargs -0 rm -rf
find /koolshare/ -name '*wemediamon*' -print0 | xargs -0 rm -rf

for key in $(dbus listall | grep 'wemediamon_' | cut -d '=' -f1); do
    dbus remove "$key"
done
