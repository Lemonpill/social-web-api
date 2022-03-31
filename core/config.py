class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "YOURSECRETKEY"
    DEBUG = True