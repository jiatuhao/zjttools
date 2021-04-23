#!/usr/bin/env python
# coding=utf-8
# Filename: server.py
# Author:   <zhoujiatu@playcrab.com>
# Description: File description
# -*-coding:u8-*-
import time
import os
import json
import socket
import threading
import requests
import json
encoding = 'utf-8'
BUFSIZE = 102400
CONFIG_JSON_DATA = {}
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

def handle_autotag(params):
    lua_branch = params[1]

    sh_string = "sh ~/autotag.sh "+lua_branch+" "+CONFIG_JSON_DATA["luapath"]
    try:
        data = os.popen(sh_string).read()
        startIdx = data.find("tag:")
        endIdx = data.find("\n", startIdx)
        tag = data[startIdx+4:endIdx]
        _dingding_notify("newtag", 
            "新tag是:"+tag,
            CONFIG_JSON_DATA["url"]
            )
    except Exception as e:
        print (e)

cmd_list = {
    "tag":handle_autotag,
}

###接收回调内容 并进行解析和响应 
def handle_client(client):
    data = client.recv(BUFSIZE)   
    string = bytes.decode(data, encoding) 
    split_result = string.split("\r\n")

    split_result1 = split_result[0].split(" ")
    if len(split_result1)>1:
        print(split_result1)
        cmd = split_result1[1].replace("/?", "")
        cmd_info = cmd.split(":")
        # print(cmd)
        if cmd_list.has_key(cmd_info[0]):
            cmd_func = cmd_list[cmd_info[0]]
            if cmd_func != None:
                cmd_func(cmd_info)
                try:
                    responseHeaderLines = "HTTP/1.1 200 OK\r\n"
                    responseHeaderLines += "\r\n"
                    responseBody = "success!"
                    response = responseHeaderLines + responseBody
                    b_response=response.encode(encoding="utf-8")
                    client.send(b_response)
                except Exception as e:
                    print (e)
            else:
                try:
                    responseHeaderLines = "HTTP/1.1 200 OK\r\n"
                    responseHeaderLines += "\r\n"
                    responseBody = "正在运行命令"+g_cmd+",请稍后"
                    response = responseHeaderLines + responseBody
                    b_response=response.encode(encoding="utf-8")
                    client.send(b_response)
                except Exception as e:
                    print (e)

if __name__ == '__main__':
    cur_path = os.path.abspath(__file__)
    p,f = os.path.split(cur_path)
    configfile = os.path.join(p, ".configfile")
    if os.path.exists(configfile):
        with open(configfile,'r')as fp:
            CONFIG_JSON_DATA = json.load(fp)

        ip_string = CONFIG_JSON_DATA["ip"]
        ip_string = ip_string.encode('unicode-escape').decode('string_escape')
        g_cmd = None
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ip_string, 9011))  ##绑定ip和端口
        server_socket.listen(0)
        while True:
            client, cltadd = server_socket.accept()
            handle_client(client)
    else:
        print("没找到配置文件")
