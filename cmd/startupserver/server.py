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

def handle_autotag_master():
    try:
        data = os.popen("sh /Users/playcrab/autotag.sh kosdt_master /Users/playcrab/Documents/svn/koslua").read()
        startIdx = data.find("tag:")
        endIdx = data.find("\n", startIdx)
        tag = data[startIdx+4:endIdx]
        _dingding_notify("newtag", 
            "新tag是:"+tag,
            "https://oapi.dingtalk.com/robot/send?access_token=6bea31231b6b645838e8c3db433683fef297deb42ee543497534f407781d6395"
            )
    except Exception as e:
        print (e)

def handle_autotag_preonline():
    try:
        data = os.popen("sh /Users/playcrab/autotag.sh kosdt_preonline /Users/playcrab/Documents/svn/koslua").read()
        startIdx = data.find("tag:")
        endIdx = data.find("\n", startIdx)
        tag = data[startIdx+4:endIdx]
        _dingding_notify("newtag", 
            "新tag是:"+tag,
            "https://oapi.dingtalk.com/robot/send?access_token=6bea31231b6b645838e8c3db433683fef297deb42ee543497534f407781d6395"
            )
    except Exception as e:
        print (e)

def handle_autotag_online():
    try:
        data = os.popen("sh /Users/playcrab/autotag.sh kosdt_newonline /Users/playcrab/Documents/svn/koslua").read()
        startIdx = data.find("tag:")
        endIdx = data.find("\n", startIdx)
        tag = data[startIdx+4:endIdx]
        _dingding_notify("newtag", 
            "新tag是:"+tag,
            "https://oapi.dingtalk.com/robot/send?access_token=6bea31231b6b645838e8c3db433683fef297deb42ee543497534f407781d6395"
            )
    except Exception as e:
        print (e)

cmd_list = {
    "master":handle_autotag_master,
    "preonline":handle_autotag_preonline,
    "online":handle_autotag_online,
}


###接收回调内容 并进行解析和响应 
def handle_client(client):
    data = client.recv(BUFSIZE)   
    string = bytes.decode(data, encoding) 
    split_result = string.split("\r\n")

    split_result1 = split_result[0].split(" ")
    if len(split_result1)>1:
        # print(split_result1)
        cmd = split_result1[1].replace("/?", "")
        # print(cmd)
        if cmd_list.has_key(cmd):
            cmd_func = cmd_list[cmd]
            if cmd_func != None:
                cmd_func()
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
    g_cmd = None
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 9011))  ##绑定ip和端口
    server_socket.listen(0)
    while True:
        client, cltadd = server_socket.accept()
        handle_client(client)
