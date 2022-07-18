from operator import le
from pickle import FRAME
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import sys
import os
import multiprocessing
import subprocess
import pathlib

from tkinter import ttk

global aria2_cmd
global catcher_cmd


class Task:
    url = ""
    download_path = ""
    password = ""

    frame = None
    url_inputfield = None
    download_path_btn = None
    password_inputfield = None

    def __init__(self) -> None:
        pass
    def input(this,line):
        get_space = False
        get_quote1 = False
        get_quote2 = False
        eq_count = 0
        read_pwd = False
        for character in line:
            if not get_space:
                if character == ' ':
                    get_space = True
                    continue
                this.url += character
            else:
                if not get_quote1 :
                    if character == '"':
                        get_quote1 = True
                        continue
                else:
                    if not get_quote2:
                        if character == '"':
                            get_quote2 = True
                            continue
                        this.download_path += character
                    else:
                        if not read_pwd:
                            if character == '=':
                                eq_count += 1
                                if eq_count == 2:
                                    read_pwd = True
                        elif character != '\n':
                            this.password += character
    def update(this):
        if this.url_inputfield != None:
            this.url = this.url_inputfield.get()
        if this.download_path_btn != None:
            this.download_path = this.download_path_btn['text']
        if this.password_inputfield != None:
            this.password = this.password_inputfield.get()
    def output(this):
        this.update()
        if len(this.url) == 0 or len(this.download_path) == 0:
            return ""
        result = (this.url + " dir==\"" + this.download_path + "\"")
        if len(this.password) > 0:
            result +=  (" pwd==" + this.password)
        result += '\n'
        return result

def run_catcher():
    global catcher_cmd
    global catcher_process
    catcher_process = subprocess.Popen(catcher_cmd)

def run_aria2():
    global aria2_cmd
    global aria2_process
    aria2_process = subprocess.Popen(aria2_cmd)

def get_cmd():
    global aria2_cmd
    global catcher_cmd
    file = open('cmd.txt')
    aria2_cmd = file.readline()
    catcher_cmd = file.readline()
    if len(aria2_cmd) == 0 or len(catcher_cmd) == 0:
        os._exit(0)

def change_port(inputfield):
    global aria2_process
    if not inputfield.get().isnumeric():
        tk.messagebox.showerror('Input Error', 'Error: Port must be a number')
        return
    if aria2_process == None:
        return
    aria2_process.terminate()
    conf_change("aria2.conf","rpc-listen-port",inputfield.get())
    conf_change("aria2.conn.config","Aria2_port",inputfield.get())
    run_aria2()


def conf_change(filename,parameter,newval):
    fin = open(filename, "rt")
    lines = fin.readlines()
    fin.close()
    result = []
    for line in lines:
        new_line = ""
        for character in line:
            if character == '=':
                if new_line == parameter:
                    new_line += ('=' + newval + '\n')
                    result.append(new_line)
                else:
                    result.append(line)
            else:
                new_line += character 
    fout = open(filename, "wt")
    fout.writelines(result)
    fout.close()

def conf_get(filename,parameter):
    fin = open(filename, "rt")
    lines = fin.readlines()
    fin.close()
    result = ""
    for line in lines:
        new_line = ""
        get_eq = False
        for character in line:
            if character == '=':
                if new_line == parameter:
                    get_eq = True
            else:
                new_line += character
                if get_eq and character != '\n':
                    result += character
        if get_eq:
            return result
    return ""

def get_all_task(filename):
    fin = open(filename, "rt", encoding="utf-8")
    lines = fin.readlines()
    fin.close()
    result = []
    for line in lines:
        if (line[0] == '#') or (line[0] == '/' and line[1] == '/') or (len(line) < 2):
            continue
        task = Task()
        task.input(line)
        print(task.output())
        result.append(task)
    return result


def get_download_path(btn):
    path = filedialog.askdirectory()
    if len(path) != 0:
        btn['text'] = path
        save_tasks()


def add_task_to_UI(frame,task):
    task.frame = tk.Frame(frame,bg='#1e2124',highlightbackground="#1e2124",highlightthickness=5)
    task.url_inputfield = tk.Entry(task.frame, width=50)
    task.url_inputfield.insert(0,task.url)
    task.url_inputfield.grid(row=0, column=0, sticky="nsew",padx=5,pady=5)
    task.download_path_btn = tk.Button(task.frame,text=task.download_path, width=50,anchor="w",command=lambda:get_download_path(task.download_path_btn))
    task.download_path_btn.grid(row=0, column=1, sticky="nsew",padx=5,pady=5)
    task.password_inputfield = tk.Entry(task.frame, width=30)
    task.password_inputfield.insert(0,task.password)
    task.password_inputfield.grid(row=0, column=2, sticky="nsew",padx=5,pady=5)
    task.frame.grid_columnconfigure(0, weight=1, uniform="group1")
    task.frame.grid_columnconfigure(1, weight=1, uniform="group1")
    task.frame.grid_rowconfigure(0, weight=1)
    task.frame.pack(fill=tk.X,padx=5)

