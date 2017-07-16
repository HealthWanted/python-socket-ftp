import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_HOME = os.path.join(BASE_DIR, 'home')
LOG_DIR = os.path.join(BASE_DIR, 'log')
LOG_LEVEL = 'DEBUG'

# user psw + username
ACCOUNT_DIR = os.path.join(BASE_DIR, 'conf')
ACCOUNT_FILE = os.path.join(ACCOUNT_DIR, 'accounts.ini')



HOST = '0.0.0.0'
PORT = 9999