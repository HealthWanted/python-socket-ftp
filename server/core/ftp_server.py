import socketserver
import configparser
import hashlib
import json
import os

from lib.file_tramsmission import FileTransmission
from lib.utils import get_token
from conf import settings 



STATUS_CODE  = {
	500 : "Internal server error",

	400 : "Bad request",
	401 : "Unauthorized",
	404 : "Not Found ",

	200 : "OK",
}


class FTPHandler(socketserver.BaseRequestHandler):
	def handle(self):
		self.data = self.request.recv(1024).strip()
		print('Client data: ', self.data)

		while self.data:
			data = json.loads(self.data.decode('utf-8'))
			action = data.get('action', None)
			if action:
				func = getattr(self, '_%s' % data.get('action', None) , None)
				if func:
					func(data)
				else:
					self.send_response(404, 
						{'invalid request': 'action does not exist'})
			else:
				self.send_response(400, 
					{'invalid header': 'need "action"'})

			self.data = self.request.recv(1024).strip()
		else:
			print('Client closed')

	def send_response(self, status_code, data=None):
		response = {'status_code': status_code,
					'status_msg': STATUS_CODE[status_code]}
		if data:
			response.update(data)
			
		self.request.send(json.dumps(response).encode())

	def __validate(func):
		def decorator(self, *args, **kwargs):
			data = args[0]
			if data.get('auth_token', None) == self.auth_token:
				func(self, *args, **kwargs)
			else:
				self.send_response(401, {'detail': 'Invalid token.'})
		return decorator

	def authenticate(self, username, password):
		md5_obj = hashlib.md5()
		md5_obj.update(bytes(password, encoding='utf-8'))
		hash_pass = md5_obj.hexdigest()

		config = configparser.ConfigParser()
		config.read(settings.ACCOUNT_FILE)

		if username in config.sections():
			_password = config[username]['Password']
			if _password == hash_pass:
				
				config[username]['Username'] = username
				return config[username]
			else:
				return None
		else:
			return None

	def _auth(self, *args, **kwargs):
		data = args[0]
		username = data.get('username', None)
		password = data.get('password', None)
		if username and password:
			user = self.authenticate(username, password)
			if user:
				print('pass auth...', username)

				self.auth_token = get_token(username, password)
				self.socket_file_obj = FileTransmission(self.request)
				self.user = user
				self.user_home_dir = os.path.join(settings.USER_HOME,
					self.user['Username'])

				self.send_response(200, 
					{ 'auth_token': self.auth_token})
			else:
				self.send_response(400, 
					{'non_field_errors': 'Unable to login with provided credentials.'})
		else:
			self.send_response(400, 
				{'invalid data': 'username & password is required'})

	@__validate
	def _get(self, *args, **kwargs):
		data = args[0]
		filename = data.get('filename', None)
		if filename:
			file_abs_path = os.path.join(self.user_home_dir,
				filename)
			if os.path.isfile(file_abs_path):
				# https://docs.python.org/3/library/os.path.html#os.path.getsize
				file_size = os.path.getsize(file_abs_path) # file_size should be bytes!
				self.send_response(200, data={'file_size':file_size})

				self.request.recv(1)

				if data.get('md5', None):
					md5_result = self.socket_file_obj.file_sender(file_abs_path,
						is_md5=True)

					# self.request.recv(1)

					self.send_response(200, {'md5':md5_result})
				else:
					self.socket_file_obj.file_sender(file_abs_path)
			else:
				self.send_response(400,
					{'invalid data': 'filename is not exist'})
		else:
			self.send_response(400, 
				{'invalid data': 'filename is required'})

	@__validate
	def _put(self, *args, **kwargs):
		data = args[0]
		file_abs_path = os.path.join(self.user_home_dir,
			data.get('filename'))
		file_size = data.get('file_size', None)

		# this should send back a if the filename + filesize is valid
		# according to the user data
		self.request.send(b'9')

		if data.get('md5', None):
			md5_result = self.socket_file_obj.file_receiver(file_abs_path,
				file_size,
				is_md5=True
				)
			
			# self.request.send(b'9')

			md5_from_sender = self.request.recv(1024).decode('utf-8')
			if md5_result == md5_from_sender:
				self.send_response(200)
			else:
				self.send_response(500, {'File md5': 'validate failed'})
		else:
			self.socket_file_obj.file_receiver(file_abs_path, 
				file_size
				)
			if os.path.isfile(file_abs_path):
				self.send_response(200)
			else:
				self.send_response(500)