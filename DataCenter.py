  # coding utf-8
VERSION = "0.8";
import urllib.parse
import urllib.request
import http.client
import json
import http.cookiejar
import MainFrame
import DataCenter
import pdfkit
import webbrowser
import threading
import shutil
import time
import os

# 设置
# setting

HANDLE = "";
PASSWORD = "";
PDFCONFIG = pdfkit.configuration(wkhtmltopdf=b"d:/wkhtmltopdf/bin/wkhtmltopdf.exe")
DEBUG = 1;
POOL_SIZE_LIMIT = 20;
CF_MAX_PROBLEMPAGE = 32;

COOKIE_FILE = "data/cookie.txt";
BANLIST_FILE = "data/banlist.txt";
PROBLEMLIST_FILE = "data/problemlist.txt";



# 初始化
# init

POOL_SIZE_NOW = 0;
COOKIE = http.cookiejar.MozillaCookieJar(COOKIE_FILE)
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE))

CSRF_TOKEN = "";
FTAA = "";
BFAA = "";
BANLIST = [];
PROBLEMLIST = [];
MF = "";

def pdfdownload(url, path):
    try:
        pdfkit.from_url(url , path, configuration=DataCenter.PDFCONFIG);
    except Exception as e:
        if(DataCenter.DEBUG):
            print(e);
        
def all_txt_wrap_by(start_str, end_str, html_str):
    '''取出字符串html_str中的，被start_str与end_str包绕的所有字符串'''
    reslist = [];
    while (1):
        start = html_str.find(start_str);
        if start >= 0:
            start += len(start_str);
            end = html_str.find(end_str, start);
            if end >= 0:
                reslist.append(html_str[start:end].strip());
                html_str = html_str[end:];
#                 print(html_str);
            else:
                return reslist;
        else:
            return reslist;   

def txt_wrap_by(start_str, end_str, html_str):
    '''取出字符串html_str中的，被start_str与end_str包绕的字符串'''
    start = html_str.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html_str.find(end_str, start)
        if end >= 0:
            return html_str[start:end].strip()

def output_to_file(file_name_str, file_str):
    file_output = open(file_name_str, 'w+', encoding="utf-8")
    file_output.write(file_str)
    file_output.close()
    
def login():
    if(DataCenter.HANDLE == ''):
        return;
    result = DataCenter.OPENER.open("http://codeforces.com/enter");
    DataCenter.COOKIE.save(ignore_discard=True, ignore_expires=True)
    html_str = result.read().decode("utf-8");
    if DataCenter.DEBUG:
        output_to_file("test/before.txt", html_str);
    
    DataCenter.CSRF_TOKEN = txt_wrap_by(r"<input type='hidden' name='csrf_token' value='", r"'/>", html_str);
    if DataCenter.DEBUG:
        print(DataCenter.CSRF_TOKEN);
    params = urllib.parse.quote("");
    body = urllib.parse.urlencode({
        "csrf_token" : DataCenter.CSRF_TOKEN,
        "action" : "enter",
        "ftaa" : DataCenter.FTAA,
        "bfaa" : DataCenter.BFAA,
        "handle" : DataCenter.HANDLE,
        "password" : DataCenter.PASSWORD,
        "remember" : "on",
        "_tta" : "785"
    });
    
    result = DataCenter.OPENER.open("http://codeforces.com/enter", data=body.encode("ascii"));
    DataCenter.COOKIE.save(ignore_discard=True, ignore_expires=True)
    html_str = result.read().decode("utf-8");
    if DataCenter.DEBUG:
        output_to_file("test/after.txt", html_str);
    DataCenter.CSRF_TOKEN = txt_wrap_by(r"<input type='hidden' name='csrf_token' value='", r"'/>", html_str);
    DataCenter.FTAA = txt_wrap_by(r'window._ftaa = "', r'";', html_str);
    DataCenter.BFAA = txt_wrap_by(r'window._bfaa = "', r'";', html_str);
    
    if DataCenter.DEBUG:
        print(DataCenter.CSRF_TOKEN);
        print(DataCenter.FTAA);
        print(DataCenter.BFAA);

def load_banlist():
    banfile = open(BANLIST_FILE, "r+")
    banlines = banfile.readlines();
    DataCenter.BANLIST = [];
    for line in banlines:
        DataCenter.BANLIST.append(line.strip());
    if DataCenter.DEBUG:
        print(DataCenter.BANLIST);
    banfile.close();

def load_problemlist():
    problemfile = open(PROBLEMLIST_FILE, "r+")  
    problemlines = problemfile.readlines();
    DataCenter.PROBLEMLIST = [];
    for line in problemlines:
        DataCenter.PROBLEMLIST.append(line.strip());
    if DataCenter.DEBUG:
        print(DataCenter.PROBLEMLIST);
    problemfile.close();
        
def save_banlist():
    banfile = open(BANLIST_FILE, "w+")  
    for line in DataCenter.BANLIST:
        banfile.write(line);
        banfile.write("\n");
    if DataCenter.DEBUG:
        print(DataCenter.BANLIST);
    banfile.close();
        
def save_problemlist():
    problemfile = open(PROBLEMLIST_FILE, "w+")  
    for line in DataCenter.PROBLEMLIST:
        problemfile.write(line);
        problemfile.write("\n");
    if DataCenter.DEBUG:
        print(DataCenter.PROBLEMLIST);
    problemfile.close();

