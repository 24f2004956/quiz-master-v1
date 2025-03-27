from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from app.models.subject import Subject , Chapter
from app.models.quiz import Quiz
from app.models.user import User
from app.models.score import Score
from app.extensions import db
from app.utils.decorators import admin_required

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Helper function for JSON response
def api_response(data=None, message='Success', status=200, error=False):
    """
    Standardized API response format
    """
    response = {
        'success': not error,
        'message': message,
        'data': data or {}
    }
    return jsonify(response), status

# Subjects API
@api_bp.route('/subjects', methods=['GET'])
@login_required
def get_subjects():
    """
    Get all subjects or a specific subject
    Query params:
    - id (optional): specific subject ID
    """
    try:
        subject_id = request.args.get('id', type=int)
        
        if subject_id:
            subject = Subject.query.get_or_404(subject_id)
            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'total_chapters': len(subject.chapters)
            }
            return api_response(data=subject_data)
        
        subjects = Subject.query.all()
        subjects_data = [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'total_chapters': len(subject.chapters)
        } for subject in subjects]
        
        return api_response(data=subjects_data)
    
    except SQLAlchemyError as e:
        return api_response(
            message=f'Database error: {str(e)}', 
            status=500, 
            error=True
        )

# Chapters API
@api_bp.route('/chapters', methods=['GET'])
@login_required
def get_chapters():
    """
    Get chapters
    Query params:
    - subject_id (optional): filter chapters by subject
    - id (optional): get specific chapter
    """
    try:
        subject_id = request.args.get('subject_id', type=int)
        chapter_id = request.args.get('id', type=int)
        
        if chapter_id:
            chapter = Chapter.query.get_or_404(chapter_id)
            chapter_data = {
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'subject_id': chapter.subject_id,
                'subject_name': chapter.subject.name,
                'total_quizzes': len(chapter.quizzes)
            }
            return api_response(data=chapter_data)
        
        if subject_id:
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        else:
            chapters = Chapter.query.all()
        
        chapters_data = [{
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject_id,
            'subject_name': chapter.subject.name,
            'total_quizzes': len(chapter.quizzes)
        } for chapter in chapters]
        
        return api_response(data=chapters_data)
    
    except SQLAlchemyError as e:
        return api_response(
            message=f'Database error: {str(e)}', 
            status=500, 
            error=True
        )

# Quizzes API
@api_bp.route('/quizzes', methods=['GET'])
@login_required
def get_quizzes():
    """
    Get quizzes
    Query params:
    - chapter_id (optional): filter quizzes by chapter
    - user_id (optional): get user's attempted quizzes
    """
    try:
        chapter_id = request.args.get('chapter_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        # Base query
        query = Quiz.query
        
        # Apply filters if provided
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        quizzes = query.all()
        
        quiz_list = []
        for quiz in quizzes:
            quiz_data = {
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'chapter_name': quiz.chapter.name,
                'date_of_quiz': quiz.date_of_quiz,
                'time_duration': quiz.time_duration,
                'total_questions': len(quiz.questions)
            }
            
            # If user_id is provided, add user's score information
            if user_id:
                user_score = Score.query.filter_by(quiz_id=quiz.id, user_id=user_id).first()
                if user_score:
                    quiz_data['user_score'] = user_score.total_scored
                    quiz_data['score_timestamp'] = user_score.time_stamp_of_attempt.isoformat()
            
            quiz_list.append(quiz_data)
        
        return api_response(data=quiz_list)
    
    except SQLAlchemyError as e:
        return api_response(
            message=f'Database error: {str(e)}', 
            status=500, 
            error=True
        )

# Scores API
@api_bp.route('/scores', methods=['GET'])
@login_required
def get_scores():
    """
    Get scores
    Query params:
    - user_id (optional): get scores for a specific user
    - quiz_id (optional): get scores for a specific quiz
    """
    try:
        user_id = request.args.get('user_id', type=int)
        quiz_id = request.args.get('quiz_id', type=int)
        
        # Base query
        query = Score.query
        
        # Apply filters if provided
        if user_id:
            query = query.filter_by(user_id=user_id)
        if quiz_id:
            query = query.filter_by(quiz_id=quiz_id)
        
        scores = query.all()
        
        scores_data = [{
            'id': score.id,
            'quiz_id': score.quiz_id,
            'quiz_name': score.quiz.chapter.name,  # Using chapter name as quiz name
            'user_id': score.user_id,
            'user_name': score.user.full_name,
            'total_scored': score.total_scored,
            'timestamp': score.time_stamp_of_attempt.isoformat()
        } for score in scores]
        
        return api_response(data=scores_data)
    
    except SQLAlchemyError as e:
        return api_response(
            message=f'Database error: {str(e)}', 
            status=500, 
            error=True
        )

# Admin-only API for user management
@api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """
    Get all users (admin-only)
    Query params:
    - role (optional): filter users by role
    """
    try:
        role = request.args.get('role')
        
        if role:
            users = User.query.filter_by(role=role).all()
        else:
            users = User.query.all()
        
        users_data = [{
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'total_quizzes_attempted': len(user.scores)
        } for user in users]
        
        return api_response(data=users_data)
    
    except SQLAlchemyError as e:
        return api_response(
            message=f'Database error: {str(e)}', 
            status=500, 
            error=True
        )