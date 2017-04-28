#coding=utf-8
#!/usr/bin/env python2

from lxml import etree   #导入xpath库
import time
import urllib2
import urllib
import re
import json
import random
from Item import Item
import sys

reload( sys )
sys.setdefaultencoding( "utf-8" )

class MySpiders:
	#初始化赋值
	def __init__(self):
		self.pageNum = 50   #总共的目录数量
		self.startURL = "http://www.mafengwo.cn/search/s.php?q=普吉岛&p=%d&t=info&kt=1"  #初始化的url
		self.writeFilePath = "./../data/TravelogueJson"   #写入文件的地址

	#读取网页的信息，返回网页的sourceCode,加入user_agent主要的目的是伪装成代理服务器
	def getPageContent(self, url):
		# # 设置用户代理，这个例子没有跑过，不知道行不行，代码是可以，但是代理IP比较难搞
		# proxies=["121.232.147.28:9000","121.232.146.138:9000","114.106.191.207:808","218.249.154.66:8081"] 
		# randIndex = random.randint(0, len(proxies) - 1)                  #随机的选择哪个IP地址
		# proxy_support = urllib2.ProxyHandler( {'http':proxies[randIndex]} )
		# opener = urllib2.build_opener(proxy_support)
		# urllib2.install_opener(opener)

		user_agent = ["Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11", "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16"]   #这里可以设置多个user_agent进行代理
		index = random.randint(0, len(user_agent) - 1)     #使用不同的usr_agent
		headers = { 'User-Agent' : user_agent[index] }    #知乎网站就要加入headers，主要是为了确保是不是浏览器发出来的请求
		try:
			request = urllib2.Request(url, None, headers)   #加入头文件主要是伪装成浏览器
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.HTTPError, e:   #这是是http出现问题，也就是网络访问错误
			print e.code
			return None
		except urllib2.URLError, e:  #这个是url出现问题，可以认为没有这个url
			print e.reason
			return None

	#这个函数的主要目的是提取我们所需要的内容，并且格式化的存放在data目录下面
	def parsePageContent(self, travelogueResponse, traveloguesURL):
		item = Item()
		response = etree.HTML(travelogueResponse)    #j将网页信息转换成html格式，也就是用来解析树

		#获取游记的URL
		item.setUrl(traveloguesURL)
		#获取旅游的标题
		title = response.xpath("//head/title/text()")[0]
		print title
		item.setTitle( title )
		#获取游记的目的地
		destination = response.xpath("//head/meta[@name='keywords']/@content")[0]
		print destination
		item.setDestination( destination )
		
		#获取游记的文本
		content = ""
		for text in response.xpath("//p[contains(@class, '_j_note_content')]/text()"): 
			#之所以采用contains语法，主要在于不同的html文件中有的是_j_note_content _j_seqitem，有的是_j_note_content
			#如果只是一种可以考虑只用"//p[@class='_j_note_content_j_segitem']/text()"
			segment = text.replace("\n", "").replace("\t", "")
			content += segment.strip()
		print content
		item.setContent( content )

		#将item中的信息写入到数据中去
		fw = open(self.writeFilePath, 'a')
		line = json.dumps(dict(item.infor)   , ensure_ascii = False) + "\n"
		fw.write(line)
		fw.close()

	#这个函数的主要目的是解析目录游记，从中获取游记的列表
	def parseDirContent(self, pageDirContent):
		response = etree.HTML(pageDirContent)              #将源码转化为能被XPath匹配的格式
		regex = re.compile( r"http://www.mafengwo.cn/i/[0-9]{6,7}.html" )
		travelList = response.xpath("//div[@class='flt1']/a/@href")
		for traveloguesURL in travelList:
			print "the travelogues page url is : ", traveloguesURL
			if regex.match(traveloguesURL):
				travelogueResponse = self.getPageContent(traveloguesURL)
				if travelogueResponse != None:
					self.parsePageContent(travelogueResponse, traveloguesURL)  #对于正常的游记URL进行解析，获取他的源代码
					sleepTime = random.uniform(10, 60)
					print "the server is resting ... "
					time.sleep(sleepTime)   #让服务器休息10～60秒再进行采集数据
				else:
					print "get the travelogue text failed "

	#这个函数主要目的是为了对目录网页进行分析，并从中获取每篇游记的url
	def startCrawl(self):
		for i in range(1, 1 + self.pageNum):
			currentURL = self.startURL%i
			print "currentURL is : ", currentURL
			print "begin to parse the html "
			pageDirContent = self.getPageContent(currentURL)
			if pageDirContent != None:
				self.parseDirContent(pageDirContent)
			else :
				print "get %d the pageDir failed !!! "%i

if __name__ == '__main__' :
	myspiders = MySpiders()
	myspiders.startCrawl()

#验证获取的代理IP是否有效
# url = "http://quote.stockstar.com/stock"  #打算抓取内容的网页
# proxy_ip={'http': '27.17.32.142:80'}  #想验证的代理IP
# proxy_support = urllib.request.ProxyHandler(proxy_ip)
# opener = urllib.request.build_opener(proxy_support)
# opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64)")]
# urllib.request.install_opener(opener)
# print(urllib.request.urlopen(url).read())
# 若IP是有效的，则可打印出网页源码，否则会出现错误。所以我们可以通过以上代码对所抓取的代理IP逐个进行验证。
#from threading import Thread
#from Queue import Queue
#from time import sleep
## q是任务队列
##NUM是并发线程总数
##JOBS是有多少任务
#q = Queue()
#NUM = 2
#JOBS = 10
##具体的处理函数，负责处理单个任务
#def do_somthing_using(arguments):
#    print arguments
##这个是工作进程，负责不断从队列取数据并处理
#def working():
#    while True:
#        arguments = q.get()
#        do_somthing_using(arguments)
#        sleep(1)
#        q.task_done()
##fork NUM个线程等待队列
#for i in range(NUM):
#    t = Thread(target=working)
#    t.setDaemon(True)
#    t.start()
##把JOBS排入队列
#for i in range(JOBS):
#    q.put(i)
##等待所有JOBS完成
#q.join()
