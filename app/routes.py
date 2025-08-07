from flask import Blueprint, jsonify, request
from .db import mongo
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from services.embed import Embedder
from services.vector_db import VectorDB
from services.chatbot import Gemini

chatbot_api = Blueprint('chatbot_api', __name__)

load_dotenv()
#Model nhúng
model_name = os.getenv("EMMBEDDING_MODEL")

# Khởi tạo embedder, veector_db và chatbot
embedder = Embedder(model_name)
persist_path = os.getenv("PERSIST_PATH") 
vector_db = VectorDB(embedder.model, persist_path=persist_path)
gemini_chatbot = Gemini(vector_db.get_vectorstore())

@chatbot_api.route('/user', methods=['GET'])
def get_user():
    db = mongo['Chatbot'] 
    users = list(db.user.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify({
        "code": 200,
        "message": "Success",
        "data": users
    })

@chatbot_api.route('/user', methods=['POST'])
def login_user():
    db = mongo['Chatbot']
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({
            "code": 400,
            "message": "Missing username or password"
        }), 400

    user = db.user.find_one({"username": username, "password": password})
    if user:
        user['_id'] = str(user['_id'])
        return jsonify({
            "code": 200,
            "message": "Login successful",
            "data": {"username": user['username']}
        }), 200
    else:
        return jsonify({
            "code": 401,
            "message": "Invalid username or password"
        }), 401

@chatbot_api.route('/message', methods=['POST'])
def chat_message():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({
            "code": 400,
            "message": "Missing message"
        }), 400

    try:
        response = gemini_chatbot.chat(user_input)
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": {
                "response": response
            }
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error: {str(e)}"
        }), 500