def add_task(frame):
    global tasks
    task_count = len(tasks)
    last = task_count - 1
    tasks[last].update()
    if len(tasks[last].url) == 0:
        return
    task = Task()
    task.download_path = tasks[last].download_path
    tasks.append(task)
    add_task_to_UI(frame,task)
    save_tasks()

def save_tasks():
    global tasks
    result = []
    for task in tasks:
        result.append(task.output())
    fout = open("tasklist", "wt", encoding="utf-8")
    fout.writelines(result)
    fout.close()

def remove_last_task(frame):
    global tasks
    task_count = len(tasks)
    last = task_count - 1
    tasks[last].url_inputfield.pack_forget()
    tasks[last].url_inputfield.destroy()
    tasks[last].download_path_btn.pack_forget()
    tasks[last].download_path_btn.destroy()
    tasks[last].password_inputfield.pack_forget()
    tasks[last].password_inputfield.destroy()
    tasks[last].frame.pack_forget()
    tasks[last].frame.destroy()
    tasks.pop()
    save_tasks()
    if len(tasks) == 0:
        init_tasks()
        add_task_to_UI(frame,tasks[0])
    
def remove_all_task(frame):
    global tasks
    task_count = len(tasks)
    while task_count:
        remove_last_task(frame)
        task_count -= 1

def start_download():
    save_tasks()
    run_catcher()

def put_UI_comp():
    global app
    global tasks
    port_frame = tk.Frame(app,bg='#36393e',highlightbackground="#36393e",highlightthickness=5)
    tk.Label(port_frame,text='Aria2 Port: ',anchor="w",bg='#36393e',fg='#FFFAFA').pack(side=tk.LEFT,padx=5) 
    port = conf_get("aria2.conf","rpc-listen-port")
    if port != conf_get("aria2.conn.config","Aria2_port"):
        conf_change("aria2.conn.config","Aria2_port",port)
    port_inputfield = tk.Entry(port_frame)
    port_inputfield.insert(0,port)
    port_inputfield.pack(side=tk.LEFT,padx=5)
    port_change_btn = tk.Button(port_frame, text='更換 port',bg='#1e2124',fg='#FFFAFA',command=lambda : change_port(port_inputfield))
    port_change_btn.pack(side=tk.LEFT,padx=5)
    port_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)
    btns_frame = tk.Frame(app,bg='#36393e',highlightbackground="#36393e",highlightthickness=5)
    add_task_btn = tk.Button(btns_frame,text = "新增任務",command= lambda : add_task(tasks_frame),bg='#71C562')
    add_task_btn.pack(side=tk.LEFT,fill=tk.X,expand=1)
    save_task_btn = tk.Button(btns_frame,text = "保存所有任務",command= lambda : save_tasks(),bg='#315399')
    save_task_btn.pack(side=tk.LEFT,fill=tk.X,expand=1,padx=5)
    remove_all_task_btn = tk.Button(btns_frame,text = "刪除所有任務",command= lambda : remove_all_task(tasks_frame),bg='#A7171A')
    remove_all_task_btn.pack(side=tk.RIGHT,fill=tk.X,expand=1,padx=5)
    remove_task_btn = tk.Button(btns_frame,text = "刪除最後任務",command= lambda : remove_last_task(tasks_frame),bg='#FFC0CB')
    remove_task_btn.pack(side=tk.RIGHT,fill=tk.X,expand=1,padx=5)
    btns_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)
    tasks_frame = tk.Frame(app,bg='#36393e')
    tasks_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)
    tasks_head_frame = tk.Frame(tasks_frame,bg='#1e2124',highlightbackground="#1e2124",highlightthickness=5)
    tk.Label(tasks_head_frame,text='Sharepoint 網址(僅支援資料夾)',anchor="w",bg='#1e2124',fg='#FFFAFA').grid(row=0, column=0, sticky="nsew")
    tk.Label(tasks_head_frame,text='下載路徑(點擊以選取路徑)',anchor="w",bg='#1e2124',fg='#FFFAFA').grid(row=0, column=1, sticky="nsew")
    tk.Label(tasks_head_frame,text='密碼(無則免填)',anchor="w",bg='#1e2124',fg='#FFFAFA').grid(row=0, column=2, sticky="nsew")
    tasks_head_frame.grid_columnconfigure(0, weight=1, uniform="group1")
    tasks_head_frame.grid_columnconfigure(1, weight=1, uniform="group1")
    tasks_head_frame.grid_rowconfigure(0, weight=1)
    tasks_head_frame.pack(fill=tk.X,padx=5)
    for task in tasks:
        add_task_to_UI(tasks_frame,task)
    start_download_btn = tk.Button(app,height=2,text = "開始下載",command= lambda : start_download(),bg='#90EE90')
    start_download_btn.pack(side=tk.TOP,fill=tk.BOTH,padx=5,pady=5)
    
    
