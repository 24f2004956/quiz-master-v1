# import the required the modules 
from flask_sqlalchemy import SQLAlchemy

# for time_stamp_of_attempt in scores
from datetime import datetime

#initalise the database
db=SQLAlchemy()

#set the tables using classes

#user class
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String,  nullable=False)
    full_name = db.Column(db.String,  nullable=False)
    qualification = db.Column(db.String)
    DOB = db.Column(db.String)

    # relationship with score
    score = db.relationship('Score', backref='user')


#admin class
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


#subject class
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String, nullable=False)    
    description = db.Column(db.String, nullable=True)

    #relation with chapter
    chapter = db.relationship('Chapter', backref='subject')

#chapter class
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String, nullable=False)   
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False) 
    description = db.Column(db.Integer, nullable=True)

    #relation with quiz
    quiz = db.relationship('Quiz', backref='chapter')

#quiz class:
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False) 
    date_of_quiz = db.Column(db.String, nullable=False)
    time_duration = db.Column(db.String, nullable=False)
    remarks = db.Column(db.String, nullable=True)

    #relation with question
    question = db.relationship('Question', backref='quiz')

#class question
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False) 
    question_statement = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

#class score
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)




    
