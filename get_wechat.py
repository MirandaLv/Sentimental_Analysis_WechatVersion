
# code source: http://blog.51cto.com/superleedo/2124494
# This code is used to search wechat articles by keywords, not by specific wechat platform

import re
import urllib.request
import time
import sys
import urllib.error
import threading
import queue

urlqueue = queue.Queue()


headers=("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36")

opener = urllib.request.build_opener()
opener.addheaders = [headers]

urllib.request.install_opener(opener)

listurl = list()


##定义代理服务器函数
#def use_proxy(proxy_addr,url):
#       try:
#               import urllib.request
#               proxy=urllib.request.ProxyHandler({'http':proxy_addr})
#               opener=urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
#               urllib.request.install_opener(opener)
#               data=urllib.request.urlopen(url).read().decode('utf-8')
#               data=str(data)
#               return data
#       except urllib.error.URLError as e:
#               if hasattr(e,"code"):
#                       print(e.code)
#               if hasattr(e,"reason"):
#                       print(e.reason)
#               time.sleep(10)
#       except Exception as e:
#               print("exception"+str(e))
#               time.sleep(1)



class getlisturl(threading.Thread):

    def __init__(self, key, pagestart, pageend, urlqueue):

        threading.Thread.__init__(self)
        self.key = key
        self.pagestart = pagestart
        self.pageend = pageend
        self.urlqueue = urlqueue


    def run(self):

        page = self.pagestart
        keycode = urllib.request.quote(key)

        for page in range(self.pagestart, self.pageend+1):

            url = "http://weixin.sogou.com/weixin?type=2&query="+keycode+"&page="+str(page)

            data1 = urllib.request.urlopen(url).read().decode('utf-8')
            data1 = str(data1)
            listurlpat = '<a data-z="art".*?(http://.*?)"'
            listurl.append(re.compile(listurlpat.re.S).findall(data1))
            time.sleep(2)


        print("There are" + str(len(listurl)) + "pages retrieved")

        for i in range(0, len(listurl)):

            time.sleep(6)

            for j in range(0, len(listurl(i))):

                try:

                    url = listurl[i][j]
                    url = url.replace("amp;", "")
                    print("第" + str(i) + "i" + str(j) + "j次入队")
                    self.urlqueue.put(url)
                    self.urlqueue.task_done()

                except urllib.error.URLError as e:

                    if hasattr(e, "code"):
                        print(e.code)

                    if hasattr(e, "reason"):
                        print(e.reason)

                    time.sleep(10)

                except Exception as e:

                    print("exception" + str(e))
                    time.sleep(1)



##定义获取文章内容
class getcontent(threading.Thread):

    def __init__(self,urlqueue):

        threading.Thread.__init__(self)
        self.urlqueue=urlqueue

    def run(self):

        #               i = 0
        # 设置本地文件中的开始html编码

        html1 = '''
            <!DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
            <title>微信文章页面</title>
            </head>
            <body>
                                '''
        fh=open("/home/urllib/test/1.html","wb")
        fh.write(html1.encode("utf-8"))
        fh.close()

        #再次以追加写入的方式打开文件，以写入对应文章内容
        fh=open("/home/urllib/test/1.html","ab")
        i=1
        while(True):
            try:

                url=self.urlqueue.get()
                data=urllib.request.urlopen(url).read().decode('utf-8')
                data=str(data)
                titlepat='var msg_title = "(.*?)";'
                contentpat='id="js_content">(.*?)id="js_sg_bar"'
                title=re.compile(titlepat).findall(data)
                content=re.compile(contentpat,re.S).findall(data)

                #初始化标题与内容
                thistitle = "此次没有获取到"
                thiscontent= "此次没有获取到"

                #如果标题列表不为空，说明找到了标题，取列表第0个元素，即此次标题赋给变量thistitle
                if (title!=[]):

                    thistitle = title[0]

                if (content!=[]):

                    thiscontent = content[0]

                #将标题与内容汇总赋给变量dataall
                dataall = "<p>标题为:"+thistitle+"</p><p>内容为："+thiscontent+"</p><br>"
                fh.write(dataall.encode('utf-8'))
                print("第"+str(i)+"个网页处理")

                time.sleep(1)
                i+=1

            except urllib.error.URLError as e:

                if hasattr(e,"code"):
                    print(e.code)

                if hasattr(e,"reason"):
                    print(e.reason)

                time.sleep(10)
            except Exception as e:

                print("exception"+str(e))
                time.sleep(1)


        fh.close()
        html2='''</body>
        </html>
        '''
        fh=open("/home/urllib/test/1.html","ab")
        fh.write(html2.encode("utf-8"))
        fh.close()

class contrl(threading.Thread):

    def __init__(self,urlqueue):

        threading.Thread.__init__(self)
        self.urlqueue=urlqueue

    def run(self):

        while(True):

            print("程序执行中.....")
            time.sleep(60)

            if(self.urlqueue.empty()):

                print("程序执行完毕。。。")
                exit()


key="科技"
#proxy="122.114.31.177:808"
pagestart=1
pageend=2
#listurl=getlisturl(key,pagestart,pageend)
#getcontent(listurl)
t1=getlisturl(key,pagestart,pageend,urlqueue)
#子进程设置daemon为true，保证程序正常退出
t1.setDaemon(True)
t1.start()
t2=getcontent(urlqueue)
t2.setDaemon(True)
t2.start()
t3=contrl(urlqueue)
t3.start()






























