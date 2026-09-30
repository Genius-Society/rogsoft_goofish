#! /bin/sh

source $KSROOT/scripts/base.sh
goofish_pid=$(ps w | grep python | grep Start.py | grep -v grep | awk '{print $1}')
LOGTIME=$(TZ=UTC-8 date -R "+%Y-%m-%d %H:%M:%S")
if [ -n "${goofish_pid}" ]; then
	http_response "【$LOGTIME】goofish 进程运行正常! (Python: ${goofish_pid})"
else
	http_response "【$LOGTIME】goofish 进程未运行!"
fi
