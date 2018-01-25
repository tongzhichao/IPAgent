#coding:utf-8
import sys
sys.path.append('..')
import datetime
from sqlalchemy import Column,Integer,String,DateTime,Numeric,create_engine,VARCHAR

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
from config import DB_CONFIG,DEFAULT_SCORE

from db.ISqlHelper import ISqlHelper


BaseModel = declarative_base()

class Proxy(BaseModel):#定义数据库的表名及字段名
	__tablename__ = 'proxys'
	id = Column(Integer,primary_key= True,autoincrement=True)
	ip = Column(VARCHAR(16),nullable=False)
	port = Column(Integer,nullable=False)
	types = Column(Integer,nullable = False)
	protocol = Column(Integer,nullable=False,default=0)
	country = Column(VARCHAR(100),nullable=False)
	area = Column(VARCHAR(100),nullable = False)
	updatetime = Column(DateTime(),default=datetime.datetime.utcnow)
	speed = Column(Numeric(5,2),nullable=False)
	score = Column(Integer,nullable=False,default=DEFAULT_SCORE)
	
class SqlHelper(ISqlHelper):
	params = {'ip':Proxy.ip, 'port':Proxy.port, 'types':Proxy.types, 'protocol':Proxy.protocol, 
				'country':Proxy.country, 'area':Proxy.area,'score':Proxy.score}
	
	
	def __init__(self):#链接数据库
		if 'sqlite' in DB_CONFIG['DB_CONNECT_STRING']:
			connect_args = {'check_same_thread':False}
			self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'],echo=False,connect_args=connect_args)
		else:
			self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'],echo=False)
			
		DB_Session = sessionmaker(bind=self.engine)
		self.session = DB_Session()
		
	def init_db(self):#初始化数据库
		BaseModel.metadata.create_all(self.engine)
		
	def drop_db(self):#删除数据库
		BaseModel.metadata.drop_all(self.engine)
		
	def insert(self,value):#插入数据
		proxy = Proxy(ip=value['ip'],port=value['port'],types=value['types'],protocol=value['protocol'],			country=value['country'],
					area=value['area'],speed=value['speed'])
		
		self.session.add(proxy)
		self.session.commit()
		
	def delete(self,conditions=None):#删除数据
		print('conditions的值：',conditions)	
		if conditions:
			conditon_list=[]
			for key in list(conditions.keys()):#遍历需要删除的字典conditions
				print('params的值是：',self.params)
				if self.params.get(key,None):#param有定义过需删除的key
					conditon_list.append(self.params.get(key)==conditions.get(key))#将需要删除的value传给params,并添加到列表
					print('conditon的列表值是',conditon_list)
			conditions = conditon_list
			query = self.session.query(Proxy) #获得该表的映射方法
			for condition in conditions:
				query = query.filter(condition) #子查询
				
			deleteNum = query.delete()
			self.session.commit()
			
		else:
			deleteNum = 0
			
		return ('deleteNum',deleteNum)
		
	def update(self,conditions=None,value=None):#更新数据库
		
		if conditions and value:
			conditon_list = []
			for key in list(conditions.keys()):
				if self.params.get(key,None):
					conditon_list.append(self.params.get(key)==conditions.get(key))
					
			conditions = conditon_list
			query = self.session.query(Proxy)
			for condition in conditions:
				query = query.filter(condition)
				
			updatevalue={}
			for key in list(value.keys()):
				if self.params.get(key,None):
					updatevalue[self.params.get(key,None)] = value.get(key)
			updateNum = query.update(updatevalue)
			self.session.commit()
			
		else:
			updateNum = 0
		return {'updateNum':updateNum}
		
	def select(self,count=None,conditions=None):#选择数据，不填参数，默认全选
		if conditions:
			conditon_list =[]
			print(list(conditions.keys()))
			for key in list(conditions.keys()):
				if self.params.get(key,None):
					print(self.params.get(key))
					print(conditions.get(key))
					conditon_list.append(self.params.get(key)==conditions.get(key))
					print(conditon_list)
			conditions = conditon_list
			
		else:
			conditions = []
		print('conditions',conditions)	
		query = self.session.query(Proxy.ip,Proxy.port,Proxy.score)
		if len(conditions)> 0 and count:
			for condition in conditions:
				query = query.filter(condition)
			return query.order_by(Proxy.score.desc(),Proxy.speed).limit(count).all()
			
		elif count:
			return query.order_by(Proxy.score.desc(),Proxy.speed).limit(count).all()
			
		elif len(conditions)>0:
			for condition in conditions:
				query = query.filter(condition)
			return query.order_by(Proxy.score.desc(),Proxy.speed).all()
		else:
			return query.order_by(Proxy.score.desc(),Proxy.speed).all()
			
	def close(self):
		pass

if __name__=='__main__':
	sqlhelper = SqlHelper()
	sqlhelper.init_db()
	count = 10
	ipxoy = {'ip': '120.25.253.234', 'port': 8118}
	s = sqlhelper.select(count,ipxoy)
	print(s)
	#proxy={'ip':'192.168.1.1','port':80,'types':0,'protocol':0,'country':'中国','area':'广州','speed':11.23}
	#sqlhelper.insert(proxy)
	#sqlhelper.update({'ip':'192.168.1.1','port':80},{'score':10})
	#values = {'ip': '192.168.1.1', 'port': 80, 'types': 0, 'protocol': 0, 'country': '中国', 'area': '广州', 'speed': 11.12}
	#values = {'ip':'192.168.1.1'}
	#print(sqlhelper.select(1))

	#sqlhelper.delete(values)
	#print('删除成功')
			
