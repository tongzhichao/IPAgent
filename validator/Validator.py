# coding:utf-8
import sys
sys.path.append('..')
import chardet
from gevent import monkey #异步协程
monkey.patch_all()

import json
import os
import gevent
import requests
import time
import psutil
from multiprocessing import Process,Queue

import config
from db.DataStore import sqlhelper
from util.exception import Test_URL_Fail


def detect_from_db(myip,proxy,proxies_set):
	proxy_dict = {'ip':proxy[0],'port':proxy[1]}
	result = detect_proxy(myip,proxy_dict)
#	print('IP检查的结构',result)
	if result:
		print('该数据库代理IP可用',proxy[0])
		proxy_str = '%s:%s' %(proxy[0],proxy[1])
		proxies_set.add(proxy_str) #可用的代理IP，存放到集合内
		
	else:
		if proxy[2] < 1:
			print('该代理IP即将被删除',proxy[0])
			sqlhelper.delete({'ip':proxy[0],'port':proxy[1]}) #如果该代理IP分数小于1，则删除
		else:
			score = proxy[2] - 1
			print('该代理IP分数减1',proxy[0])
			sqlhelper.update({'ip':proxy[0],'port':proxy[1]},{'score':score})#否则代理IP分数减1，更新数据库分数
			proxy_str = '%s:%s' % (proxy[0],proxy[1])
			proxies_set.add(proxy_str)#将代理IP放入集合
			
			
		
def validator(queue1,queue2,myip):
#queue1为新爬取的代理IP队列
#queue2为校验新代理IP后的队列
	tasklist = []  #新代理IP的存放列表
	proc_pool = {} #存放新代理IP进程号为Key，进程为value的字典,用于判断进程数
	cntl_q = Queue() #控制信息队列,进程pid队列
	while True:
		if not cntl_q.empty():
			try:

				pid = cntl_q.get()
				print('准备杀死的进程',pid)
				proc = proc_pool.pop(pid)
				proc_ps = psutil.Process(pid)
				proc_ps.kill()
				proc_ps.wait()
				print('杀死进程')
			except Exception as e:
				pass 
				print(e)
				print('不能杀死进程')
		try:
			if len(proc_pool) >= config.MAX_CHECK_PROCESS:
				time.sleep(config.CHECK_WATI_TIME)
				continue
				
			proxy = queue1.get()
#			print('本次校验的IP是：',proxy['ip'])
			tasklist.append(proxy)
			if len(tasklist) >= config.MAX_CHECK_CONCURRENT_PER_PROCESS:
				p = Process(target=process_start,args=(tasklist,myip,queue2,cntl_q)) #每次校验都会产生新的进程，故需要杀死
				p.start()
				print('产生的新进程',p.pid)
				proc_pool[p.pid] = p
				tasklist = []
				
		except Exception as e:
			if len(tasklist) > 0:
				p = Process(target=process_start,args=(tasklist,myip,queue2,cntl_q))
				p.start()
				proc_pool[p.pid] = p 
				tasklist = []
				
def process_start(tasks,myip,queue2,cntl):
	print('启动进程')

	spawns = []
	for task in tasks:
		spawns.append(gevent.spawn(detect_proxy,myip,task,queue2))
	gevent.joinall(spawns)
	cntl.put(os.getpid())
#	print('加入到进程队列管理:',os.getpid())

	
	
#protocol为协议类型，0：http,1:https,2:http/https
#type为类型，	0: 高匿,1:匿名,2 透明
#speed为速度，使用代理IP访问的速度
def detect_proxy(selfip,proxy,queue2=None): #检查代理IP是否可用，可用则返回更新后的代理IP，不可以则返回None
	
	ip = proxy['ip']
	print('本次校验的IP是：',ip)
	port = proxy['port']
	proxies = {'http':'http://%s:%s'%(ip,port),'https':'https://%s:%s'%(ip,port)}
	protocol,types,speed = getattr(sys.modules[__name__],config.CHECK_PROXY['function'])(selfip,proxies) #通过获得属性方法，即相当于运行checkProxy(selfip,proxies)
	if protocol >=0:
		proxy['protocol'] = protocol
		proxy['types'] = types
		proxy['speed'] = speed 
		print('该代理IP可用',ip)
		
	else:
		proxy = None 
		print('该代理IP不可用',ip)
	if queue2:
		queue2.put(proxy)
	return proxy  
	
def checkProxy(selfip,proxies): #检查代理IP是否可用
	
	protocol = -1 
	types = -1 
	speed = -1 
	http,http_types,http_speed = _checkHttpProxy(selfip,proxies)
	print('http的返回值')
	print(http,http_types,http_speed)
	https,https_types,https_speed = _checkHttpProxy(selfip,proxies,False)
	print('https返回的值：')
	print(https,https_types,https_speed)
	
	if http and https:
		protocol = 2 
		types = http_types 
		speed = http_speed
	elif http:
		types = http_types 
		protocol = 0 
		speed = http_speed 
	elif https:
		types = https_types 
		protocol = 1 
		speed = https_speed 
	else:
		types = -1
		protocol = -1 
		speed = -1
		
	return protocol ,types,speed
	
	
def _checkHttpProxy(selfip,proxies,isHttp=True): #检查代理IP是否可用具体函数
	print('准备验证的代理ip为：',proxies)
	types = -1 
	speed = -1 
	if isHttp:
		test_url = config.TEST_HTTP_HEADER
	
	else:
		test_url = config.TEST_HTTPS_HEADER 
		
	try:
		start = time.time()
		r = requests.get(url=test_url,headers=config.get_header(),timeout=config.TIMEOUT,proxies= proxies)
		
		if r.ok:
			speed = round(time.time() - start, 2)
			content = json.loads(r.text)
			headers = content['headers']
			ip = content['origin']
			proxy_connection = headers.get('Proxy-Connection',None)
			
			if ',' in ip:
				types = 2 
			elif proxy_connection:
				types = 1 
				
			else:
				types = 0 
				
			return True,types,speed 
		else:
			return False ,types,speed 
			
	except Exception as e:
		print('出错')
		print(False,types,speed)
		return False ,types,speed  
		
		
def baidu_check(selfip,proxies):
	
	protocol = -1 
	types = -1 
	speed = -1 
	
	try:
		start = time.time()
		r = requests.get(url='https://www.baidu.com',headers=config.get_header(),timeout=config.TIMEOUT,proxies=proxies)
		r.encoding = chardet.detect(r.content)['encoding']
		
		if r.ok:
			speed = round(time.time() - start,2)
			protocol = 0 
			types = 0 
			
		else:
			speed = -1 
			protocol = -1 
			types = -1 
	except Exception as e:
		speed = -1 
		protocol = -1 
		types = -1 
	return protocol,types ,speed


def getMyIP():
	try:
		r = requests.get(url=config.TEST_IP,headers=config.get_header(),timeout=config.TIMEOUT)
		ip = json.loads(r.text)
		return ip['origin']
	except Exception as e:
		raise Test_URL_Fail
		
if __name__ == '__main__':
	ip = '124.165.252.72'
	port = 80
	proxies = {"http":"https://%s:%s" %(ip,port),"https":"https://%s:%s" %(ip,port)}
	c = _checkHttpProxy(None,proxies)
	print(c)
		
