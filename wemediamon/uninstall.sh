#!/bin/sh
source /koolshare/scripts/base.sh

rm -rf /koolshare/wemediamon
rm -rf /koolshare/wemediamon*
rm -rf /koolshare/bin/scripts
rm -rf /koolshare/res/icon-wemediamon.png
rm -rf /koolshare/res/wemediamon.*
rm -rf /koolshare/scripts/wemediamon*
rm -rf /koolshare/webs/Module_wemediamon.asp
rm -rf /tmp/wemediamon*

for key in $(dbus listall | grep 'wemediamon_' | cut -d '=' -f1); do
    dbus remove "$key"
done
