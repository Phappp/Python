from flask import redirect, url_for, flash, session, request, current_app
from app.models.exercise_model import Exercise, Submission, TestCase
from app.forms import ProgrammingExerciseForm, CodeSubmissionForm, ManualFeedbackForm
import json
import subprocess
import tempfile
import os
import time
import psutil
from datetime import datetime
import requests

class ProgrammingExerciseController:
    
    @staticmethod
    def create_exercise(form):
        """
        Tạo bài tập lập trình mới
        """
        if form.validate_on_submit():
            try:
                # Parse test cases từ JSON
                test_cases = []
                if form.test_cases_json.data:
                    try:
                        test_cases_data = json.loads(form.test_cases_json.data)
                        for tc in test_cases_data:
                            test_cases.append({
                                'input': tc.get('input', ''),
                                'expected_output': tc.get('expected_output', ''),
                                'description': tc.get('description', ''),
                                'is_hidden': tc.get('is_hidden', False)
                            })
                    except json.JSONDecodeError:
                        flash('Định dạng JSON test cases không hợp lệ!', 'danger')
                        return None

                # Tạo bài tập
                exercise_id = Exercise.create(
                    title=form.title.data,
                    description=form.description.data,
                    language_supported=[form.language_supported.data],
                    test_cases=test_cases,
                    created_by=session.get('username'),
                    is_visible=form.is_visible.data,
                    time_limit=form.time_limit.data,
                    memory_limit=form.memory_limit.data
                )
                
                flash('Bài tập đã được tạo thành công!', 'success')
                return redirect(url_for('programming_exercise.manage_exercises'))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra: {e}', 'danger')
        return None

    @staticmethod
    def update_exercise(exercise_id, form):
        """
        Cập nhật bài tập
        """
        if form.validate_on_submit():
            try:
                # Parse test cases từ JSON
                test_cases = []
                if form.test_cases_json.data:
                    try:
                        test_cases_data = json.loads(form.test_cases_json.data)
                        for tc in test_cases_data:
                            test_cases.append({
                                'input': tc.get('input', ''),
                                'expected_output': tc.get('expected_output', ''),
                                'description': tc.get('description', ''),
                                'is_hidden': tc.get('is_hidden', False)
                            })
                    except json.JSONDecodeError:
                        flash('Định dạng JSON test cases không hợp lệ!', 'danger')
                        return None

                # Cập nhật bài tập
                Exercise.update(exercise_id, {
                    'title': form.title.data,
                    'description': form.description.data,
                    'language_supported': [form.language_supported.data],
                    'test_cases': test_cases,
                    'is_visible': form.is_visible.data,
                    'time_limit': form.time_limit.data,
                    'memory_limit': form.memory_limit.data
                })
                
                flash('Bài tập đã được cập nhật thành công!', 'success')
                return redirect(url_for('programming_exercise.manage_exercises'))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra: {e}', 'danger')
        return None

    @staticmethod
    def submit_code(exercise_id, form):
        """
        Nộp bài code và chấm điểm tự động
        """
        if form.validate_on_submit():
            try:
                # Tạo submission
                submission_id = Submission.create(
                    exercise_id=exercise_id,
                    user_id=session.get('username'),
                    code=form.code.data,
                    language=form.language.data
                )
                
                # Chạy test cases và chấm điểm
                score, llm_feedback, test_results = ProgrammingExerciseController._evaluate_submission(
                    exercise_id, form.code.data, form.language.data
                )
                
                # Cập nhật kết quả
                Submission.update_score(submission_id.inserted_id, score, llm_feedback, test_results)
                
                flash('Bài tập đã được nộp và chấm điểm thành công!', 'success')
                return redirect(url_for('programming_exercise.view_submission', submission_id=submission_id.inserted_id))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra: {e}', 'danger')
        return None

    @staticmethod
    def _evaluate_submission(exercise_id, code, language):
        """
        Đánh giá submission bằng test cases và AI
        """
        exercise = Exercise.find_by_id(exercise_id)
        if not exercise:
            return 0, "Bài tập không tồn tại", []
        
        test_cases = exercise.get('test_cases', [])
        total_tests = len(test_cases)
        passed_tests = 0
        test_results = []
        
        for i, test_case in enumerate(test_cases):
            try:
                # Chạy code với test case
                result = ProgrammingExerciseController._run_code(
                    code, language, test_case['input'], 
                    exercise.get('time_limit', 5), 
                    exercise.get('memory_limit', 128)
                )
                
                # So sánh kết quả
                expected = test_case['expected_output'].strip()
                actual = result['output'].strip()
                passed = expected == actual
                
                if passed:
                    passed_tests += 1
                
                test_results.append({
                    'test_case': i + 1,
                    'input': test_case['input'],
                    'expected': expected,
                    'actual': actual,
                    'passed': passed,
                    'execution_time': result.get('execution_time'),
                    'memory_used': result.get('memory_used'),
                    'error': result.get('error')
                })
                
            except Exception as e:
                test_results.append({
                    'test_case': i + 1,
                    'input': test_case['input'],
                    'expected': test_case['expected_output'],
                    'actual': 'ERROR',
                    'passed': False,
                    'error': str(e)
                })
        
        # Tính điểm dựa trên test cases (70%)
        test_score = (passed_tests / total_tests) * 7 if total_tests > 0 else 0
        
        # Phân tích code bằng AI (30%)
        ai_score, ai_feedback = ProgrammingExerciseController._analyze_code_with_ai(code, language, exercise)
        
        # Tổng điểm
        total_score = min(10, test_score + ai_score)
        
        return round(total_score, 1), ai_feedback, test_results

    @staticmethod
    def _run_code(code, language, input_data, time_limit, memory_limit):
        """
        Chạy code với input và giới hạn thời gian/bộ nhớ
        """
        # Nếu input_data rỗng và code có gọi input(), trả về cảnh báo thân thiện
        if (not input_data or input_data.strip() == "") and "input(" in code:
            return {
                'output': '',
                'error': 'Lưu ý: Bạn chưa thử nhập input',
                'execution_time': 0,
                'memory_used': 0
            }
        # Tạo file tạm với encoding utf-8
        with tempfile.NamedTemporaryFile(mode='w', suffix=ProgrammingExerciseController._get_file_extension(language), delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Chuẩn bị command để chạy code
            if language == 'python':
                cmd = ['python', temp_file]
            elif language == 'java':
                # Compile Java trước
                compile_cmd = ['javac', temp_file]
                subprocess.run(compile_cmd, capture_output=True, timeout=time_limit)
                # Chạy Java class
                class_name = os.path.basename(temp_file).replace('.java', '')
                cmd = ['java', '-cp', os.path.dirname(temp_file), class_name]
            elif language == 'cpp':
                # Compile C++
                output_file = temp_file.replace('.cpp', '.out')
                compile_cmd = ['g++', temp_file, '-o', output_file]
                subprocess.run(compile_cmd, capture_output=True, timeout=time_limit)
                cmd = [output_file]
            else:
                # Mặc định là Python
                cmd = ['python', temp_file]
            
            # Xử lý input data - chuyển đổi \n thành newline thực tế
            if input_data:
                processed_input = input_data.replace('\\n', '\n')
            else:
                processed_input = ''
            
            # Chạy code với input
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            try:
                stdout, stderr = process.communicate(input=processed_input, timeout=time_limit)
                execution_time = time.time() - start_time
                
                # Đảm bảo output/error luôn là UTF-8 hợp lệ
                if stdout is not None:
                    stdout = stdout.encode('utf-8', errors='replace').decode('utf-8')
                if stderr is not None:
                    stderr = stderr.encode('utf-8', errors='replace').decode('utf-8')
                
                # Lấy thông tin bộ nhớ
                memory_used = 0
                try:
                    process_info = psutil.Process(process.pid)
                    memory_used = process_info.memory_info().rss / 1024 / 1024  # MB
                except:
                    pass
                
                return {
                    'output': stdout,
                    'error': stderr if stderr else None,
                    'execution_time': round(execution_time, 3),
                    'memory_used': round(memory_used, 2)
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'output': '',
                    'error': f'Code chạy quá thời gian cho phép ({time_limit}s)',
                    'execution_time': time_limit,
                    'memory_used': 0
                }
            except Exception as e:
                try:
                    process.kill()
                except:
                    pass
                return {
                    'output': '',
                    'error': f'Lỗi khi chạy code: {str(e)}',
                    'execution_time': 0,
                    'memory_used': 0
                }
                
        except Exception as e:
            return {
                'output': '',
                'error': f'Lỗi khi chuẩn bị môi trường: {str(e)}',
                'execution_time': 0,
                'memory_used': 0
            }
        finally:
            try:
                os.unlink(temp_file)
                if language == 'cpp' and os.path.exists(temp_file.replace('.cpp', '.out')):
                    os.unlink(temp_file.replace('.cpp', '.out'))
            except:
                pass

    @staticmethod
    def _get_file_extension(language):
        """
        Lấy extension file cho ngôn ngữ
        """
        extensions = {
            'python': '.py',
            'java': '.java',
            'cpp': '.cpp',
            'javascript': '.js',
            'csharp': '.cs',
            'php': '.php',
            'ruby': '.rb',
            'go': '.go',
            'rust': '.rs',
            'swift': '.swift'
        }
        return extensions.get(language, '.py')

    @staticmethod
    def _analyze_code_with_ai(code, language, exercise):
        """
        Phân tích code bằng Gemini API (ngắn gọn, chỉ đánh giá, không chào hỏi, dùng \n)
        """
        GEMINI_API_KEY = "AIzaSyDwjDXqx20FqZszeoQ_KgOqvAwn2_o0yU4"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = (
            f"Chỉ trả về đánh giá ngắn gọn cho đoạn code sau (ngôn ngữ: {language}), không chào hỏi, không giải thích thêm.\n"
            f"{code}\n"
            "- Ghi rõ: 'Điểm mạnh: ...' (1 câu).\n"
            "- Ghi rõ: 'Cần cải thiện: ...' (1 câu, nếu có).\n"
            "- Đánh giá chất lượng code trên thang điểm 0-3 (ghi rõ: 'Điểm AI: x/3').\n"
            "- Xuống dòng bằng ký tự \n, không dùng <br>."
        )
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        try:
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
            if response.status_code == 200:
                result = response.json()
                # Lấy nội dung phản hồi
                feedback = result["candidates"][0]["content"]["parts"][0]["text"]
                # Tìm điểm AI trong phản hồi
                import re
                match = re.search(r"Điểm AI: (\d+(?:\.\d+)?)/3", feedback)
                ai_score = 1.5  # Mặc định nếu không tìm thấy
                if match:
                    ai_score = float(match.group(1))
                return ai_score, feedback
            else:
                return 1.5, f"[Gemini API lỗi {response.status_code}] {response.text}"
        except Exception as e:
            return 1.5, f"[Gemini API lỗi] {str(e)}"

    @staticmethod
    def add_manual_feedback(submission_id, form):
        """
        Thêm phản hồi thủ công của giảng viên
        """
        if form.validate_on_submit():
            try:
                submission = Submission.find_by_id(submission_id)
                if not submission:
                    flash('Không tìm thấy submission!', 'danger')
                    return None
                
                # Cập nhật phản hồi thủ công
                manual_feedback = form.manual_feedback.data
                score_adjustment = form.score_adjustment.data or 0
                
                # Tính điểm mới
                new_score = min(10, max(0, (submission.get('score', 0) or 0) + score_adjustment))
                
                # Cập nhật submission
                Submission.update_score(
                    submission_id, 
                    new_score, 
                    submission.get('llm_feedback', ''),
                    submission.get('test_results', [])
                )
                
                # Lưu phản hồi thủ công
                from app.extensions import mongo
                mongo.db.submissions.update_one(
                    {'_id': submission['_id']},
                    {'$set': {
                        'manual_feedback': manual_feedback,
                        'score_adjustment': score_adjustment,
                        'graded_by': session.get('username'),
                        'graded_at': datetime.utcnow()
                    }}
                )
                
                flash('Đã thêm phản hồi thủ công thành công!', 'success')
                return redirect(url_for('programming_exercise.view_submission', submission_id=submission_id))
            except Exception as e:
                flash(f'Đã có lỗi xảy ra: {e}', 'danger')
        return None 