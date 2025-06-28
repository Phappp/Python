import os
from flask import Blueprint, request, jsonify, session
import requests
from dotenv import load_dotenv

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
            return jsonify({'reply': reply})
        else:
            return jsonify({'reply': 'Lỗi API Gemini: ' + response.text})
    except Exception as e:
        return jsonify({'reply': f'Lỗi: {e}'})
