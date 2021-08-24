import os
from utils import load_env

# loading environment variables from .env
load_env(os.path.join(os.path.dirname(__file__), '.env'))

ADMIN_ID = os.environ.get('ADMIN_ID')
API_TOKEN = os.environ.get('API_TOKEN')

"""
webhook settings:
WEBHOOK_HOST = 'https://your.domain'
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}
"""
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

"""
webserver settings
WEBAPP_HOST = '127.0.0.1'  # or ip
WEBAPP_PORT = 5000
"""
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = os.environ.get('PORT')
