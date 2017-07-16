import os, json, sys
import socket
import optparse
import getpass
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from file_transmission import FileTransmission

class FTPClient(object):
	def __init__(self):
		parser = optparse.OptionParser()
		parser.add_option('-s', '--server',
						dest='server',
						help='ftp server ip addr')
		parser.add_option('-P', '--port',
						type='int',
						dest='port',
						help='ftp server ip port')
		parser.add_option('-p', '--password',
						dest='password',
						help='password')
		parser.add_option('-u', '--username',
						dest='username',
						help='username')
		self.options, self.args = parser.parse_args()
		self.auth_token = None
		self.user = None
		
		self.verify_args()
		self.make_connection()

	def verify_args(self):
		if self.options.server and self.options.port:
			if self.options.port > 0 and self.options.port < 65535:
				if self.options.username and self.options.password:
					pass
				else:
					if self.options.username is None and \
					self.options.password is None:
						pass
					else:
						exit('Err: username+password should be a pair')
			else:
				exit('host port in 0-65535')
		else:
			exit('Server & Port is required')

	def make_connection(self):
		self.sock = socket.socket()
		self.sock.connect((self.options.server, self.options.port))

	def help(self):
		help_msg = '''
		get [filename]
		put [filename]
		get [filename] --md5
		put [filename] --md5
		'''
		print(msg)

	def interactive(self):
		if self.auth():
			print('Welcome to FTP Client')

			exit_flag = False
			while not exit_flag:
				# e.g: get python.pdf; put python.pdf
				choice = input('Input your cmd [%s]: ' % self.user).strip()
				if len(choice) == 0: 
					exit_flag = True
				else:
					cmd_list = choice.split()
					# the first element is always command
					func = getattr(self, '_%s' % cmd_list[0], None)
					if func:
						func(cmd_list)
					else:
						print("Func not implement yet")
						self.help()
		else:
			print('Login Failed')

	def get_response(self):
		data = self.sock.recv(1024)
		if data:
			data = json.loads(data.decode('utf-8'))
		else:
			data = {'status_code': 500, 'status_msg':'Internal server error'}
		return data

	def authenticate(self, username, password):
		data = {
			'action': 'auth',
			'username': username,
			'password':password
		}
		self.sock.send(json.dumps(data).encode('utf-8'))

		response = self.get_response()
		if response.get('status_code') == 200:
			self.auth_token = response.get('auth_token')
			self.socket_file_obj = FileTransmission(self.sock)
			self.user = username
			return True
		else:
			return False


	def auth(self):
		if self.options.username:
			return self.authenticate(self.options.username, 
				self.options.password)
		else:
			retry = 0
			while retry < 3 :
				username = input('username: ').strip()
				password = input('password: ').strip()
				if self.authenticate:
					return True
				else:
					retry += 1
			print('You have tried too many times')
			return False

	def __md5_required(self, cmd_list):
		if '--md5' in cmd_list:
			return True

	def _get(self, cmd_list):
		if len(cmd_list) == 1:
			print('No file name follows')
			return None

		data_header = {
			'action': 'get',
			'filename': cmd_list[1],
			'auth_token': self.auth_token
		}
		is_md5 = self.__md5_required(cmd_list)
		if is_md5:
			data_header['md5'] = True

		self.sock.send(json.dumps(data_header).encode('utf-8'))

		response = self.get_response()
		if response.get('status_code', None) == 200:

			self.sock.send(b'9')

			base_filename = cmd_list[1].split('/')[-1]
			if is_md5:
				md5_result = self.socket_file_obj.file_receiver(base_filename,
					response['file_size'],
					is_md5=True)

				# self.sock.send(b'9')

				md5_from_server = self.get_response()
				if md5_from_server['md5'] == md5_result:
					print('%s consistence verification success' % base_filename)
				else:
					print('%s consistence verification Failed' % base_filename)

			else:
				self.socket_file_obj.file_receiver(base_filename,
					response['file_size'])
				print('file got')
		else:
			print('Fail to get file')
			print('detail: ', response)

	def _put(self, cmd_list):
		if len(cmd_list) == 1:
			print('No file name follows')
			return None

		filename = cmd_list[1]
		base_filename = filename.split('/')[-1]
		if os.path.isfile(filename):
			data_header = {
				'action': 'put',
				'filename': base_filename,
				# https://docs.python.org/3/library/os.path.html#os.path.getsize
				# file_size should be bytes!
				'file_size': os.path.getsize(filename),
				'auth_token': self.auth_token
			}
			is_md5 = self.__md5_required(cmd_list)
			if is_md5:
				data_header['md5'] = True

			# sock can only send "bytes"
			self.sock.send(json.dumps(data_header).encode('utf-8'))

			# 1. wait for server to confirm 2. in case of sticky packet
			self.sock.recv(1)

			if is_md5:
				md5_result = self.socket_file_obj.file_sender(filename,
					is_md5=True)

				# self.sock.recv(1)

				self.sock.send(md5_result.encode('utf-8'))
				response = self.get_response()
				if response['status_code'] == 200:
					print('%s consistence verification success' % base_filename)
				else:
					print('Fail to put file')
					print('detail: ', response)
			else:
				self.socket_file_obj.file_sender(filename)
				response = self.get_response()
				if response['status_code'] == 200:
					print('file uploaded')
				else:
					print(response)

if __name__ == '__main__':
	ftp = FTPClient()
	ftp.interactive()