from multiprocessing import Pool,Process ,Queue

import os,time,random

from sqlalchemy import Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	id = Column(String(20),primary_key = True)
	name = Column(String(20))
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/proxy?charset=utf8')
DBSession = sessionmaker(bind=engine)


session = DBSession()
#Base.metadata.create_all(engine)
#插入数据
#new_user = User(id='5',name='Bob')
#session.add(new_user)
#session.commit()
#session.close()
# 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
#user = session.query(User).filter(User.id=='5').all()
#user = session.query(User).all()
#print(user)
#
#for u in user:
#	print(u)
#	print(u.name)
#print('type:',type(user))
#print('name',user.name)

#session.close()
#user = session.query(User).filter(User.id=='6').one()
#print(user.name)
quser = session.query(User)
print(quser.all())
#quser.filter(User.id=='6').update({'name':'tongzhichao'})
#quser.filter(User.id)
session.flush()
session.commit()

#print(quser.get('6').name)
#quser.filter(User.id=='5').delete()
#session.commit()

'''
def write(q):
	print('process to write:%s' % os.getpid())
	for value in ['a','b','c']:
		print('put %s to queue' % value)
		q.put(value)
		time.sleep(random.random())

def read(q):
	print('Process to read:%s' % os.getpid())
	while True:
		value = q.get(True)
		print('Get %s from queue' % value)

if __name__ == '__main__':
	q = Queue()
	pw = Process(target = write,args=(q,))
	pr = Process(target = read,args=(q,))
	pw.start()
	pr.start()
	pw.join()
	pr.terminate()


def long_time_task(name):
	print('run task %s (%s)..' % (name,os.getpid()))
	start = time.time()
	time.sleep(random.random()*3)
	end = time.time()
	print('task %s runs %0.2f seconds'%(name,(end-start)))

if __name__ == '__main__':
	print('parent process %s' % os.getpid())
	p = Pool(4)
	for i in range(5):
		p.apply_async(long_time_task,args=(i,))
	print('wait for done')
	p.close()
	p.join()
	print('all done')
'''