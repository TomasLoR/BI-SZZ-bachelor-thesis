from flask import Flask
import os

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
    
    def get_app(self):
        return self.app