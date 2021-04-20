#!/usr/bin/env python
# coding=utf-8
# Filename: splitApk.py
# Author:   <zhangyanguang@playcrab.com>
# Desc:拆分walleui生成的apk包,生成google play obb扩展包

''''
    --obb
        |--test(apk解压到此目录)
        |--obb(obb包资源,从test/assets/release下移到该目录)
        |--update.sql(更新reslib的sql文件)
        |--lib
            |--zipalign(apk包4字节对齐工具)
            |--sqlitetools(加密sqlite db操作工具)
'''

import os
import shutil
import sys
import string
import time
import zipfile
import sqlite3
import subprocess
import click


CONFIG = {
    "packageName" : "com.onepunchman.ggplay.vn",
    "keyStore" : "google.keystore",
    "storepass": "123456",
    "keyAlias" : "tronghv",
    "packageSize" : 60
}


def getdirsize(dir):  
   size = 0L  
   for root, dirs, files in os.walk(dir):  
      size += sum([os.path.getsize(os.path.join(root, name)) for name in files])  
   return size

def unzip(zipName,desDir):
    r = zipfile.is_zipfile(zipName)
    if r:
        starttime = time.time()
        fz = zipfile.ZipFile(zipName,'r')
        for file in fz.namelist():
            fz.extract(file,desDir)
        endtime = time.time()
        times = endtime - starttime
    # print('times' + str(times))

