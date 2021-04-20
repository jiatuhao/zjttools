#!/usr/bin/env python
# coding=utf-8
# Filename: cachesvnltool.py
# Author:   <zhoujiatu@playcrab.com>
# Description: File description
import sys
import os, os.path
import requests
import json
import subprocess
from subprocess import Popen, PIPE, STDOUT
reload(sys)  
sys.setdefaultencoding('utf8')

class Logging:
    # TODO maybe the right way to do this is to use something like colorama?
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    MAGENTA = '\033[35m'
    RESET = '\033[0m'

    @staticmethod
    def _print(s, color=None):
        if color and sys.stdout.isatty() and sys.platform != 'win32':
            print color + s + Logging.RESET, 
        else:
            print s, 

    @staticmethod
    def debug(s):
        Logging._print(s, Logging.MAGENTA)

    @staticmethod
    def info(s):
        Logging._print(s, Logging.GREEN)

    @staticmethod
    def warning(s):
        Logging._print(s, Logging.YELLOW)

    @staticmethod
    def error(s):
        Logging._print(s, Logging.RED)

def _dingding_notify(work, content, url):
    HEADERS = {
        "Content-Type": "application/json ;charset=utf-8 "
    }
    content = work + ": " + content
    String_textMsg = json.dumps({ "msgtype": "text", "text": {"content": content}})
    try:
        req = requests.post(url, data=String_textMsg, headers=HEADERS, timeout=30)
        if req.ok:
            print("发送了钉钉消息:{}".format(content))
            print(req.ok)
    except Exception as ex:
        print("发送钉钉通知失败: {}  {}".format(work, content))
        print(ex)

def filter(line):
	filter_list = ["PackupTask input pic_list is empty"]
	for k in filter_list:
		if line.find(k) != -1:
			return False
	return True
def run():
	cmd = '''cd /Users/playcrab/Documents/svn/kosdt/kosres_online
xrun synclocal -b online -d /Users/playcrab/Documents/svn/kosdt/data/online/online.20200107 -r /Users/playcrab/Documents/svn/kosdt/kosres_online -o /Users/playcrab/Documents/svn/kosdt/DTOnlineEnvironment/Resources -l kosdt_newonline --updatalua --updatadata --updatares --comitsvn --dingding'''

	need_warning_lines = []
	setting = {"error":[Logging.error,True],"warning":[Logging.warning,False],"svn: e":[Logging.error,True]}

	proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
	for line in iter(proc.stdout.readline, b''):
		flag = False
		for k in setting:
			info = setting[k]
			if line.lower().find(k) != -1:
				info[0](line)
				flag = True
				if info[1] == True and filter(line):
					need_warning_lines.append(line)
				break

		if flag == False:
			Logging.info(line)

		if not subprocess.Popen.poll(proc) is None:
			if line == "":
				break
	proc.stdout.close()
	if len(need_warning_lines)>0:
		print "需要注意的错误提示:"
		for k in need_warning_lines:
			Logging.error(k)
		_dingding_notify("synclocal", 
		    "新的KOS内网测试环境打包有报错信息:\n"+"\n".join(need_warning_lines),
		    "https://oapi.dingtalk.com/robot/send?access_token=11ab6ad8259cddabf86e59de8ce47472ba32c44e451bfce59d1b5e35b8a8aeff"
		    )
run()
