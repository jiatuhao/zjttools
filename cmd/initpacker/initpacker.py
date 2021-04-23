#!/usr/bin/env python
# coding=utf-8
# Filename: cachesvnltool.py
# Author:   <zhoujiatu@playcrab.com>
# Description: File description
import time
import os
import json
import click
import shutil
import tempfile
from tempfile  import TemporaryFile,NamedTemporaryFile
encoding = 'utf-8'

import paramiko  # 用于调用scp命令
from scp import SCPClient
 
 
# 将指定目录的图片文件上传到服务器指定目录
# remote_path远程服务器目录
# file_path本地文件夹路径
# img_name是file_path本地文件夹路径下面的文件名称
def upload_dir(ip, src_dir, dest_dir):
    host = ip  #服务器ip地址
    print("host:"+host)
    port = 22  # 端口号
    username = "playcrab"  # ssh 用户名
    password = "wanxie@2016"  # 密码
    
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(host, port, username, password)
    scpclient = SCPClient(ssh_client.get_transport(),socket_timeout=15.0)
    
    cur_list = os.listdir(src_dir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(cur_list)):
        src_path = os.path.join(src_dir, cur_list[i])
        dest_path = os.path.join(dest_dir, cur_list[i])
        try:
            scpclient.put(src_path, dest_path)
        except FileNotFoundError as e:
            print(e)
            print("系统找不到指定文件" + src_path)
        else:
            print(src_path+"  upload success!")

    cmd = "cd ~/ | python ./tagserver.py"
    print("执行命令："+cmd)
    ssh_client.exec_command(cmd)
    ssh_client.close()


@click.command()
@click.option('--ip', required=True, help=u'内网打包机ip')
@click.option('--url',required= True, help=u'内网打包机钉钉tag提醒网址')
@click.option('--luapath',required= True, help=u'内网打包机lua目录绝对路径')
@click.option('--code',required= True, help=u'项目代号')
def execute(**options):
    u'''生成googleplay obb包(小包apk+obb资源扩展包模式)'''
    CONFIG = {}
    CONFIG["ip"] = options["ip"]
    CONFIG["url"] = options["url"]
    CONFIG["luapath"] = options["luapath"]
    CONFIG["code"] = options["code"]
    cur_path = os.path.abspath(__file__)
    p,f = os.path.split(cur_path)
    configfile = os.path.join(p, "copyfiles", CONFIG["code"],".configfile")
    f1 = NamedTemporaryFile()
    with open(f1.name , "w+") as jsonFile:
        jsonFile.write(json.dumps(CONFIG))
    shutil.copy(f1.name, configfile)
        
    rootdir = os.path.join(p, "copyfiles", CONFIG["code"])
    upload_dir(CONFIG["ip"], rootdir, "~/")
    
    # global VERSION_CODE
    # VERSION_CODE = options["vcode"]
    # global BUILD_VERSION 
    # BUILD_VERSION = options["bversion"]
    # baseDir = os.path.dirname(srcApk)

    # global BASE_DIR
    # BASE_DIR = baseDir

    # apkName = baseDir + "/src.apk"
    # unpackPath = baseDir + "/test"
    # obbPath = baseDir + "/obb/"

    # dirname = os.path.dirname(os.path.realpath(__file__))
    # src_path = os.path.join(dirname, "lib")
    # dest_path = os.path.join(baseDir, "lib")
    # if not os.path.exists(dest_path):
    #     shutil.copytree(src_path, dest_path)

    # # src_keyStore = os.path.join(dirname, CONFIG["keyStore"])
    # # dest_keyStore = os.path.join(baseDir, CONFIG["keyStore"])
    # # if not os.path.exists(dest_keyStore):
    # #     shutil.copy(src_keyStore, dest_keyStore)

    # global ZIPALIGN_BIN
    # ZIPALIGN_BIN = baseDir + "/lib/zipalign"
    # global SQLITETOOLS_BIN
    # SQLITETOOLS_BIN = baseDir + "/lib/sqlitetools"

    # global RESLIB_KEY
    # RESLIB_KEY = options["dbkey"]

    # global OUTPUT_DIR 
    # OUTPUT_DIR = options["output"]

    # if OUTPUT_DIR == None or OUTPUT_DIR == "":
    #     OUTPUT_DIR = baseDir + "/output"
    #     if not os.path.isdir(OUTPUT_DIR):
    #         os.mkdir(OUTPUT_DIR)

    # tmp_name = os.path.basename(srcApk)
    # tmp_name_array = os.path.splitext(tmp_name)
    # OUTPUT_DIR = os.path.join(OUTPUT_DIR, tmp_name_array[0])
    # print(OUTPUT_DIR)
    # if not os.path.isdir(OUTPUT_DIR):
    #     os.mkdir(OUTPUT_DIR)
    # if not os.path.isdir(OUTPUT_DIR):
    #     print "输出目录不存在:".decode("utf-8") + OUTPUT_DIR
    #     return

    # # 重置环境
    # def resetEnv():
    #     if os.path.exists(apkName):
    #         subprocess.check_call("rm -R " + apkName,shell=True)
    #     if os.path.exists(unpackPath):
    #         subprocess.check_call("rm -R " + unpackPath,shell=True)
    #     if os.path.exists(obbPath):
    #         subprocess.check_call("rm -R " + obbPath,shell=True)

    # resetEnv()
    
    # beginTime = time.time()
    # # 拷贝apk包
    # print "do copy apk ..."
    # shutil.copy(srcApk,apkName)
    # # 解压apk包
    # print "do unpack apk ..."
    # unzip(apkName,unpackPath)
    # #移动资源（检测资源包大小）
    # print "do move res ..."
    # moveRes(unpackPath,obbPath)
    # # 更新relib
    # updateReslib(baseDir,obbPath,unpackPath + "/assets/reslib")
    # generateResultPackage()
    # # # 重置环境
    # resetEnv()
    # print "##total cost time=" + str(time.time() - beginTime)

if __name__ == '__main__':
    execute()
