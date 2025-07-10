from flask import Blueprint, render_template, request

quiz_page_bp = Blueprint('quiz_page', __name__)

@quiz_page_bp.route('/quiz/create_quiz')
def create_quiz_page():
    return render_template('quiz/create_quiz.html')

@quiz_page_bp.route('/quiz/list_quiz')
def list_quiz_page():
    return render_template('quiz/list_quiz.html')

@quiz_page_bp.route('/quiz/do')
def do_quiz_page():
    return render_template('quiz/do_quiz.html')

@quiz_page_bp.route('/quiz/quiz_results')
def quiz_results_page():
    return render_template('quiz/quiz_results.html')

@quiz_page_bp.route('/quiz/my_quiz_result')
def my_quiz_result_page():
    return render_template('quiz/my_quiz_result.html') 