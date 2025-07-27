#!/bin/sh
source /koolshare/scripts/base.sh

rm -rf /koolshare/wemediamon
rm -rf /koolshare/wemediamon*
rm -rf /koolshare/bin/scripts
rm -rf /koolshare/res/icon-wemediamon.png
rm -rf /koolshare/scripts/wemediamon*
rm -rf /koolshare/webs/Module_wemediamon.asp
rm -rf /tmp/wemediamon*

dbus remove wemediamon_enable
dbus remove wemediamon_mail
dbus remove wemediamon_period
dbus remove wemediamon_smtp
dbus remove wemediamon_tmp
dbus remove wemediamon_cookie

dbus remove wemediamon_version
dbus remove softcenter_module_wemediamon_description
dbus remove softcenter_module_wemediamon_install
dbus remove softcenter_module_wemediamon_name
dbus remove softcenter_module_wemediamon_title
dbus remove softcenter_module_wemediamon_version
