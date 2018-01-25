import web 
import sys
urls = (
	'/index','index',
	'/blog/\d+','blog',
	'/(.*)','hello')

app = web.application(urls,globals())

class hello:
	def GET(self,name):
		return 'hello' + name 

class index:
	def GET(self):
		return 'index method'

class blog:
	def GET(self):
		return 'blog GET method'

	def POST(self):
		return 'blog POST method'


#class hello:
#	def GET(self,name):
#		i = web.input(times=1)
#		if not name:
#			name = 'world'
#		for c in range(int(i.times)):
#			print('hello',name+'!')
#		return 'hello,' + name + '!'

if __name__ == '__main__':
	sys.argv.append('0.0.0.0:8000')
	app = web.application(urls,globals())
	app.run()
