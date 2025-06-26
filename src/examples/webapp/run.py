# run.py
from .src.app import FlaskApp
from .src.router import Router
from .src.services import Services
from .src.database import Database
from .src.api.api_router import APIRouter
from .src.api.api_services import APIServices

if __name__ == '__main__':
    flask_app = FlaskApp()
    app = flask_app.get_app()
    
    services = Services()
    api_services = APIServices()
    
    Router(app, services)
    APIRouter(app, api_services)
    
    app.run(host='0.0.0.0', port=5000, debug=True)