def init_tasks():
    global tasks
    if tasks != None:
        tasks.clear()
    tasks = get_all_task("tasklist")
    if len(tasks) == 0:
        empty_task = Task()
        empty_task.download_path = pathlib.Path().resolve()
        tasks.append(empty_task)


def main():
    global aria2_process
    global catcher_process
    global app
    global tasks
    aria2_process = None
    catcher_process = None
    tasks = None
    get_cmd()
    init_tasks()
    run_aria2()
    app = tk.Tk()
    app.title("Sharepoint Downloader GUI")
    app.resizable(width=True, height=False)
    app.update_idletasks()
    app.configure(bg='#36393e',highlightthickness=0)
    app.iconbitmap('./sharepoint_logo.ico')
    app.protocol('WM_DELETE_WINDOW',app_closed)
    #put_my_title_bar()
    put_UI_comp()
    app.mainloop()

def toggle(event):
    global app
    if event.type == tk.EventType.Map:
        app.deiconify()
    else:
        app.withdraw()

def app_closed():
    save_tasks()
    if aria2_process != None:
        aria2_process.terminate()
    if catcher_process != None:
        catcher_process.terminate()
    app.destroy()


def fullscreen():
    global fullscreenTurn
    global screenSize
    global app
    if (fullscreenTurn): 
        app.overrideredirect(False)
        screenSize=f'{app.winfo_width()}x{app.winfo_height()}' #saving last screen size before fullscreen
        app.attributes('-fullscreen',True)
        app.overrideredirect(True)
        fullscreenTurn=False
    else:
        app.overrideredirect(False)
        app.attributes('-fullscreen',False)
        app.geometry(f"{screenSize}")
        app.overrideredirect(True)
        fullscreenTurn=True

# Window Movement
def moveWindow(event):
    global app
    x = app.winfo_pointerx() - app.offsetx
    y = app.winfo_pointery() - app.offsety
    app.geometry(f'+{x}+{y}')

# Coordinates where the titlebar is clicked
def click(event):
    global app
    app.offsetx=event.x
    app.offsety=event.y

if __name__ == '__main__':
    main()







'''
def put_my_title_bar():
    global app
    app.overrideredirect(True)
    # create the "invisible" toplevel
    
    top = tk.Toplevel()
    top.geometry('0x0+10000+10000') # make it not visible
    top.title('Sharepoint Downloader GUI') # title for the process in task manager
    top.protocol('WM_DELETE_WINDOW', app_closed) # close root window if toplevel is closed
    top.bind("<Map>", toggle)
    top.bind("<Unmap>", toggle)
    
    fgColour='#c0c8c6'
    #Making the titlebar
    titlebg='#505050'
    titlebar=tk.Frame(app,background=titlebg,bd=1,relief=tk.FLAT)
    titlebar.pack(side=tk.TOP, fill=tk.X)
    titleLabel=tk.Label(titlebar,text="Sharepoint Downloader GUI",fg=fgColour,bg=titlebg)
    titleLabel.pack(side=tk.LEFT)
    tk.Button(titlebar,command=app_closed,bg=titlebg,text="X",fg=fgColour,width=3,relief=tk.FLAT,font='Helvetica 10 bold').pack(side=tk.RIGHT)
    #tk.Button(titlebar,command=fullscreen,bg=titlebg,text="O",fg=fgColour,width=3,relief=tk.FLAT,font='Helvetica 10 bold').pack(side=tk.RIGHT)
    #tk.Button(titlebar,command=top.iconify,bg=titlebg,text="---",fg=fgColour,width=3,relief=tk.FLAT,font='Helvetica 10 bold').pack(side=tk.RIGHT)
    titlebar.bind('<B1-Motion>',moveWindow)
    titlebar.bind('<Button-1>',click)
    #Binding to label otherwise the window didn't move when cursor was over the label
    titleLabel.bind('<B1-Motion>',moveWindow)
    titleLabel.bind('<Button-1>',click)
'''