def main():
    try:
        login();
    except Exception as e:
        if(DataCenter.DEBUG):
            print(e);
            
    if not os.path.exists("problemset"):
        os.mkdir("problemset");
    if not os.path.exists("data"):
        os.mkdir("data");
    if not os.path.exists("test"):
        os.mkdir("test");
    if not os.path.exists("code"):
        os.mkdir("code");
        
    banfile = open(BANLIST_FILE, "w+")  
    banfile.write('');
    banfile.close();

    problemfile = open(PROBLEMLIST_FILE, "w+")  
    problemfile.write('');
    problemfile.close();
    
    load_banlist();
    load_problemlist();
    
    DataCenter.MF = MainFrame.MainFrame();
    DataCenter.MF.start_window();

class PdfDownloader(threading.Thread):
    def __init__(self, url, path):
        threading.Thread.__init__(self)
        self.url = url;
        self.path = path;    
        
    def run(self):
        while(1):
            if (DataCenter.POOL_SIZE_NOW < DataCenter.POOL_SIZE_LIMIT):
                DataCenter.POOL_SIZE_NOW += 1;
                DataCenter.pdfdownload(self.url , self.path);
                if not os.exist("problemset"):
                    os.mkdir("problemset");
                shutil.move(self.path, "problemset/")
                DataCenter.POOL_SIZE_NOW -= 1;
                break;
            else:
                time.sleep(1);
                
def submit(problem_id, programTypeId=42):
    result = DataCenter.OPENER.open("http://codeforces.com/problemset/submit");
    DataCenter.COOKIE.save(ignore_discard=True, ignore_expires=True)
    
    html_str = result.read().decode("utf-8");
    if DataCenter.DEBUG:
        output_to_file("test/sbefore.txt", html_str);
    
    DataCenter.CSRF_TOKEN = txt_wrap_by(r"<input type='hidden' name='csrf_token' value='", r"'/>", html_str);
#     DataCenter.FTAA = txt_wrap_by(r'window._ftaa = "', r'";', html_str);
#     DataCenter.BFAA = txt_wrap_by(r'window._bfaa = "', r'";', html_str);
    
    if DataCenter.DEBUG:
        print(DataCenter.CSRF_TOKEN);
        print(DataCenter.FTAA);
        print(DataCenter.BFAA);
    params = urllib.parse.quote("");
    
    boundary = "------WebKitFormBoundaryIvB2cxeQ7OrkJlwD"
    body = '';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="csrf_token"\n\n';
    body += DataCenter.CSRF_TOKEN;
    body += '\n';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="ftaa"\n\n';
    body += DataCenter.FTAA;
    body += '\n';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="bfaa"\n\n';
    body += DataCenter.BFAA;
    body += '\n';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="action"\n\n';
    body += 'submitSolutionFormSubmitted';
    body += '\n';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="submittedProblemCode"\n\n';
    body += problem_id;
    body += '\n';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="programTypeId"\n\n';
    body += str(programTypeId);
    body += '\n';
    
    body += boundary;
    body += '\nContent-Disposition: form-data; name="source"\n\n';
    f = open("code/" + problem_id + ".txt", "r");
    body += f.read();
    body += '\n';
    body += r'''------WebKitFormBoundaryIvB2cxeQ7OrkJlwD
Content-Disposition: form-data; name="tabSize"

4
------WebKitFormBoundaryIvB2cxeQ7OrkJlwD
Content-Disposition: form-data; name="sourceFile"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundaryIvB2cxeQ7OrkJlwD
Content-Disposition: form-data; name="_tta"

5
------WebKitFormBoundaryIvB2cxeQ7OrkJlwD--
'''
    
    
    
    if DataCenter.DEBUG:
        print(body);
    req = urllib.request.Request("http://codeforces.com/problemset/submit?csrf_token=" + DataCenter.CSRF_TOKEN, body.encode("utf-8"));
    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8");
    req.add_header("Accept-Encoding", "plain_text");
    req.add_header('Accept-Language', 'zh-CN,zh;q=0.8');
    req.add_header('Cache-Control', 'max-age=0');
    req.add_header('Connection', 'keep-alive');
    req.add_header("Content-length", str(len(body)));
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary);

    req.add_header('Host', 'codeforces.com');
    req.add_header('Origin', 'http://codeforces.com');
    req.add_header('Referer', 'http://codeforces.com/problemset/submit');
    req.add_header('Upgrade-Insecure-Requests', '1');
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0');
    
    result = DataCenter.OPENER.open(req);
#     result = DataCenter.OPENER.open("http://codeforces.com/problemset/submit?csrf_token=" + DataCenter.CSRF_TOKEN, data=body.encode("utf-8"));
    DataCenter.COOKIE.save(ignore_discard=True, ignore_expires=True)
    html_str = result.read().decode("utf-8");
    
    if DataCenter.DEBUG:
        output_to_file("test/safter.txt", html_str);
    DataCenter.CSRF_TOKEN = txt_wrap_by(r"<input type='hidden' name='csrf_token' value='", r"'/>", html_str);
#     DataCenter.FTAA = txt_wrap_by(r'window._ftaa = "', r'";', html_str);
#     DataCenter.BFAA = txt_wrap_by(r'window._bfaa = "', r'";', html_str);
    
    if DataCenter.DEBUG:
        print(DataCenter.CSRF_TOKEN);
        print(DataCenter.FTAA);
        print(DataCenter.BFAA);         

if __name__ == "__main__":
    main();
