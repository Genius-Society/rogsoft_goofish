#!/bin/sh
source /koolshare/scripts/base.sh

dbus set goofish_enable=0
sh /koolshare/scripts/goofish_config.sh
find /tmp/upload/ -name '*goofish*' -print0 | xargs -0 rm -rf
find /koolshare/ -name '*goofish*' -print0 | xargs -0 rm -rf

for key in $(dbus listall | grep 'goofish_' | cut -d '=' -f1); do
	dbus remove "$key"
done
