from flask import Flask
from .routes import main
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = "dev"

    app.register_blueprint(main)

    return app