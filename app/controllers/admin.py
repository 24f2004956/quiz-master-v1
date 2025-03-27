from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.subject import Subject, Chapter
from app.models.quiz import Quiz, Question
from app.models.user import User
from app.models.score import Score
from app.utils.decorators import admin_required

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import io
import base64

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', 
                           subjects=subjects, 
                           chapters=chapters, 
                           quizzes=quizzes, 
                           users=users)

# Subject management
@admin_bp.route('/subject/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')

        if Subject.query.filter_by(name=name).first():
            flash('Subject already exists!', 'danger')
            return redirect(url_for('admin.dashboard'))

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_subject.html')

@admin_bp.route('/subject/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_subject.html', subject=subject)

@admin_bp.route('/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

# Chapter management
@admin_bp.route('/chapter/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_chapter():
    subjects = Subject.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        subject_id = request.form.get('subject_id')
        
        # ✅ Validation checks
        if not name or not description or not subject_id:
            flash("All fields are required, including selecting a subject.", "danger")
            return redirect(url_for('admin.add_chapter'))  # Prevent processing incomplete form

        # Check if subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Invalid subject selected!", "danger")
            return redirect(url_for('admin.add_chapter'))

        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter added successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_chapter.html', subjects=subjects)

@admin_bp.route('/chapter/edit/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subjects = Subject.query.all()

    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        chapter.subject_id = request.form['subject_id']
        db.session.commit()
        flash("Chapter updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_chapter.html', chapter=chapter, subjects=subjects)

@admin_bp.route('/chapter/delete/<int:chapter_id>', methods=['POST'])
@login_required
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))

# Quiz management
@admin_bp.route('/quiz/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_quiz():
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']

        new_quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration)
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    chapters = Chapter.query.all()
    return render_template('admin/add_quiz.html', chapters=chapters)

@admin_bp.route('/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        quiz.chapter_id = request.form['chapter_id']
        quiz.date_of_quiz = request.form['date_of_quiz']
        quiz.time_duration = request.form['time_duration']
        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_quiz.html', quiz=quiz, chapters=chapters, questions=questions)

@admin_bp.route('/quiz/delete/<int:quiz_id>', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))

# Question management
@admin_bp.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']

        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=int(correct_option)
        )

        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))

    return render_template('admin/add_question.html', quiz=quiz)

@admin_bp.route('/question/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = int(request.form['correct_option'])
        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('admin.edit_quiz', quiz_id=question.quiz_id))

    return render_template('admin/edit_question.html', question=question)

@admin_bp.route('/question/delete/<int:question_id>', methods=['GET','POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))

# ✅ Route to Edit User
@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.qualification = request.form['qualification']
        user.role = request.form.get('role','user')
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))  # Redirect to admin dashboard

    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent deletion of admin
    if user.role == 'admin':
        flash("Admin cannot be deleted!", "danger")
        return redirect(url_for('admin.dashboard'))

    try:
        # Delete all scores associated with the user
        Score.query.filter_by(user_id=user.id).delete()

        # Delete user after scores are removed
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")

    return redirect(url_for('admin.dashboard'))


# charts and Admin summary
@admin_bp.route('/admin_summary')
@login_required
@admin_required
def admin_summary():
    # Get all subjects
    subjects = Subject.query.all()
    subject_names = [subject.name for subject in subjects]
    
    # Calculate top scores by subject
    top_scores = []
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        subject_top_score = 0
        
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            for quiz in quizzes:
                scores = Score.query.filter_by(quiz_id=quiz.id).all()
                if scores:
                    quiz_top_score = max([score.total_scored for score in scores])
                    if quiz_top_score > subject_top_score:
                        subject_top_score = quiz_top_score
        
        top_scores.append(subject_top_score)
    
    # Create subject-wise top scores bar chart
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(subject_names, top_scores, color='lightgreen')
    ax1.set_xlabel('Subjects')
    ax1.set_ylabel('Top Score')
    ax1.set_title('Subject-wise Top Scores')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Convert plot to base64 image
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    top_scores_chart = base64.b64encode(img1.getvalue()).decode()
    plt.close(fig1)
    
    # Calculate attempts by subject
    subject_attempts = []
    for subject in subjects:
        attempts = 0
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            for quiz in quizzes:
                quiz_attempts = Score.query.filter_by(quiz_id=quiz.id).count()
                attempts += quiz_attempts
        
        subject_attempts.append(attempts)
    
    # Create subject-wise attempts pie chart
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.pie(subject_attempts, labels=subject_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
    ax2.set_title('Subject-wise User Attempts')
    plt.tight_layout()
    
    # Convert plot to base64 image
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    attempts_chart = base64.b64encode(img2.getvalue()).decode()
    plt.close(fig2)
    
    # Prepare overall quiz statistics
    quiz_stats = []
    for subject in subjects:
        quiz_count = 0
        attempt_count = 0
        total_score = 0
        score_count = 0
        
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            quiz_count += len(quizzes)
            
            for quiz in quizzes:
                scores = Score.query.filter_by(quiz_id=quiz.id).all()
                attempt_count += len(scores)
                
                for score in scores:
                    total_score += score.total_scored
                    score_count += 1
        
        avg_score = total_score / score_count if score_count > 0 else 0
        
        quiz_stats.append({
            'subject_name': subject.name,
            'quiz_count': quiz_count,
            'attempt_count': attempt_count,
            'avg_score': avg_score
        })
    
    return render_template('admin/admin_summary.html', 
                          top_scores_chart=top_scores_chart, 
                          attempts_chart=attempts_chart, 
                          quiz_stats=quiz_stats)
