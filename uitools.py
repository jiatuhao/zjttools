#!/usr/bin/env python
# coding=utf-8
# Filename: kosuitools.py
# Author:   <zhoujiatu@playcrab.com>
# Description: File description

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import platform
import os, os.path
import shutil
import threading
import time
import webbrowser
import subprocess
import click

from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *
from Queue import *
from tkinter import ttk
from uiconfig import select_list
#控件基础库 start
def create_btn(inst, win, row_num, col_num, name, click_func):
    action = ttk.Button(win, text=name, command=click_func)     # 创建一个按钮, text：显示按钮上面显示的文字, command：当这个按钮被点击之后会调用command函数
    action.grid(column= col_num, row=row_num)
    inst._nodes.append(action)

def create_text_link(inst, win, row_num, text_name, value):
    label = Label(win, text=text_name)
    label.grid(row=row_num, column=0)
    inst._nodes.append(label)

    def callback(event):
        webbrowser.open_new(value)
    link = Label(win, text=value, fg="blue", cursor="hand2")
    link.pack()
    link.bind("<Button-1>", callback)
    link.grid(row=row_num, column=1)
    inst._nodes.append(link)
    return label, link, None

def create_text_edit(inst, win, row_num, text_name, value):
    label = Label(win, text=text_name)
    label.grid(row=row_num, column=0)
    inst._nodes.append(label)
    def eventhandler(event):
        entry.focus()

    edit_str = StringVar()
    entry=Entry(win,width=60,textvariable=edit_str)
    entry.bind_all('<Control-f>', eventhandler ) # 绑定快捷键Ctrl-f
    entry.grid(row=row_num, column=1)
    edit_str.set(value)
    inst._nodes.append(entry)
    return label, entry,edit_str

def create_text_path_dir(inst, win, row_num, text_name, value):
    label = Label(win, text=text_name)
    label.grid(row=row_num, column=0)
    inst._nodes.append(label)


    def eventhandler(event):
        entry.focus()
    edit_str = StringVar()
    entry=Entry(win,width=60,textvariable=edit_str)
    entry.bind_all('<Control-f>', eventhandler ) # 绑定快捷键Ctrl-f
    entry.grid(row=row_num, column=1)
    edit_str.set(value)
    inst._nodes.append(entry)

    def pathCallback():
        filepath = askdirectory()
        if filepath:
            entry.delete(0, END)
            entry.insert(0, filepath)

    btn = Button(win, text="选择路径", width = 6, command = pathCallback)
    btn.grid(row=row_num, column=2)
    inst._nodes.append(btn)
    
    return label, entry,edit_str

def create_text_path_file(inst, win, row_num, text_name, value):
    label = Label(win, text=text_name)
    label.grid(row=row_num, column=0)
    inst._nodes.append(label)


    def eventhandler(event):
        entry.focus()
    edit_str = StringVar()
    entry=Entry(win,width=60,textvariable=edit_str)
    entry.bind_all('<Control-f>', eventhandler ) # 绑定快捷键Ctrl-f
    entry.grid(row=row_num, column=1)
    edit_str.set(value)
    inst._nodes.append(entry)

    def pathCallback():
        filepath = askopenfilename()
        if filepath:
            entry.delete(0, END)
            entry.insert(0, filepath)

    btn = Button(win, text="选择路径", width = 6, command = pathCallback)
    btn.grid(row=row_num, column=2)
    inst._nodes.append(btn)
    
    return label, entry,edit_str
#控件基础库 end
#控件信息配置 start
node_list = {
    "link":{"create_func":create_text_link, "set_func":"null"},
    "edit":{"create_func":create_text_edit, "set_func":"set"},
    "edit_path_dir":{"create_func":create_text_path_dir, "set_func":"set"},
    "edit_path_file":{"create_func":create_text_path_file, "set_func":"set"},
}
#控件信息配置 end
#核心代码 start
__DIR__, _ = os.path.split(os.path.abspath(__file__)) 
__ISATTY__ = sys.stdout.isatty()
class Logging:
    # TODO maybe the right way to do this is to use something like colorama?
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    MAGENTA = '\033[35m'
    RESET = '\033[0m'

    @staticmethod
    def _print(s, color=None):
        if color and __ISATTY__ and sys.platform != 'win32':
            # print color + s + Logging.RESET, 
            print(s)
        else:
            print(s)

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


