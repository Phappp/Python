import os
from flask import Blueprint, request, jsonify, session
import requests
from dotenv import load_dotenv
from app.extensions import mongo
from datetime import datetime
from bson import ObjectId

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

def get_next_session_name(username):
    sessions = list(mongo.db.chat_sessions.find({'username': username}).sort('created_at', 1))
    return f"Đoạn chat {len(sessions)+1}"

@chatbot_bp.route('/api/gemini_chat_sessions', methods=['GET'])
def get_gemini_chat_sessions():
    username = session.get('username')
    if not username:
        return jsonify({'sessions': []})
    sessions = list(mongo.db.chat_sessions.find({'username': username}).sort('created_at', 1))
    return jsonify({'sessions': [{'_id': str(s['_id']), 'name': s['name']} for s in sessions]})

@chatbot_bp.route('/api/gemini_chat_new', methods=['POST'])
def create_gemini_chat_session():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Chưa đăng nhập'}), 401
    sessions = list(mongo.db.chat_sessions.find({'username': username}).sort('created_at', 1))
    if len(sessions) >= 10:
        mongo.db.chat_sessions.delete_one({'_id': sessions[0]['_id']})
    name = get_next_session_name(username)
    session_doc = {
        'username': username,
        'name': name,
        'messages': [],
        'created_at': datetime.utcnow()
    }
    result = mongo.db.chat_sessions.insert_one(session_doc)
    return jsonify({'session_id': str(result.inserted_id)})

@chatbot_bp.route('/api/gemini_chat_save', methods=['POST'])
def save_gemini_chat_session():
    username = session.get('username')
    data = request.get_json()
    session_id = data.get('session_id')
    if not username or not session_id:
        return jsonify({'error': 'Thiếu thông tin'}), 400
    sessions = list(mongo.db.chat_sessions.find({'username': username}).sort('created_at', 1))
    if len(sessions) > 10:
        mongo.db.chat_sessions.delete_one({'_id': sessions[0]['_id']})
    return jsonify({'success': True})

@chatbot_bp.route('/api/gemini_chat', methods=['POST'])
def gemini_chat():
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id')
    if not message:
        return jsonify({'reply': 'Bạn chưa nhập câu hỏi.'})
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'reply': 'Chưa cấu hình API key Gemini.'})
    username = session.get('username')
    if not username:
        return jsonify({'reply': 'Bạn cần đăng nhập để sử dụng chatbot.'})
    try:
        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
            params={'key': api_key},
            json={
                'contents': [{
                    'parts': [{'text': message}]
                }]
            },
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            reply = data['candidates'][0]['content']['parts'][0]['text'] if data.get('candidates') else 'Không có phản hồi.'
            # Lưu vào session hiện tại
            if session_id:
                mongo.db.chat_sessions.update_one(
                    {'_id': ObjectId(session_id), 'username': username},
                    {'$push': {'messages': {'$each': [
                        {'role': 'user', 'text': message, 'timestamp': datetime.utcnow()},
                        {'role': 'bot', 'text': reply, 'timestamp': datetime.utcnow()}
                    ]}}}
                )
            else:
                # Nếu chưa có session, tạo mới
                name = get_next_session_name(username)
                session_doc = {
                    'username': username,
                    'name': name,
                    'messages': [
                        {'role': 'user', 'text': message, 'timestamp': datetime.utcnow()},
                        {'role': 'bot', 'text': reply, 'timestamp': datetime.utcnow()}
                    ],
                    'created_at': datetime.utcnow()
                }
                result = mongo.db.chat_sessions.insert_one(session_doc)
                session_id = str(result.inserted_id)
            return jsonify({'reply': reply, 'session_id': str(session_id)})
        else:
            return jsonify({'reply': 'Lỗi API Gemini: ' + response.text})
    except Exception as e:
        return jsonify({'reply': f'Lỗi: {e}'})

@chatbot_bp.route('/api/gemini_chat_history', methods=['GET'])
def get_gemini_chat_history():
    username = session.get('username')
    session_id = request.args.get('session_id')
    if not username:
        return jsonify({'messages': []})
    if session_id:
        chat_doc = mongo.db.chat_sessions.find_one({'_id': ObjectId(session_id), 'username': username})
        if chat_doc and 'messages' in chat_doc:
            messages = [
                {**msg, 'timestamp': msg['timestamp'].isoformat() if 'timestamp' in msg and msg['timestamp'] else ''}
                for msg in chat_doc['messages']
            ]
            return jsonify({'messages': messages})
    return jsonify({'messages': []})

@chatbot_bp.route('/api/gemini_chat_delete', methods=['POST'])
def delete_gemini_chat_session():
    username = session.get('username')
    data = request.get_json()
    session_id = data.get('session_id')
    if not username or not session_id:
        return jsonify({'error': 'Thiếu thông tin'}), 400
    mongo.db.chat_sessions.delete_one({'_id': ObjectId(session_id), 'username': username})
    return jsonify({'success': True})
