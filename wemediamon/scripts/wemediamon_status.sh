#! /bin/sh

source $KSROOT/scripts/base.sh
wemediamon_pid=$(ps w | grep python | grep wemediamon.py | grep -v grep | awk '{print $1}')
LOGTIME=$(TZ=UTC-8 date -R "+%Y-%m-%d %H:%M:%S")
if [ -n "${wemediamon_pid}" ]; then
	http_response "【$LOGTIME】WeMediaMon 进程运行正常! (Python: ${wemediamon_pid})"
else
	http_response "【$LOGTIME】WeMediaMon 进程未运行!"
fi
