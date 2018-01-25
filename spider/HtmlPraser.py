#coding:utf-8
import base64
import sys,requests
sys.path.append('..')
from config import QQWRY_PATH,CHINA_AREA
from util.IPAddress import IPAddresss

import re
from util.compatibility import text_

from lxml import etree

class Html_Parser(object):
	def __init__(self):
		self.ips = IPAddresss(QQWRY_PATH)
		
		
	def parse(self,response,parser):
	
		if parser['type'] == 'xpath':
			return self.XpathPraser(response,parser)
			
		elif parser['type'] == 'regular':
			
			return self.RegularPraser(response,parser)
			
		elif parser['type'] == 'module':
			return getattr(self,parser['moduleName'],None)(response,parser)
		else:
			return None
			
	def AuthCountry(self,addr):
		for area in CHINA_AREA:
			if text_(area) in addr:	
				return True
			return False
			
	def XpathPraser(self,response,parser):
		proxylist = []
		root = etree.HTML(response)
		proxys = root.xpath(parser['pattern'])
		
		for proxy in proxys:
			try:
				ip = proxy.xpath(parser['position']['ip'])[0].text
				port = proxy.xpath(parser['position']['port'])[0].text
				type = 0
				protocol = 0
				addr = self.ips.getIpAddr(self.ips.str2ip(ip))
				
				print(addr)
				country = text_('')
				area = text_('')
				
				if text_('省') in addr or self.AuthCountry(addr):
					country = text_('国内')
					area = addr
				else:
					country = text_('国外')
					area = addr
			except Exception as e:
				continue
				
			proxy = {'ip':ip,'port':int(port),'types':int(type),'protocol':int(protocol),'country':country,'area':area,'speed':100}
			proxylist.append(proxy)
			
		return proxylist
		
	def RegularPraser(self,response,parser):
		proxylist = []
		
		pattern = re.compile(parser['pattern'])
		
		matchs = pattern.findall(response)
		if matchs != None:
			for match in matchs:
				try:
					ip = match[parser['position']['ip']]
					port = match[parser['position']['port']]
					type = 0
					
					protocol = 0 
					addr = self.ips.getIpAddr(self.ips.str2ip(ip))
					country = text_("")
					area = text_('')
					
					if text_('省') in addr or self.AuthCountry(addr):
						country = text_('国内')
						area = addr
					else:
						country = text_('国外')
						area = addr 
						
				except Exception as e:
					continue
					
				proxy = {'ip':ip,'port':port,'types':type,'protocol':protocol,'country':country,'area':area,'speed':100}
			proxylist.append(proxy)
			
		return proxylist
				
				
	def CnproxyPraser(self,response,parser):
			proxylist = self.RegularPraser(response,parser)
			chardict = {'v': '3', 'm': '4', 'a': '2', 'l': '9', 'q': '0', 'b': '5', 'i': '7', 'w': '6', 'r': '8', 'c': '1'}
			
			for proxy in proxylist:
				port  = proxy['port']
				new_port = ''
				for i in range(len(port)):
					if port[i] != '+':
						new_port += chardict[port[i]]
				new_port = int(new_port)
				proxy['port'] = new_port
				
			return proxylist
			
	def proxy_listPraser(self,response,parser):
		proxylist = []
		pattern = re.compile(parser['pattern'])
		matchs = pattern.findall(response)
		
		if matchs:
			for match in matchs:
				try:
					ip_port = base64.b64decode(match.replace("Proxy('","").replace("')",""))
					
					ip = ip_port.split(':')[0]
					port = ip_port.split(':')[1]
					type = 0
					protocol = 0
					addr = self.ips.getIpAddr(self.ips.str2ip(ip))
					country = text_('')
					area = text_('')
					
					if text_('省') in addr or self.AuthCountry(addr):
						country = text_('国内')
						area = addr
						
					else:
						country = text_('国外')
					
						area = addr
				except Exception as e:
					continue
					
				proxy = {'ip': ip, 'port': int(port), 'types': type, 'protocol': protocol, 'country': country,'area': area, 'speed': 100}
				proxylist.append(proxy)
			return proxylist
		
		

if __name__=='__main__':
	url = 'http://www.66ip.cn/index.html'
	r = requests.get(url)
	s = r.content.decode('GBK')
	#print(s)
	parser = {
		'urls':['http://www.66ip.cn/index.html'],
		'type':'xpath',
		'pattern':".//*[@id='main']/div/div[1]/table/tr[position()>1]",
		'position':{'ip':'./td[1]','port':'./td[2]','type':'./td[4]','protocol':''}
	}
	c = Html_Parser()


	proxy = c.parse(s,parser)
	print(proxy)
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
			
			
	

	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
					
				
			
			
			
