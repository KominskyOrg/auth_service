# models.py

from app import db
import jwt
from datetime import datetime, timedelta
from flask import current_app

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    def generate_access_token(self):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(hour=12)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
