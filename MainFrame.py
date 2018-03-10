# coding utf-8
import tkinter
import tkinter.filedialog
import datetime
import time
import socket
import threading
import DataCenter
import os
import pdfkit
import webbrowser

import urllib.parse
import urllib.request
import http.client
import json
import http.cookiejar
import shutil


class MainFrame(tkinter.Frame):
    def __init__(self):
        pass;
    def start_window(self):
        self.root = self.createWindow()
        tkinter.Frame.__init__(self, self.root)
        self.grid(row=0, column=0, sticky="nsew")
        self.createFrame()
        self.mainloop()

    def createWindow(self):
        root = tkinter.Tk()
    #     filename = tkinter.filedialog.askopenfilename(title="Open File",initialdir='E:/')
    #     print(filename)
        root.title('welcom,' + DataCenter.HANDLE)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.geometry('320x480')  # 设置了主窗口的初始大小960x540 800x450 640x360    
        return root
    
    
    def download(self, problem_id):
        try:
            
            problem_path = problem_id + ".pdf"
            problem_path = problem_path.strip();
            if(os.path.exists("problemset/" + problem_path)):
                return 1;
            if(problem_id[-1].isdigit()):
                problem_url = 'http://codeforces.com/problemset/problem/' + problem_id[:-2] + '/' + problem_id[-2:];
                if DataCenter.DEBUG:
                    print(problem_url);
            else:
                problem_url = 'http://codeforces.com/problemset/problem/' + problem_id[:-1] + '/' + problem_id[-1];
            problem_url = problem_url.strip();
            
            DataCenter.pdfdownload(problem_url , problem_path);
            
            shutil.move(problem_path, "problemset/")
            
        except Exception as e:
            return 0;
        return 0;
    
    def download_multi(self, problem_id):
        try:
            problem_path = problem_id + ".pdf"
            problem_path = problem_path.strip();
            if(os.path.exists("problemset/" + problem_path)):
                return 1;
            if(problem_id[-1].isdigit()):
                problem_url = 'http://codeforces.com/problemset/problem/' + problem_id[:-2] + '/' + problem_id[-2:];
                if DataCenter.DEBUG:
                    print(problem_url);
            else:
                problem_url = 'http://codeforces.com/problemset/problem/' + problem_id[:-1] + '/' + problem_id[-1];
            problem_url = problem_url.strip();
            
            DataCenter.PdfDownloader(problem_url, problem_path).start();
            return 0;
        except Exception as e:
            return 0;
       
    
    def save(self):
        problem_index = self.text_dialog.curselection();
        problem_id = self.text_dialog.get(problem_index);
        f = open("code/" + problem_id + ".txt", "w");
        f.write(self.text_input.get(0.0, tkinter.END));
    
    def show(self):
#         pdfconfig = pdfkit.configuration(wkhtmltopdf=b"d:/wkhtmltopdf/bin/wkhtmltopdf.exe")
        problem_index = self.text_dialog.curselection();
        problem_id = self.text_dialog.get(problem_index);
        
        self.text_input.delete(0.0, tkinter.END);
        if(os.path.exists("code/" + problem_id + ".txt")):
            f = open("code/" + problem_id + ".txt", "r");
            lines = f.read()
            if DataCenter.DEBUG:
                print(lines);
            self.text_input.insert(tkinter.END, lines);
            
        problem_path = problem_id + ".pdf"
        problem_path = problem_path.strip();
        self.download(problem_id);
        webbrowser.open(os.path.split(os.path.realpath(__file__))[0] + "/problemset/" + problem_path)
        
    def remove(self):
        problem_index = self.text_dialog.curselection();
        problem_id = self.text_dialog.get(problem_index);
        self.text_dialog.delete(self.text_dialog.curselection());
        DataCenter.PROBLEMLIST.remove(problem_id);
        DataCenter.save_problemlist();
        self.text_input.delete(0.0, tkinter.END);
        
    def ban(self):
        problem_index = self.text_dialog.curselection();
        problem_id = self.text_dialog.get(problem_index);
        DataCenter.BANLIST.append(problem_id);
        DataCenter.save_banlist();
        self.remove();
    
    def submit(self):
        problem_index = self.text_dialog.curselection();
        problem_id = self.text_dialog.get(problem_index);
        DataCenter.submit(problem_id);
    
    def downloadall(self):
        for problem_id in DataCenter.PROBLEMLIST:
            self.download_multi(problem_id)
    
#     def downloadall(self):
#         flag0 = 1;
#         while(flag0):
#             flag0 = 0;
#             for problem_id in DataCenter.PROBLEMLIST:
#                 if(self.download_multi(problem_id) == 0):
#                     flag0 = 1;
    
    def clear(self):
        self.text_dialog.delete(0, self.text_dialog.size());
        DataCenter.PROBLEMLIST.clear();
        DataCenter.save_problemlist();
        
    def drag(self):
        lstr = r'''<tr >'''
        rstr = r'''</a>'''
