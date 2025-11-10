
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ituriu-electricals-secret-key-2024'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'ituriu-jwt-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ituriu_electricals.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
