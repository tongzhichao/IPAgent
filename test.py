# coding:utf-8
import time
import gevent
#from gevent import select,Timeout,Event
from gevent import Greenlet
from gevent.event import Event
evt = Event()

from gevent.queue import Queue

tasks = Queue(maxsize=3)


def worker(n):

    try:
        while not tasks.empty():
            task = tasks.get(timeout=1)
            print('worker %s got task %s ' % (n, task))
            gevent.sleep(0)
    except Empty:
        print('Quitting time')
    print('Quitting time')


def boss():
    for i in range(1, 10):
        tasks.put(i)
    print('Assigned all workd in iteration 1')
    for i in range(10, 20):
        tasks.put(i)
    print('Assigned all work in interaiton 2')

# gevent.spawn(boss).join()

gevent.joinall([
    gevent.spawn(boss),
    gevent.spawn(worker, 'steve'),
    gevent.spawn(worker, 'john'),
    gevent.spawn(worker, 'nancy'),
])


'''
def setter():
	print('A:Hey wait for me,I have to do something')
	gevent.sleep(3)
	print('OK,i done')
	evt.set()

def waiter():
	print('i wait for you ')
	evt.wait()
	print('it is about time')

def main():
	gevent.joinall([
		gevent.spawn(setter),
		gevent.spawn(waiter),
		gevent.spawn(waiter),
		gevent.spawn(waiter),
		gevent.spawn(waiter),
		gevent.spawn(waiter),
])

if __name__ == '__main__':
	main()



seconds = 10 

timeout = Timeout(seconds)
timeout.start()

def wait():
	gevent.sleep(10)

try:
	gevent.spawn(wait).join()
except Timeout:
	print('could not complete')





def win():
	return 'you win'

def fail():
	raise Exception('you fail at failing')

winner = gevent.spawn(win)
loser = gevent.spawn(fail)

print(winner.started)
print(loser.started)

try:
	gevent.joinall([winner,loser])

except Exception as e:
	print('This will never be reached')

print(winner.value)
print(loser.value)

print(winner.ready())
print(loser.ready())

print(winner.successful())
print(loser.successful())


print(loser.exception)






class MyGreenlet(Greenlet):
	def __init__(self,message,n):
		Greenlet.__init__(self)
		self.message = message
		self.n = n 

	def _run(self):
		print(self.message)
		gevent.sleep(self.n)

g = MyGreenlet('hi there',3)
g.start()
g.join()



def echo(i):
	time.sleep(0.001)
	return i 

def foo(message,n):
	gevent.sleep(n)
	print(message)

thread1 = Greenlet.spawn(foo,'hello',1)

thread2 = Greenlet.spawn(foo,'I live',2)

thread3 = Greenlet.spawn(lambda x:(x+1),2)

threads = [thread1,thread2,thread3]
gevent.joinall(threads)


from multiprocessing.pool import Pool 

p = Pool(10)
run1 = [a for a in p.imap_unordered(echo,range(10))]
run2 = [a for a in p.imap_unordered(echo,range(10))]
run3 = [a for a in p.imap_unordered(echo,range(10))]
run4 = [a for a in p.imap_unordered(echo,range(10))]
print(run1,run2,run3,run4)
print(run1 == run2 == run3 == run4)

from gevent.pool import Pool 
p = Pool(10)

run1 = [a for a in p.imap_unordered(echo,range(10))]
run2 = [a for a in p.imap_unordered(echo,range(10))]

run3 = [a for a in p.imap_unordered(echo,range(10))]
run4 = [a for a in p.imap_unordered(echo,range(10))]

print(run1,run2,run3,run4)
print(run1 == run2 == run3 == run4)


start = time.time()
tic = lambda:'at %1.1f seconds' % (time.time() - start)
def gr1():
	print('started polling:%s' % tic())
	select.select([],[],[],2)
	print('Ended polling:%s' % tic())

def gr2():
	print('Started polling:%s' % tic())
	select.select([],[],[],2)
	print('End polling:%s' % tic())

def gr3():
	print('Hey lets do some stuff while the greenlets poll,%s'% tic())
	gevent.sleep(1)

gevent.joinall([
	gevent.spawn(gr1),
	gevent.spawn(gr2),
	gevent.spawn(gr3),
])




def foo():
	print('running in foo')
	gevent.sleep(0)
	print('Explicit context switch to foo agin')

def bar():
	print('Explicit content to bar')
	gevent.sleep(0)
	print('Implicit context switch back to bar')

gevent.joinall([gevent.spawn(foo),gevent.spawn(bar),])





import requests
import json 
s = int(input('请输入1-5位正数：'))
r = requests.get('http://127.0.0.1:8000/?types=0&count=5&country=国内')
ip_ports = json.loads(r.text)
ip = ip_ports[s][0]
port = ip_ports[s][1]

proxies = {
	'http':'http://%s:%s'%(ip,port),
	'https':'https://%s:%s'%(ip,port)}

print(proxies)
#r = requests.get('http://ip.chinaz.com/',proxies=proxies)
r = requests.get('http://ip.chinaz.com/getip.aspx',proxies=proxies)
r.encoding = 'utf-8'

print(r.text)
'''
