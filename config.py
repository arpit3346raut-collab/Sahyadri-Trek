import os

def get_mail_port():
    try:
        return int(os.environ.get('MAIL_PORT') or 587)
    except ValueError:
        return 587


class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB configuration
    MONGO_URI = 'mongodb://arpit3346raut:ERwbAZzPpDfGRMHe@ac-lb69q9d-shard-00-00.kcdiq0q.mongodb.net:27017,ac-lb69q9d-shard-00-01.kcdiq0q.mongodb.net:27017,ac-lb69q9d-shard-00-02.kcdiq0q.mongodb.net:27017/?ssl=true&replicaSet=atlas-1204ly-shard-0&authSource=admin&appName=arpit3346raut'
    
    # Mail configuration (for sending trek passes)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = get_mail_port()
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@sahyadri-trek.gov.in'
    
    # Session configuration
    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = None  # Will be set in app.py
    SESSION_MONGODB_DB = 'sahyadri_trek'
    SESSION_COLLECTION = 'sessions'
    
    # Upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
