from flask import Blueprint, render_template, request, jsonify
from app.utils.decorators import role_required
import subprocess
import tempfile
import os

code_practice_bp = Blueprint('code_practice', __name__)

@code_practice_bp.route('/practice-code', methods=['GET'])
@role_required('student')
def practice_code_page():
    return render_template('practice_code.html')

@code_practice_bp.route('/practice-code/run', methods=['POST'])
@role_required('student')
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    result = ''
    error = ''
    timeout = 5
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.py' if language=='python' else '.pl') as temp:
            temp.write(code)
            temp.flush()
            temp_name = temp.name
        if language == 'python':
            cmd = ['python', temp_name]
        elif language == 'perl':
            cmd = ['perl', temp_name]
        else:
            return jsonify({'output': '', 'error': 'Ngôn ngữ không hỗ trợ!'}), 400
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        result = completed.stdout
        error = completed.stderr
    except subprocess.TimeoutExpired:
        error = 'Chạy code quá thời gian cho phép!'
    except Exception as e:
        error = str(e)
    finally:
        if 'temp_name' in locals() and os.path.exists(temp_name):
            os.remove(temp_name)
    return jsonify({'output': result, 'error': error}) 