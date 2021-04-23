#!/usr/bin/env python
# coding=utf-8
# Filename: kosuitools.py
# Author:   <zhoujiatu@playcrab.com>
# Description: File description

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# 注意事项：
# 1 参数名字如果需要中文，一定是英语(中文)格式，到时候参数传递会自动把(中文)去掉，一定要带小括号, link类型特殊,因为不传递
# 2

global select_list
select_list = {
    "越南": {
        "info":{
            "code": "kosvn"
        },
        "autotag": {
            "desc": "越南自动打tag",
            "template":{
                "link":{
                    "主干":"http://10.2.181.147:9011?master",
                    "分支":"http://10.2.181.147:9011?preonline",
                    "online":"http://10.2.181.147:9011?online",
                }
            }
        },
        "initpacker": {
            "desc": "初始化内网打包机",
            "template":{
                "edit":{
                    "参数1":"默认值",
                }
            }
        },
    },
    "港澳台东南亚":{
        "info":{
            "code": "kosdt"
        },
        "autotag": {
            "desc": "港澳台东南亚自动打tag",
            "template":{
                "link":{
                    "lua主干":"http://10.2.181.147:9011?tag:kosdt_master",
                    "lua分支":"http://10.2.181.147:9011?tag:kosdt_preonline",
                    "lua线上":"http://10.2.181.147:9011?tag:kosdt_newonline",
                }
            }
        },
        "initpacker": {
            "desc": "初始化内网打包机",
            "template":{
                "edit":{
                    "ip(内网打包机ip)":"10.2.181.147",
                    "url(内网打包机钉钉tag提醒网址)":"https://oapi.dingtalk.com/robot/send?access_token=6bea31231b6b645838e8c3db433683fef297deb42ee543497534f407781d6395",
                    "luapath(内网打包机lua目录绝对路径)":"/Users/playcrab/Documents/svn/koslua"
                }
            },
            "cmd":{
                "script":"initpacker/initpacker.py",
                "request_params":[
                    "ip",
                    "url",
                    "luapath",
                ]
            },
        },
    }
}



# "autotag": {
#     "desc": "港澳台东南亚自动打tag",
#     "template":{
#         "link":{
#             "主干":"http://10.2.181.147:9011?master",
#             "分支":"http://10.2.181.147:9011?preonline",
#             "online":"http://10.2.181.147:9011?online",
#         }
#     }
# },
# "splitobb": {
#     "desc": "obb拆包",
#     "cmd":{
#         "script":"splitobb/outputobb.py",
#         "request_params":[
#             "packageName",
#             "keyStore",
#             "keyAlias",
#             "vcode",
#             "bversion",
#             "apk",
#             "output",
#         ]
#     },
#     "template":{
#         "edit":{
#             "packageName":"",
#             "keyStore":"",
#             "keyAlias":"",
#             "vcode(apk包内版本号)":"",
#             "bversion(Wallet的版本号)":"",
#         },
#         "edit_path_dir":{
#             "output(输出路径)":"",
#         },
#         "edit_path_file":{
#             "apk(apk包路径)":"",
#         }
#     },
#     "template_1":{
#         "desc":"越南",
#         "edit":{
#             "packageName":"com.vng.onepunchman",
#             "keyStore":"vn/google.keystore",
#             "keyAlias":"tronghv",
#         },
#     },
#     "template_2":{
#         "desc":"东南亚",
#         "edit":{
#             "packageName":"com.onepunchman.ggplay.dt",
#             "keyStore":"sea/playcrab_kos.keystore",
#             "keyAlias":"playcrab_kos",
#         },
#     }
# },
# "pushobb": {
#     "desc": "obb推送到手机上(数据线连接并打开开发者模式)",
#     "template":{
#         "edit":{
#             "参数1":"默认值",
#         }
#     }
# },
# "twowrapp": {
#     "desc": "越南android二次封包",
#     "template":{
#         "edit":{
#             "参数1":"默认值",
#         }
#     },
#     "cmd":{
#         "script":"twowrapp/twowrapp.py",
#         "request_params":[
#             "packageName",
#             "keyStore",
#             "keyAlias",
#             "vcode",
#             "bversion",
#             "apk",
#             "output",
#         ]
#     },
# },


