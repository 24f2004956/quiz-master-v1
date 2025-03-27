from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.quiz import Quiz, Question
from app.models.subject import Chapter
from app.models.score import Score
from sqlalchemy.orm import joinedload

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/<int:quiz_id>/attempt', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f"q{question.id}")
            if user_answer and int(user_answer) == question.correct_option:
                score += 1
        
        new_score = Score(quiz_id=quiz_id, user_id=current_user.id, total_scored=score)
        db.session.add(new_score)
        db.session.commit()
        
        flash(f'Quiz submitted! Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/attempt_quiz.html', quiz=quiz, questions=questions)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    score = 0
    for question in questions:
        selected_option = request.form.get(f'question_{question.id}')
        if selected_option and int(selected_option) == question.correct_option:
            score += 1

    # Save score in the database
    new_score = Score(quiz_id=quiz_id, user_id=current_user.id, total_scored=score)
    db.session.add(new_score)
    db.session.commit()

    flash(f'You scored {score}/{len(questions)}', 'success')
    return redirect(url_for('user.dashboard'))

@quiz_bp.route('/view_quiz/<int:quiz_id>', methods=['GET'])
@login_required
def view_quiz(quiz_id):
        quiz = Quiz.query.options(
        db.joinedload(Quiz.chapter),
        db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
        db.joinedload(Quiz.questions)
        ).get_or_404(quiz_id)
        return render_template('user/view_quiz.html' , quiz=quiz)