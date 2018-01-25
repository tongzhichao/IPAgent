#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiprocessing import Value,Queue,Process
from api.apiServer import start_api_server
from db.DataStore import store_data

from validator.Validator import validator,getMyIP
from spider.ProxyCrawl import startProxyCrawl

from config import TASK_QUEUE_SIZE

if __name__ == '__main__':
	myip = getMyIP() #测试后的返回IP(即测试IP)
	print(myip)
	DB_PROXY_NUM = Value('i',0)
	q1 = Queue(maxsize=TASK_QUEUE_SIZE) #存放代理IP的队列
	q2 = Queue()
#	p0 = Process(target=start_api_server)#开个线程启动web.py，可以通过请求该web得到所有的IP
	p1 = Process(target=startProxyCrawl,args=(q1,DB_PROXY_NUM,myip))
	p2 = Process(target=validator,args=(q1,q2,myip))
	p3 = Process(target=store_data,args=(q2,DB_PROXY_NUM))
#	p0.start()
	p1.start()
	p2.start()
	p3.start()
	print('p1的进程',p1.pid)
	print('p2的进程',p2.pid)
	print('p3的进程',p3.pid)
#	p0.join()
	p1.join()
	p2.join()
	
	p3.join()

	

