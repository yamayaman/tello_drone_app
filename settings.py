import os

from flask import Flask

SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 5000
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(PROJECT_ROOT, 'templates')
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
DEBUG_MODE = True

app = Flask(__name__, template_folder=TEMPLATES, static_folder=STATIC_FOLDER)

if DEBUG_MODE:
    app.debug = True