#         pattern = re.compile(r'''()([.])*()''')
        dragnum = int(self.text_dragnum.get(0.0, tkinter.END));
        if DataCenter.DEBUG:
            print(dragnum);
        
        nowcnt = 0;
        pagenum = 0;
        while (nowcnt < dragnum):
            pagenum += 1;
            if(pagenum > DataCenter.CF_MAX_PROBLEMPAGE):
                break;
            result = DataCenter.OPENER.open("http://codeforces.com/problemset/page/" + str(pagenum) + "?order=BY_SOLVED_DESC");
            DataCenter.COOKIE.save(ignore_discard=True, ignore_expires=True)
            html_str = result.read().decode("utf-8");
            if DataCenter.DEBUG:
                DataCenter.output_to_file("test/problemset" + str(pagenum) + ".txt", html_str);
            DataCenter.CSRF_TOKEN = DataCenter.txt_wrap_by(r"<input type='hidden' name='csrf_token' value='", r"'/>", html_str);
            if DataCenter.DEBUG:
                print(DataCenter.CSRF_TOKEN);   
                
#             match = pattern.match(html_str)
#                 
#             if match:
#                 # 使用Match获得分组信息
#                 print(match.groups());
#                 nowcnt += match.groups().size();
            
            res = DataCenter.all_txt_wrap_by(lstr, rstr, html_str);
            for au in res:
                au = au.split()[-1];
                if(au in DataCenter.BANLIST):
                    continue;
                if(au in DataCenter.PROBLEMLIST):
                    continue;
                else:
                    DataCenter.PROBLEMLIST.append(au);
                    self.text_dialog.insert(self.text_dialog.size(), au);
                    nowcnt += 1;
                if(nowcnt >= dragnum):
                    break;
        DataCenter.save_problemlist();
            
    
    def createFrame(self):
#         label_frame_top = tkinter.LabelFrame(self)
        # label_frame_top.pack()

        label_frame_center = tkinter.LabelFrame(self)
        label_frame_center.pack(fill="both", expand=1)

        text_frame = tkinter.LabelFrame(label_frame_center)
        text_frame.pack(fill="both", expand=1)
        
        
        
        button_frame2 = tkinter.LabelFrame(text_frame)
        button_frame2.pack(fill="both", expand=0)
        
        button_frame1 = tkinter.LabelFrame(text_frame)
        button_frame1.pack(fill="both", expand=0)
        
        file_frame = tkinter.LabelFrame(label_frame_center)
        file_frame.pack(fill="y", expand=0)

#         self.text_frame_l = tkinter.Label(text_frame, text="文件路径：", width=10)
#         self.text_frame_l.pack(fill="none", expand=0, side=tkinter.LEFT)




        self.button_show = tkinter.Button(button_frame1, text="Show" , command=self.show)
        self.button_show.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.button_save = tkinter.Button(button_frame1 , text="Save", command=self.save)
        self.button_save.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.button_submit = tkinter.Button(button_frame1 , text="Submit", command=self.submit)
        self.button_submit.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        self.button_submit.configure(state="disabled")
        
        self.button_remove = tkinter.Button(button_frame1 , text="Remove" , command=self.remove)
        self.button_remove.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.button_ban = tkinter.Button(button_frame1 , text="Ban" , command=self.ban)
        self.button_ban.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.button_submitall = tkinter.Button(button_frame2 , text="SubmitAll")
        self.button_submitall.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        self.button_submitall.configure(state="disabled")
        
        
        self.button_downloadall = tkinter.Button(button_frame2 , text="DownloadAll" , command=self.downloadall)
        self.button_downloadall.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.button_clear = tkinter.Button(button_frame2 , text="Clear", command=self.clear)
        self.button_clear.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.button_drag = tkinter.Button(button_frame2 , text="Drag", command=self.drag)
        self.button_drag.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        self.text_dragnum = tkinter.Text(button_frame2, height=1)
        self.text_dragnum.pack(fill="both", expand=1, side=tkinter.LEFT, anchor=tkinter.SW)
        
        ##########文本框与滚动条
        self.text_dialog_sv = tkinter.Scrollbar(text_frame, orient=tkinter.VERTICAL)  # 文本框-竖向滚动条
#         self.text_dialog_sh = tkinter.Scrollbar(text_frame, orient=tkinter.HORIZONTAL)  # 文本框-横向滚动条

        self.text_dialog = tkinter.Listbox(text_frame, yscrollcommand=self.text_dialog_sv.set)  # 设置滚动条-不换行
        
        
        
        
        for str in DataCenter.PROBLEMLIST:  
            self.text_dialog.insert(self.text_dialog.size(), str)
        
        self.text_input = tkinter.Text(text_frame, height=4)




        # 滚动事件
        self.text_dialog_sv.config(command=self.text_dialog.yview)
#         self.text_dialog_sh.config(command=self.text_dialog.xview)

        # 布局
        button_frame1.pack(fill="x", expand=0, side=tkinter.BOTTOM, anchor=tkinter.SW)
        button_frame2.pack(fill="x", expand=0, side=tkinter.BOTTOM, anchor=tkinter.SW)
        
        self.text_input.pack(fill="x", expand=0, side=tkinter.BOTTOM, anchor=tkinter.SW)
        self.text_dialog_sv.pack(fill="y", expand=0, side=tkinter.RIGHT, anchor=tkinter.N)
#         self.text_dialog_sh.pack(fill="x", expand=0, side=tkinter.BOTTOM, anchor=tkinter.N)
        self.text_dialog.pack(fill="both", expand=1, side=tkinter.LEFT)
        
        
        # 绑定事件
#         self.text_dialog.bind("<Control-Key-a>", self.selectAll)
#         self.text_dialog.bind("<Control-Key-A>", self.selectAll)
#         self.text_input.bind('<Return>', self.sendMessage)
        
        
#         self.text_dialog.configure(state="disabled")
        
        ##########文本框与滚动条end

    
if __name__ == "__main__":
    cha = MainFrame();
    cha.start_window();