def zipApk(zipDir,maxSize):
    zipDesFile = zipDir +'.zip'
    f = zipfile.ZipFile(zipDesFile,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(zipDir):
        for filename in filenames:
            f.write(os.path.join(dirpath,filename))
    f.close()
    fileSize = os.path.getsize(zipDesFile)/1000000
    os.remove(zipDesFile)    
    if fileSize <= maxSize :
        # os.rename(zipDesFile, zipDir +'.apk')
        return True
    else:
        return False

# 将资源移到obb中，直到剩余资源小于等于mini安装包设定的大小
def moveRes(resDir,desDir):
    resPath = resDir + "/assets/release/"
    for i in range(520,-1,-1):
        tailStr = str(i)
        if i < 100 and i >= 10:
            tailStr = "0" + tailStr
        if i < 10:
            tailStr = "00" + tailStr
        filePath = resPath + tailStr
        if os.path.exists(filePath):
            shutil.move(filePath,desDir + tailStr) 
        else:
            pass
        print "move file ===== >>>> " + filePath
        curSize = getdirsize(resDir)/1000000
        print "current packageSize ====== " + str(curSize)
        if curSize <= CONFIG["packageSize"]:
            break

def updateReslib(baseDir,obbPath,reslib):
    beginTime = time.time()
    if RESLIB_KEY == None or RESLIB_KEY == "":
        reslibKey = "ef3c7af56946360e12bc30724f40d84a"
    else:
        reslibKey = str(RESLIB_KEY)

    sqlFilePath = baseDir + "/update.sql"
    if os.path.exists(sqlFilePath):
        os.remove(sqlFilePath)
    if os.path.exists(obbPath+".DS_Store"):
        os.remove(obbPath+".DS_Store")

    sqlFile = open(sqlFilePath,"wb")
    if not sqlFile:
        print "Error:updateReslib fail,can not open " + sqlFilePath
        return

    for root, dirs, files in os.walk(obbPath):
        for name in files:
            # print "update reslib : " + os.path.join(root, name).replace(obbPath,"")
            sqlCommond = "update version_" + str(BUILD_VERSION) + " set location=0 where url = \"" + os.path.join(root, name).replace(obbPath,"") +"\" ;\n"
            sqlFile.write(sqlCommond)

    if sqlFile:
        sqlFile.close()
    
    updateSqlCmd = SQLITETOOLS_BIN + " -key " + reslibKey + " -db " + reslib + " -sql " + sqlFilePath + " -log "
    # print "updateSqlCmd="+updateSqlCmd
    subprocess.check_call(updateSqlCmd,shell=True)
    if os.path.exists(sqlFilePath):
        os.remove(sqlFilePath)
    print "updateReslib cost time="+str(time.time()-beginTime)

__DIR__, _ = os.path.split(os.path.abspath(__file__)) 
def generateResultPackage():
    baseDir = BASE_DIR
    # create result.apk
    resultApkPath = baseDir + "/result.apk"
    cmd = "cd " + baseDir + "/test && rm META-INF/* && zip -n jpg:jpeg:png:gif:wav:mp2:mp3:ogg:aac:mpg:mpeg:mid:midi:smf:jet:rtttl:imy:xmf:mp4:m4a:m4v:3gp:3gpp:3g2:3gpp2:amr:awb:wma:wmv -r " + resultApkPath + " ."
    subprocess.check_call(cmd, shell=True)
    print("cmd="+cmd)

    newApkPath = baseDir + "/kos_new.apk"
    # result.apk to kos_new.apk
    cmd = "jarsigner -digestalg SHA1 -sigalg MD5withRSA -tsa http://timestamp.digicert.com -keystore " + __DIR__ + "/" + CONFIG["keyStore"] + " -storepass " + CONFIG["storepass"] + " -signedjar " + newApkPath + " " + resultApkPath + " " + CONFIG["keyAlias"] + " && rm " + resultApkPath
    print("cmd="+cmd)
    subprocess.check_call(cmd, shell=True)

    # kos_new.apk to kos_final.apk(mini包)
    # finalApk = OUTPUT_DIR + "/kos_final.apk"
    finalApk = OUTPUT_DIR + "/" + str(VERSION_CODE) + "_kos_googleplay_mini.apk"
    if os.path.exists(finalApk):
        subprocess.check_call("rm " + finalApk,shell=True)
    cmd = ZIPALIGN_BIN + " -v 4 " + newApkPath + " " + finalApk + " > /dev/null && rm " + newApkPath
    print("cmd="+cmd)
    subprocess.check_call(cmd,shell=True)

    # 按照命名规范生成obb包
    subprocess.check_call("cd " + baseDir + "/obb && zip -n jpg:jpeg:png:gif:wav:mp2:mp3:ogg:aac:mpg:mpeg:mid:midi:smf:jet:rtttl:imy:xmf:mp4:m4a:m4v:3gp:3gpp:3g2:3gpp2:amr:awb:wma:wmv -r " + OUTPUT_DIR + "/main." + str(VERSION_CODE) + "." + CONFIG["packageName"] + ".obb .", shell=True)

@click.command()
@click.option('--apk', required=True, help=u'apk包绝对路径')
@click.option('--vcode',required= True, help=u'apk的AndroidManifest文件的versioncode')
@click.option('--bversion',required= True, help=u'walleui打包时的版本号')
@click.option('--packageName',required= True, help=u'包名')
@click.option('--keyStore',required= True, help=u'签名文件')
@click.option('--keyAlias',required= True, help=u'签名别名')
@click.option('--dbkey',required= False, help=u'reslib秘钥')
@click.option('--output',required= False, help=u'obb包输出目录(默认为apk包所在文件夹下的output)')
def execute(**options):
    u'''生成googleplay obb包(小包apk+obb资源扩展包模式)'''
    print(options["packagename"]+"42343423")
    CONFIG["packageName"] = options["packagename"]
    CONFIG["keyStore"] = options["keystore"]
    CONFIG["keyAlias"] = options["keyalias"]

    srcApk = options["apk"]
    if not os.path.isfile(srcApk):
        print "apk文件不存在:".decode("utf-8") + srcApk
        return

    global VERSION_CODE
    VERSION_CODE = options["vcode"]
    global BUILD_VERSION 
    BUILD_VERSION = options["bversion"]
    baseDir = os.path.dirname(srcApk)

    global BASE_DIR
    BASE_DIR = baseDir

    apkName = baseDir + "/src.apk"
    unpackPath = baseDir + "/test"
    obbPath = baseDir + "/obb/"

    dirname = os.path.dirname(os.path.realpath(__file__))
    src_path = os.path.join(dirname, "lib")
    dest_path = os.path.join(baseDir, "lib")
    if not os.path.exists(dest_path):
        shutil.copytree(src_path, dest_path)

    # src_keyStore = os.path.join(dirname, CONFIG["keyStore"])
    # dest_keyStore = os.path.join(baseDir, CONFIG["keyStore"])
    # if not os.path.exists(dest_keyStore):
    #     shutil.copy(src_keyStore, dest_keyStore)

    global ZIPALIGN_BIN
    ZIPALIGN_BIN = baseDir + "/lib/zipalign"
    global SQLITETOOLS_BIN
    SQLITETOOLS_BIN = baseDir + "/lib/sqlitetools"

    global RESLIB_KEY
    RESLIB_KEY = options["dbkey"]

    global OUTPUT_DIR 
    OUTPUT_DIR = options["output"]

    if OUTPUT_DIR == None or OUTPUT_DIR == "":
        OUTPUT_DIR = baseDir + "/output"
        if not os.path.isdir(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)

    tmp_name = os.path.basename(srcApk)
    tmp_name_array = os.path.splitext(tmp_name)
    OUTPUT_DIR = os.path.join(OUTPUT_DIR, tmp_name_array[0])
    print(OUTPUT_DIR)
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    if not os.path.isdir(OUTPUT_DIR):
        print "输出目录不存在:".decode("utf-8") + OUTPUT_DIR
        return

    # 重置环境
    def resetEnv():
        if os.path.exists(apkName):
            subprocess.check_call("rm -R " + apkName,shell=True)
        if os.path.exists(unpackPath):
            subprocess.check_call("rm -R " + unpackPath,shell=True)
        if os.path.exists(obbPath):
            subprocess.check_call("rm -R " + obbPath,shell=True)

    resetEnv()
    
    beginTime = time.time()
    # 拷贝apk包
    print "do copy apk ..."
    shutil.copy(srcApk,apkName)
    # 解压apk包
    print "do unpack apk ..."
    unzip(apkName,unpackPath)
    #移动资源（检测资源包大小）
    print "do move res ..."
    moveRes(unpackPath,obbPath)
    # 更新relib
    updateReslib(baseDir,obbPath,unpackPath + "/assets/reslib")
    generateResultPackage()
    # # 重置环境
    resetEnv()
    print "##total cost time=" + str(time.time() - beginTime)

if __name__ == '__main__':
    execute()