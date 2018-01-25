# coding:utf-8

from gevent import monkey
monkey.patch_all()

import sys
sys.path.append('..')
import time
import gevent

from gevent.pool import Pool

from multiprocessing import Queue,Process,Value
from api.apiServer import start_api_server
from config import THREADNUM,parserList,UPDATE_TIME,MINNUM,MAX_CHECK_CONCURRENT_PER_PROCESS,MAX_DOWNLOAD_CONCURRENT

from db.DataStore import store_data,sqlhelper
from spider.HtmlDownloader import Html_Downloader
from spider.HtmlPraser import Html_Parser
from validator.Validator import validator,getMyIP,detect_from_db


def startProxyCrawl(queue,db_proxy_num,myip):
	crawl = ProxyCrawl(queue,db_proxy_num,myip)
	crawl.run()
	
#myip:即运行该脚本的本机IP：61.130.0.179
#queue队列，最大传入TASK_QUEUE_SIZE:50
#db_proxy_num,数据库内的代理IP数，当前输入数：0

class ProxyCrawl(object):
	proxies = set() #定义空集合
	
	def __init__(self,queue,db_proxy_num,myip):
		self.crawl_pool = Pool(THREADNUM) #gevent的协程池,值为：5
		self.queue = queue
		self.db_proxy_num = db_proxy_num
		self.myip = myip
		
	def run(self):
		while True:
			self.proxies.clear()
			str = 'IPProxyPool----->>>>>begining'
			sys.stdout.write(str+'\r\n')
			sys.stdout.flush()
			
			proxylist = sqlhelper.select() #获取数据库中所有的代理IP
			print(proxylist)
			spawns = [] #协程组
			
			for proxy in proxylist:
				print(proxy)
				spawns.append(gevent.spawn(detect_from_db,self.myip,proxy,self.proxies))#运行detect_from_db，参数为后三个
				if len(spawns) >= MAX_CHECK_CONCURRENT_PER_PROCESS:
					gevent.joinall(spawns)
					spawns = []
					
			gevent.joinall(spawns)
			self.db_proxy_num.value = len(self.proxies)
			print('本次循环未删除的代理ip剩余：',len(self.proxies))
			str = 'IPProxyPool----->>>db exists ip:%d' % len(self.proxies)
			
			if len(self.proxies) < MINNUM:
				str += '\r\nIPProxyPool---->>>now ip num < MINNUM,start crawling...'
				sys.stdout.write(str + '\r\n')
				sys.stdout.flush()
				spawns=[]
				for p in parserList:
					spawns.append(gevent.spawn(self.crawl,p))
					if len(spawns) >= MAX_DOWNLOAD_CONCURRENT:
						gevent.joinall(spawns)
						spawns=[]
				gevent.joinall(spawns)
			else:
				str += '\r\nIPProxyPool---->>now ip num meet the requirement,wait UPDATE_TIME...'
				sys.stdout.write(str + '\r\n')
				sys.stdout.flush()
				
			time.sleep(UPDATE_TIME)
			
			
			
	def crawl(self,parser):
		html_parser = Html_Parser()
		for url in parser['urls']:
			print('crawl的URL是：',url)
			response = Html_Downloader.download(url)
			if response is not None:
				proxylist = html_parser.parse(response,parser)
				if proxylist is not None:
					for proxy in proxylist:
						proxy_str = '%s:%s' % (proxy['ip'],proxy['port'])
						if proxy_str not in self.proxies:
#							self.proxies.add(proxy_str) #感觉没作用
#							print('新爬取得代理IP')
#							print(proxy)
							
							while True:
								
								if self.queue.full():
									time.sleep(0.1)
									
								else:
#									print('将新的爬取到的代理IP放入队列')
									self.queue.put(proxy)
									break
if __name__ == '__main__':
	DB_PROXY_NUM = Value('i',0)
	myip = getMyIP()
	q1 = Queue()
	q2 = Queue()
	p0 = Process(target=start_api_server)
	p1 = Process(target=startProxyCrawl,args=(q1,DB_PROXY_NUM,myip))
	p2 = Process(target=validator,args=(q1,q2,myip))
	p3 = Process(target=store_data,args=(q2,DB_PROXY_NUM))
	
	p0.start()
	p1.start()
	p2.start()
	p3.start()
	
	
									
									
									
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
