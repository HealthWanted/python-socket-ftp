import hashlib
import time
def get_token(username, password):
	md5_obj = hashlib.md5()

	now = time.time()
	raw_string = '%s%s%s' % (username, time, password)

	md5_obj.update(bytes(raw_string, encoding='utf-8'))

	return md5_obj.hexdigest()
