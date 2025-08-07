from flask import Flask
from .config import Config
from .db import init_db
from dotenv import load_dotenv
from flask_cors import CORS

def create_app():
    load_dotenv()  # Load biến môi trường từ file .env
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    init_db()  # Khởi tạo kết nối MongoDB

    from .routes import chatbot_api
    app.register_blueprint(chatbot_api, url_prefix="/chatbot_api")
    return app