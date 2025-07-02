import os
from flask import Blueprint, request, jsonify, session
import requests
from dotenv import load_dotenv
from app.extensions import mongo
from datetime import datetime

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/api/gemini_chat', methods=['POST'])
def gemini_chat():
    data = request.get_json()
    message = data.get('message', '')
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
            # Lưu lịch sử chat vào MongoDB
            chat_doc = mongo.db.chat_histories.find_one({'username': username})
            msg_user = {'role': 'user', 'text': message, 'timestamp': datetime.utcnow()}
            msg_bot = {'role': 'bot', 'text': reply, 'timestamp': datetime.utcnow()}
            if chat_doc:
                mongo.db.chat_histories.update_one(
                    {'username': username},
                    {'$push': {'messages': {'$each': [msg_user, msg_bot]}}}
                )
            else:
                mongo.db.chat_histories.insert_one({
                    'username': username,
                    'messages': [msg_user, msg_bot]
                })
            return jsonify({'reply': reply})
        else:
            return jsonify({'reply': 'Lỗi API Gemini: ' + response.text})
    except Exception as e:
        return jsonify({'reply': f'Lỗi: {e}'})

# API lấy lịch sử chat cho user hiện tại
@chatbot_bp.route('/api/gemini_chat_history', methods=['GET'])
def get_gemini_chat_history():
    username = session.get('username')
    if not username:
        return jsonify({'messages': []})
    chat_doc = mongo.db.chat_histories.find_one({'username': username})
    if chat_doc and 'messages' in chat_doc:
        # Chuyển timestamp về string để frontend dễ xử lý
        messages = [
            {**msg, 'timestamp': msg['timestamp'].isoformat() if 'timestamp' in msg and msg['timestamp'] else ''}
            for msg in chat_doc['messages']
        ]
        return jsonify({'messages': messages})
    return jsonify({'messages': []})
