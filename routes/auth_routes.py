from flask import Blueprint, request, jsonify
from database import databaseConfig
from datetime import datetime, timedelta
import uuid
import secrets
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

auth_bp = Blueprint('auth', __name__)

# Get the user collection from MongoDB
beehive_user_collection = databaseConfig.get_beehive_user_collection()

def send_password_reset_email(email, reset_token):
    """
    Send a password reset email to the user with a reset link.
    """
    try:
        reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={reset_token}"
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SENDER_EMAIL')
        msg['To'] = email
        msg['Subject'] = 'Password Reset Request'
        
        body = f"""
        Hello,
        
        We received a request to reset your password. Click the link below to reset it:
        
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        Beehive Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Uncomment below to send actual emails
        # server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587)))
        # server.starttls()
        # server.login(os.getenv('SENDER_EMAIL'), os.getenv('SENDER_PASSWORD'))
        # server.send_message(msg)
        # server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiate password reset by creating a reset token.
    """
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find user by email
        user = beehive_user_collection.find_one({'email': email})
        
        if not user:
            # Return success even if user not found (security best practice)
            return jsonify({'message': 'If email exists, reset link will be sent'}), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.now() + timedelta(hours=1)
        
        # Store token in database
        beehive_user_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password_reset_token': reset_token,
                'password_reset_expires': reset_expires
            }}
        )
        
        # Send email with reset link
        send_password_reset_email(email, reset_token)
        
        return jsonify({'message': 'If email exists, reset link will be sent'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """
    Verify that the reset token is valid.
    """
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Find user with this token
        user = beehive_user_collection.find_one({
            'password_reset_token': token,
            'password_reset_expires': {'$gt': datetime.now()}
        })
        
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return jsonify({'message': 'Token is valid', 'email': user.get('email')}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """
    Reset user password with a valid token.
    """
    try:
        data = request.json
        token = data.get('token')
        new_password = data.get('password')
        confirm_password = data.get('confirmPassword')
        
        if not token or not new_password or not confirm_password:
            return jsonify({'error': 'Token and passwords are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Find and verify user
        user = beehive_user_collection.find_one({
            'password_reset_token': token,
            'password_reset_expires': {'$gt': datetime.now()}
        })
        
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Hash the new password
        import bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update user password and clear reset token
        beehive_user_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password': hashed_password,
                'password_reset_token': None,
                'password_reset_expires': None
            }}
        )
        
        return jsonify({'message': 'Password reset successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
