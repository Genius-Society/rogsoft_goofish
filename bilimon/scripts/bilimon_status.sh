#! /bin/sh

source $KSROOT/scripts/base.sh
bilimon_pid=$(pidof bilimon)
LOGTIME=$(TZ=UTC-8 date -R "+%Y-%m-%d %H:%M:%S")
if [ -n "${bilimon_pid}" ]; then
	http_response "【$LOGTIME】bilimon进程运行正常!(PID: ${bilimon_pid})"
else
	http_response "【$LOGTIME】bilimon进程未运行!"
fi