class StdoutRedirector(object):
    """Redirect output.
    """
    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, str):
        self.text_area.insert(END, str)
        self.text_area.see(END)

def run_shell(shell):
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    while True:
        line = cmd.stdout.readline()
        Logging.info(line)
        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            break

    return cmd.returncode

class TkCocosDialog(Frame):
    def clear_nodes(self):
        if self._nodes:
            for b in self._nodes:
                if b:
                    b.destroy()
        self._nodes = []
        


    def clear_other_nodes(self):
        if self._other_nodes:
            for b in self._other_nodes:
                if b:
                    b.destroy()
        self._other_nodes = []

    def create_nodes(self, win, mainInfo):
        ui_template = mainInfo["template"]
        cur_row = 2
        template_btn_row_cur = 1
        template_btn_col_fixed  = 3

        collect_templates = {}
        collect_nodes = {}
        click_funcs = {}

        def click_template_func(key):
            info = collect_templates[key]
            for k in collect_nodes:
                if info.has_key(k):
                    set_func = node_list[k]["set_func"]
                    for k1 in collect_nodes[k]:
                        if info[k].has_key(k1):
                            collect_nodes[k][k1]["node_str"].set(info[k][k1])

        for k1 in mainInfo:
            if k1.find("template_") != -1:
                content = mainInfo[k1]
                collect_templates[k1] = content
                
                create_btn(self, win, template_btn_row_cur,template_btn_col_fixed, content["desc"], 
                    lambda key=k1: click_template_func(key))
                template_btn_row_cur = template_btn_row_cur + 1

        for k in ui_template:
            if node_list.has_key(k):
                collect_nodes[k] = {}
                info = ui_template[k]
                create_func = node_list[k]["create_func"]
                set_func = node_list[k]["set_func"]
                for k1 in info:
                    label, node, node_str = create_func(self, win, cur_row, k1, info[k1])
                    if set_func != "null":
                        collect_nodes[k][k1] = {"label":label, "node_str":node_str}
                    cur_row = cur_row + 1

        def click_func():
            params = {}
            for k in collect_nodes:
                for k1 in collect_nodes[k]:
                    info = collect_nodes[k][k1]
                    text = info["label"].cget("text")
                    str_list = text.split("(")
                    params[str_list[0]] = info["node_str"].get()
            
            if select_list[self._select_project][self._select_key].has_key("cmd"):
                flag = False
                cmd_info = select_list[self._select_project][self._select_key]["cmd"]
                if cmd_info.has_key("request_params"):
                    for k in cmd_info["request_params"]:
                        if params.has_key(k) == None or params[k] == "":
                            Logging.error("参数"+k+"不能为空！！！！")
                            flag = True
                if flag == False:
                    path_tmps = cmd_info["script"].split("/")
                    path = os.path.join(__DIR__, "cmd")
                    for k in path_tmps:
                        path = os.path.join(path, k)
                    params_str = ""
                    for k in params:
                        params_str=params_str+" --"+k+" "+params[k]
                    params_str=params_str+" --"+"code"+" "+select_list[self._select_project]["info"]["code"]
                    cmd_str = "python "+path+params_str
                    Logging.info("开始运行脚本:"+cmd_str)
                    Logging.info("运行中......")
                    run_shell(cmd_str)
                    Logging.info("运行结束!")

                    # ret = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    # for line in ret.stdout.readlines(): 
                    #     line = line.strip()
                    #     Logging.info(line)
        return click_func

    def select_project(self):
        self.clear_nodes()
        self.clear_other_nodes()

        def go(*args):  #处理事件，*args表示可变参数
            select_str = numberChosen1.get()
            for k in select_list:
                if k == select_str:
                    self._select_project = k
                    self.show_project()


        win = self.parent


        label2 = ttk.Label(win, text="选择项目:")
        label2.grid(column=1, row=3)    # 添加一个标签，并将其列设置为1，行设置为0
        self._other_nodes.append(label2)
        number = StringVar()
        numberChosen1 = ttk.Combobox(win, width=60, textvariable=StringVar())
        numberChosen1.bind("<<ComboboxSelected>>",go)
        self._other_nodes.append(numberChosen1)

        info = []
        for k in select_list:
            info.append(k)
        numberChosen1['values'] = info     # 设置下拉列表的值
        numberChosen1.grid(column=3, row=3)      # 设置其在界面中出现的位置  column代表列   row 代表行
        # self.show_project()

    def show_project(self):
        self.clear_nodes()
        self.clear_other_nodes()
        new_select_list = select_list[self._select_project]

        parent = self.parent
        win = self.parent
        self._select_key = ""
        self._click_func = None
        def go(*args):  #处理事件，*args表示可变参数
            select_str = numberChosen.get()
            for k in new_select_list:
                if k != "info" and new_select_list[k]["desc"] == select_str:
                    Logging.info("选择了："+select_str)
                    self._select_key = k
                    self.clear_nodes()
                    self._click_func = self.create_nodes(win, new_select_list[k])

        label5 = ttk.Label(win, text="选择命令:")
        label5.grid(column=0, row=0)    # 添加一个标签，并将其列设置为1，行设置为0
        self._other_nodes.append(label5)
        number = StringVar()
        numberChosen = ttk.Combobox(win, width=60, textvariable=StringVar())
        numberChosen.bind("<<ComboboxSelected>>",go)
        self._other_nodes.append(numberChosen)
        # for info in select_list:

        info = []
        for k in new_select_list:
            if k != "info":
                info.append(new_select_list[k]["desc"])
        numberChosen['values'] = info     # 设置下拉列表的值
        numberChosen.grid(column=1, row=0)      # 设置其在界面中出现的位置  column代表列   row 代表行

        # button被点击之后会被执行
        def clickMe():   # 当acction被点击时,该函数则生效
            if self._click_func:
                self._click_func()
        # 按钮
        action = ttk.Button(win, text="运行", command=clickMe)     # 创建一个按钮, text：显示按钮上面显示的文字, command：当这个按钮被点击之后会调用command函数
        action.grid(column= 10, row=0)    # 设置其在界面中出现的位置  column代表列   row 代表行
        self._other_nodes.append(action)
        self.text=Text(parent,background = '#d9efff', width=200, height=50)
        self.text.bind("<KeyPress>", lambda e : "break")
        self.text.grid(row=10, column=0, columnspan=30, rowspan=2, padx=5, sticky=E+W+S+N)
        self._other_nodes.append(self.text)

        def clear():   # 当acction被点击时,该函数则生效
            self.text.delete(1.0,END)
        # 按钮
        action = ttk.Button(win, text="清空打印框", command=clear)     # 创建一个按钮, text：显示按钮上面显示的文字, command：当这个按钮被点击之后会调用command函数
        action.grid(column= 11, row=0)    # 设置其在界面中出现的位置  column代表列   row 代表行
        self._other_nodes.append(action)

        def back():   # 当acction被点击时,该函数则生效
            self.select_project()

        action1 = ttk.Button(win, text="回到上一层", command=back)     # 创建一个按钮, text：显示按钮上面显示的文字, command：当这个按钮被点击之后会调用command函数
        action1.grid(column=  15, row=0)    # 设置其在界面中出现的位置  column代表列   row 代表行
        self._other_nodes.append(action1)

        self._project_label = ttk.Label(win, text="当前项目是:"+self._select_project)
        self._project_label.grid(column=17, row=0)    # 添加一个标签，并将其列设置为1，行设置为0
        self._other_nodes.append(self._project_label)


        sys.stdout = StdoutRedirector(self.text)
    def __init__(self, parent):
        Frame.__init__(self,parent)
        self._nodes = []
        self._other_nodes = []
        self.parent = parent
        self.parent.title("一拳可视化工具")    # 添加标题
        self.select_project()
#核心代码 end

@click.command()
def execute(**arguments):
    old_stdout = sys.stdout
    root = Tk()
    app = TkCocosDialog(root)
    root.mainloop()
    sys.stdout = old_stdout
    
if __name__ =='__main__':
    execute()
