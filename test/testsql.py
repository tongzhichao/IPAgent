import sys
sys.path.append('..')
from db.SqlHelper import SqlHelper
#from util.exception import Con_DB_Fail
class Con_DB_Fail(Exception):
	def __str__(self):
		str = "使用DB_CONNECT_STRING:链接数据库失败"
		return str
try:

	sqlhelper = SqlHelper()
	sqlhelper.init_db()
	#a = 2
	#b = 0
	#a/b
	
#except Con_DB_Fail as e:
#	print(e)
#	print('出错')
#except Exception as e:
#	print('-----------------------------------')
#	print('出错')
except Exception as e:
	print('----------------------------')
	print('error')
	raise Con_DB_Fail

