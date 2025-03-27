from flask import Flask
from app.extensions import db, login_manager
from app.controllers.api import api_bp


def create_app(config_object='app.config.DevelopmentConfig'):

    # Application factory for creating Flask instances
    app = Flask(__name__)

     # Load configuration
    app.config.from_object(config_object)   
    
    # Initialize extensions
   
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

 

  
    
    #  Import and Register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.admin import admin_bp
    from app.controllers.quiz import quiz_bp
    from app.controllers.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)  # Register the API blueprint
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Initialize admin user
        from app.utils.init_db import initialize_admin
        initialize_admin()
    
    return app