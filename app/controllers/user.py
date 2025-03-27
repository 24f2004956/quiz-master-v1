from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models.quiz import Quiz
from app.models.score import Score
from app.models.subject import Subject , Chapter



import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import io
import base64

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def home():
    return render_template('index.html')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    quizzes = Quiz.query.all()
    return render_template('user/dashboard.html', quizzes=quizzes)

@user_bp.route('/summary')
@login_required
def summary():
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_summary'))
    else:
        return redirect(url_for('user.user_summary'))

@user_bp.route('/user_summary')
@login_required
def user_summary():
    # Get user's quiz scores
    user_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp_of_attempt.desc()).all()
    
    # Get quizzes by subject
    subject_data = {}
    for score in user_scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        if subject.name in subject_data:
            subject_data[subject.name] += 1
        else:
            subject_data[subject.name] = 1
    
    # Create subject-wise bar chart
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    subjects = list(subject_data.keys())
    counts = list(subject_data.values())
    ax1.bar(subjects, counts, color='skyblue')
    ax1.set_xlabel('Subjects')
    ax1.set_ylabel('Number of Quizzes')
    ax1.set_title('Subject-wise Quiz Participation')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Convert plot to base64 image
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    subject_chart = base64.b64encode(img1.getvalue()).decode()
    plt.close(fig1)
    
    # Get quizzes by month
    month_data = {}
    for score in user_scores:
        month = score.time_stamp_of_attempt.strftime('%B %Y')
        if month in month_data:
            month_data[month] += 1
        else:
            month_data[month] = 1
    
    # Create month-wise pie chart
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    months = list(month_data.keys())
    counts = list(month_data.values())
    ax2.pie(counts, labels=months, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax2.set_title('Monthly Quiz Activity')
    plt.tight_layout()
    
    # Convert plot to base64 image
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    monthly_chart = base64.b64encode(img2.getvalue()).decode()
    plt.close(fig2)
    
    return render_template('user/user_summary.html', 
                          subject_chart=subject_chart, 
                          monthly_chart=monthly_chart, 
                          user_scores=user_scores)