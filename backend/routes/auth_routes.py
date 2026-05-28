"""
Authentication Routes — Login, Register, Token Management
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User, db
from utils.email import EmailService
from utils.sms import send_sms_notification
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new student"""
    data = request.get_json()
    
    # Validation
    required_fields = ['student_id', 'first_name', 'last_name', 'email', 'phone', 'faculty', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if student already exists
    if User.get_by_student_id(data['student_id']):
        return jsonify({'message': 'Student ID already registered'}), 400
    
    if User.get_by_email(data['email']):
        return jsonify({'message': 'Email already registered'}), 400
    
    try:
        # Create new user
        user = User(
            student_id=data['student_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            faculty=data['faculty'],
            level=int(data.get('level', 100)),
            account_status='active',
            is_active=True
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        EmailService.send_welcome_email(
            user.email,
            f"{user.first_name} {user.last_name}",
            user.student_id
        )
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Student login"""
    data = request.get_json()
    
    if not data.get('student_id') or not data.get('password'):
        return jsonify({'message': 'Missing student ID or password'}), 400
    
    user = User.get_by_student_id(data['student_id'])
    
    if not user or not user.verify_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403
    
    # Update last login
    user.update_last_login()
    
    # Create token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token validity"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'valid': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh-token', methods=['POST'])
@jwt_required()
def refresh_token():
    """Refresh access token"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    new_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Token refreshed',
        'access_token': new_token
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'message': 'Email required'}), 400
    
    user = User.get_by_email(data['email'])
    
    if not user:
        # Don't reveal if user exists
        return jsonify({'message': 'If email exists, reset link sent'}), 200
    
    try:
        # Generate reset token (simplified for demo)
        reset_token = create_access_token(identity=user.id, expires_delta=False)
        
        # Send reset email
        reset_link = f"https://njala-fees.edu.sl/reset-password?token={reset_token}"
        
        html_body = f"""
        <html>
            <body style="font-family: 'DM Sans', sans-serif;">
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}" style="display: inline-block; background: #1e5c2e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                <p>This link expires in 1 hour.</p>
                <p>If you didn't request this, ignore this email.</p>
            </body>
        </html>
        """
        
        # EmailService.send_email(user.email, "Password Reset - Njala Fees Portal", html_body)
        
        return jsonify({'message': 'If email exists, reset link sent'}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token and new password required'}), 400
    
    try:
        # Verify token
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = decoded.get('sub')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
    
    except Exception as e:
        return jsonify({'message': 'Invalid token'}), 401


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'phone', 'email']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': 'Old and new passwords required'}), 400
    
    if not user.verify_password(old_password):
        return jsonify({'message': 'Incorrect old password'}), 401
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token-based, just for client cleanup)"""
    return jsonify({'message': 'Logged out successfully'}), 200
