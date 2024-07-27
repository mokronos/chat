import sys
import os
from dotenv import load_dotenv

# load environment variables from .env file (use "make env" first to create
# the .env file with the secret key)
path = '~/code/logic'
path = os.path.expanduser(path)
load_dotenv(os.path.join(path, 'flask_site/.env'))

# import the application from the flask_site package
if path not in sys.path:
    sys.path.append(path)

from flask_site import create_app
application = create_app()


