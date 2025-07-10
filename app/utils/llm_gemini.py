import requests
import re
import json

def generate_quiz_questions(content, difficulty, num_questions=5):
    """
    Gọi API Gemini 2.0 Flash để sinh danh sách câu hỏi trắc nghiệm từ nội dung và mức độ khó.
    Trả về list các dict: {question_text, options, correct_answer, explanation}
    """
    # TODO: Thay thế API_KEY và endpoint thật
    API_KEY = 'AIzaSyDxgIidcVd_PVlt43ij238cGW99ug_vdD8'
    ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + API_KEY
    prompt = f"""
    Sinh {num_questions} câu hỏi trắc nghiệm ôn tập liên quan đến chủ đề ngôn ngữ lập trình PERL hoặc PYTHON (tùy theo nội dung bên dưới), với mức độ {difficulty}.
    Nội dung bài học:
    {content}
    Định dạng trả về JSON:
    [
      {{'question_text': ..., 'options': [...], 'correct_answer': ..., 'explanation': ...}},
      ...
    ]
    """
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(ENDPOINT, json=data)
    print('Gemini raw response:', response.text)  # Thêm log để debug
    if response.status_code == 200:
        try:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            # Tìm block ```json ... ```
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
            questions = json.loads(text)
            return questions
        except Exception as e:
            print('Gemini parse error:', e)
            return []
    else:
        print('Gemini API error:', response.text)
        return [] 