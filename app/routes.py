from flask import Blueprint, jsonify, request
from .db import mongo
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from services.embed import Embedder
from services.vector_db import VectorDB
from services.chatbot import Gemini
import base64

chatbot_api = Blueprint('chatbot_api', __name__)

load_dotenv()
# Model nhúng
model_name = os.getenv("EMMBEDDING_MODEL")

# Khởi tạo embedder, vector_db và chatbot
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
    files = data.get("files", [])

    if not user_input and not files:
        return jsonify({
            "code": 400,
            "message": "Missing message or files"
        }), 400

    # Sử dụng hàm extract_file_contents của Gemini
    file_contents = gemini_chatbot.extract_file_contents(files, embedder, vector_db)

    if file_contents:
        user_input = (user_input or "") + "\n\nNội dung file:\n" + "\n\n".join(file_contents)
    print(file_contents)
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

@chatbot_api.route('/embedfile', methods=['POST'])
def embed_file():
    """
    Nhận file từ client, lưu vào data/documents và nhúng vào vector store.
    """
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "message": "Missing file"
        }), 400

    file = request.files['file']
    filename = file.filename
    save_path = os.path.join("data", "documents", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    # Đọc lại file vừa lưu và encode sang base64 để truyền cho hàm nhúng
    with open(save_path, "rb") as f:
        file_bytes = f.read()
        encoded_content = "data:application/octet-stream;base64," + base64.b64encode(file_bytes).decode()

    file_info = {
        "name": filename,
        "content": encoded_content
    }

    # Nhúng file và reload vector store
    gemini_chatbot.embed_and_reload_files([file_info], embedder, vector_db)

    return jsonify({
        "code": 200,
        "message": "File embedded and vector store updated",
        "data": {"filename": filename}
    }), 200