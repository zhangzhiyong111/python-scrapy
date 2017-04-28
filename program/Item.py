#coding=utf-8
#!/usr/bin/env python2

class Item:
	def __init__(self):
		#网站的url
		self.url = ""
		#旅游目的地
		self.destination = ""
		#游记的标题
		self.title = ""
		#游记的文本
		self.content = ""
		#这个是一个字典
		self.infor = dict()
	def setUrl(self, url):
		self.infor["url"] = url
	def setDestination(self, destination):
		self.infor["destination"] = destination
	def setTitle(self, title):
		self.infor["title"] = title
	def setContent(self, content):
		self.infor["content"] = content
