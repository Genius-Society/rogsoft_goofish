#!/bin/sh
source /koolshare/scripts/base.sh

rm -rf /koolshare/bilimon
rm -rf /koolshare/bilimon*
rm -rf /koolshare/bin/scripts
rm -rf /koolshare/res/icon-bilimon.png
rm -rf /koolshare/scripts/bilimon*
rm -rf /koolshare/webs/Module_bilimon.asp
rm -rf /tmp/bilimon*

dbus remove bilimon_period
dbus remove bilimon_mail
dbus remove bilimon_smtp
dbus remove bilimon_tmp
dbus remove bilimon_cookie

dbus remove bilimon_version
dbus remove softcenter_module_bilimon_version
dbus remove softcenter_module_bilimon_description
dbus remove softcenter_module_bilimon_install
dbus remove softcenter_module_bilimon_name
dbus remove softcenter_module_bilimon_title
