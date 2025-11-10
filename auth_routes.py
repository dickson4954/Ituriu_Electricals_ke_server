
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_
from models import db, User  # Import db from models

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        full_name = data.get("full_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not all([full_name, username, email, password]):
            return jsonify({"message": "All fields are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400

        new_user = User(
            full_name=full_name, 
            username=username, 
            email=email,
            is_admin=False
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        token = create_access_token(identity=new_user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": new_user.id,
                "full_name": new_user.full_name,
                "username": new_user.username,
                "email": new_user.email,
                "is_admin": new_user.is_admin
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Registration failed", "error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username_or_email = data.get("username")
        password = data.get("password")

        if not username_or_email or not password:
            return jsonify({"message": "Username/email and password are required"}), 400

        user = User.query.filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            # ONLY ALLOW ADMIN USERS TO LOGIN
            if not user.is_admin:
                return jsonify({
                    "message": "Access denied. Admin privileges required."
                }), 403
            
            token = create_access_token(identity=user.id)
            
            return jsonify({
                "message": "Admin login successful",
                "token": token,
                "is_admin": user.is_admin,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin
                }
            }), 200

        return jsonify({"message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 500

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        return jsonify({
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Failed to get user data", "error": str(e)}), 500

# Special endpoint to create admin user (for initial setup)
@auth_bp.route("/create-admin", methods=["POST"])
def create_admin():
    try:
        data = request.get_json()
        full_name = data.get("full_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not all([full_name, username, email, password]):
            return jsonify({"message": "All fields are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400

        # Create admin user
        admin_user = User(
            full_name=full_name, 
            username=username, 
            email=email,
            is_admin=True
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()

        return jsonify({
            "message": "Admin user created successfully",
            "user": {
                "id": admin_user.id,
                "full_name": admin_user.full_name,
                "username": admin_user.username,
                "email": admin_user.email,
                "is_admin": admin_user.is_admin
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Admin creation failed", "error": str(e)}), 500
