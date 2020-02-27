# coding=utf-8
import requests
import sys
from bs4 import BeautifulSoup
import threading
import os
import types

reload(sys)
sys.setdefaultencoding("utf-8")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}

threads = []
id = raw_input("请输入漫画ID:")  # "132"
print "本地地址" + os.getcwd() + "/"
pp = raw_input("存储地址(空白为本地):")
if pp == "": pp = "./"
path = pp + id
print "储存地址为" + path
isignore = raw_input("是否忽略已存在文件(t/f 默认为t忽略):") != "f"
if isignore:
    print "确认为忽略"
else:
    print"确认为覆盖"

try:
    line2 = input("下载线程数(默认为5):")
    line = line2
except:
    line = 5

print "线程数为" + bytes(line)


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print "---  new folder...  ---"
        print "---  OK  ---"
    else:
        print "---  There is this folder!  ---"


def readpath():
    try:
        res = requests.get("https://manhua.fzdm.com/" + id + "/", headers=headers)
        b = BeautifulSoup(res.text, "html.parser")
        fin = b.find_all("div", id="content")
        mkdir(path)
        fin2 = fin[0].find_all("li", class_="pure-u-1-2 pure-u-lg-1-4")
        lef = 0
        for i in fin2:
            savepath = path + "/" + i.find(name="a").get("title")
            mkdir(savepath)
            t = threading.Thread(target=readmap,
                                 args=(
                                     "https://manhua.fzdm.com/" + id + "/" + i.find(name="a").get("href"), savepath, 0))
            t.start()
            threads.append(t)
            lef += 1
            if lef >= line:
                for t in threads:
                    t.join()
                lef = 0

        for t in threads:
            t.join()
        print("所有线程任务完成")
    except:
        print "异常,重试下载"
    else:
        print "下载成功"


def readmap(url, savepath, i):
    try:
        name = savepath.replace(path, "") + "_" + bytes(i)
        print "开始尝试下载" + name
        if isignore and os.path.exists(savepath + "/" + bytes(i) + '.jpg'):
            i += 1
            readmap(url, savepath, i)
            print name + "存在,跳过"
            return

        res = requests.get(url + "index_" + bytes(i) + ".html", headers=headers)
        if res.status_code == 404:
            print name + "已全部下载完毕"
            return

        b = BeautifulSoup(res.text, "html.parser")
        jpg = b.find_all("script", type="text/javascript")
        for str in jpg:
            if str.text.find("document.write(") != -1:
                mhurlindex0 = str.text.find('mhurl="')
                if mhurlindex0 == -1:
                    mhurlindex0 = str.text.find('mhurl1="') + 8
                else:
                    mhurlindex0 += 7

                mhurlindex1 = str.text.find('"', mhurlindex0)
                mhurl = str.text[mhurlindex0:mhurlindex1]
                mhss = "p1.manhuapan.com"
                if mhurl.find("2016") == -1 and mhurl.find("2017") == -1 and mhurl.find("2018") == -1 and mhurl.find(
                        "2019") == -1 and mhurl.find("2020") == -1:
                    mhss = "p2.manhuapan.com"
                mhpicurl = "http://" + mhss + "/" + mhurl
                img = requests.get(mhpicurl)
                # 存储图片，多媒体文件需要参数b（二进制文件）
                f = open(savepath + "/" + bytes(i) + '.jpg', 'ab')
                f.write(img.content)  # 多媒体存储content
                f.close()
        print name + "下载成功"
        i += 1
        readmap(url, savepath, i)
    except:
        print "异常,重试下载"
        readmap(url, savepath, i)


readpath()
