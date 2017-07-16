import hashlib
class FileTransmission(object):
	def __init__(self, socket_conn):
		self.socket_conn = socket_conn

	def __show_process(self, file_size):
		received_size = 0
		current_percent = 0

		while received_size < file_size:
			received_percent = int((received_size / file_size) *100)
			
			if received_percent > current_percent:
				print("#",end="",flush=True)
				current_percent = received_percent

			new_size = yield
			received_size += new_size


	def md5_file_receiver(self, file_obj, file_size):

		md5_obj = hashlib.md5()
		received_size = 0

		while received_size < file_size:
			file_data = self.socket_conn.recv(1024)
			file_obj.write(file_data)

			md5_obj.update(file_data)

			received_size += len(file_data)

			try:
				self.process_obj.send(len(file_data))
			except StopIteration as e:
				print('>100%')
		
		else:
			md5_final_value = md5_obj.hexdigest()
			return md5_final_value

	def md5_file_sender(self, file_obj):
		md5_obj = hashlib.md5()

		for line in file_obj:
			self.socket_conn.send(line)
			md5_obj.update(line)
		else:
			md5_final_value = md5_obj.hexdigest()
			return md5_final_value

	def ordinary_file_receiver(self, file_obj, file_size):
		received_size = 0
		while received_size < file_size:
			file_data = self.socket_conn.recv(1024)
			file_obj.write(file_data)

			received_size += len(file_data)

			try:
				self.process_obj.send(len(file_data))
			except StopIteration as e:
				print('>100%')

		else:
			return True

	def ordinary_file_sender(self, file_obj):
		for line in file_obj:
			self.socket_conn.send(line)
		else:
			return True

	def file_receiver(self, file_abs_path, file_size, is_md5=False):
		self.process_obj = self.__show_process(file_size)
		self.process_obj.__next__()

		with open(file_abs_path, 'wb') as file_obj:
			if is_md5:
				return self.md5_file_receiver(file_obj, 
											file_size)
			else:
				return self.ordinary_file_receiver(file_obj,
											file_size)

	def file_sender(self, file_abs_path, is_md5=False):
		with open(file_abs_path, 'rb') as file_obj:
			if is_md5:
				return self.md5_file_sender(file_obj)
			else:
				return self.ordinary_file_sender(file_obj)