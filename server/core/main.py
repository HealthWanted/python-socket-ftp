import socketserver
import optparse

from conf import settings
from core.ftp_server import FTPHandler

class ArgvHandler(object):
	def __init__(self):
		self.parser = optparse.OptionParser()
		self.options, self.args = self.parser.parse_args()

		self.verify_args()


	def verify_args(self):
		if self.args:
			func = getattr(self, self.args[0], None)
			if func:
				func()
			else:
				self.parser.print_help()
		else:
			print('Should follow server function')



	def start(self):
		print('--start server---')
		print('On host: %s; Listen Port: %s ' % (settings.HOST, settings.PORT) )
		server = socketserver.ThreadingTCPServer((settings.HOST, settings.PORT), 
												FTPHandler)
		server.allow_reuse_address = True
		server.serve_forever()
