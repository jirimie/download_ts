# -*- coding: utf-8 -*-
"""
desc: download ts file
@author: jirimie
"""

# python3下测试
import requests
import threading
import datetime
import sys, os
import logging
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)

count =0;
def Handler(start, end, url, filename, save_path, thread_id):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=10))
    s.mount('https://', HTTPAdapter(max_retries=10))
    for i in filename[start:end]:
        global count
        try:
            r = s.get(url+i.replace("\n",""), stream=True, timeout = 60)
            #r = requests.get(url, stream=True) 
            with open(save_path+i.replace("\n",""), "wb") as code:
                 code.write(r.content)
        except :
            logger.info(i)
            continue
        count =count+1
        print("线程%d, 下载进度：%.2f" % (thread_id, count/len(filename)))
 
def download_file(url, m3u8_file, save_path, num_thread = 5):
    if url == "0":
        return
    f = open(m3u8_file, 'r', encoding='utf-8')
    text_list = f.readlines()
    s_list = []
    for i in text_list:
        if i.find('#EX')==-1:
            s_list.append(i)
            
    f.close()
    file_size = len(s_list)
 
    # 启动多线程写文件
    part = file_size // num_thread  # 如果不能整除，最后一块应该多几个字节
    for i in range(num_thread):
        start = part * i
        if i == num_thread - 1:   # 最后一块
            end = file_size
        else:
            end = start + part
 
        t = threading.Thread(target=Handler, kwargs={'start': start, 'end': end, 'url': url, 
                                                    'filename': s_list, 'save_path':save_path, 
                                                    'thread_id':i})
        t.setDaemon(True)
        t.start()
 
    # 等待所有线程下载完成
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    #print('%s 下载完成' % file_name)
    if count != file_size:
        print("download fail")
        return 0
    else:
        print("download success")
        return 1

def merge_file(need_merge, save_path):
    if need_merge == 0:
        return
    cmd = "copy /b " + save_path + "*.ts .\\0_merge\\" + save_path.replace(".", "").replace("\\", "") + ".mp4"
    print(cmd)
    os.system(cmd)

def rename_file(need_rename, save_path, m3u8_file):
    if need_rename == 0:
        return
    f = open(m3u8_file, 'r', encoding='utf-8')
    text_list = f.readlines()
    s_list = []
    for i in text_list:
        if i.find('#EX')==-1:
            s_list.append(i)
            
    f.close()
    file_size = len(s_list)
    
    for i in range(0, file_size):
        if i < 0:
            continue
        old_name = s_list[i].replace("\n","")
        new_name = "%03d.ts"%(i+1)
        os.rename(os.path.join(save_path, old_name), os.path.join(save_path, new_name))

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("please input url, m3u8 file, save path, need rename file")
        sys.exit(-1)
    url = sys.argv[1]
    m3u8_file = sys.argv[2]
    save_path = sys.argv[3]
    need_rename = sys.argv[4]
    need_merge = sys.argv[5]
    
    handler = logging.FileHandler(save_path+"fail.txt")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    start = datetime.datetime.now().replace(microsecond=0)  
    ret = download_file(url, m3u8_file, save_path)
    if ret == 1:  
        rename_file(need_rename, save_path, m3u8_file)
        merge_file(need_merge, save_path)
    end = datetime.datetime.now().replace(microsecond=0)
    print("用时: ", end='')
    print(end-start)
