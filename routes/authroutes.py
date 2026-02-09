from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import secrets
from datetime import datetime, timedelta
from database.Database import Database
from usersutils.hash_password import hash_password, check_password
import hashlib
import smtplib
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

db = Database()

class PasswordResetManager:
    """Manages password reset tokens and operations"""
    
    @staticmethod
    def generate_reset_token():
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def send_reset_email(email, reset_token, reset_link):
        """Send password reset email"""
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            
            if not all([sender_email, sender_password]):
                return False, "Email credentials not configured"
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = 'Password Reset Request - Beehive'
            
            body = f"""
            Hello,
            
            You requested a password reset. Click the link below to reset your password:
            {reset_link}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            Beehive Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            return True, "Reset email sent successfully"
        except Exception as e:
            print(f"Error sending reset email: {e}") # Replace with proper logging
            return False, "An error occurred while sending the email."


@auth_bp.route('/request-password-reset', methods=['POST'])
@cross_origin()
def request_password_reset():
    """Request password reset endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find user by email
        user_collection = db.get_collection('users')
        user = user_collection.find_one({'email': email})
        
        if not user:
            # Return success even if user doesn't exist (security best practice)
            return jsonify({
                'message': 'If an account exists, a reset link has been sent'
            }), 200
        
        # Generate reset token
        reset_token = PasswordResetManager.generate_reset_token()
        reset_expiry = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token in database
        # Store hashed reset token in database
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()
        user_collection.update_one(
            {'email': email},
            {'$set': {
                'password_reset_token': hashed_token,
                'password_reset_expiry': reset_expiry
            }}
        )
        
        # Generate reset link
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{base_url}/reset-password?token={reset_token}"
        
        # Send email
        success, message = PasswordResetManager.send_reset_email(email, reset_token, reset_link)
        
        if not success:
            return jsonify({'error': f'Failed to send email: {message}'}), 500
        
        return jsonify({
            'message': 'If an account exists, a reset link has been sent'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
@cross_origin()
def reset_password():
    """Reset password endpoint"""
    try:
        data = request.get_json()
        reset_token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([reset_token, new_password, confirm_password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Find user by reset token
        # Find user by hashed reset token
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()
        user_collection = db.get_collection('users')
        user = user_collection.find_one({
            'password_reset_token': hashed_token,
            'password_reset_expiry': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update password and clear reset token
        user_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password': hashed_password,
                'password_reset_token': None,
                'password_reset_expiry': None,
                'updated_at': datetime.utcnow()
            }}
        )
        
        return jsonify({
            'message': 'Password reset successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/verify-reset-token', methods=['POST'])
@cross_origin()
def verify_reset_token():
    """Verify if a reset token is valid"""
    try:
        data = request.get_json()
        reset_token = data.get('token')
        
        if not reset_token:
            return jsonify({'error': 'Token is required'}), 400

            hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()
        
        user_collection = db.get_collection('users')
        user = user_collection.find_one({
            'password_reset_token': hashed_token,
            'password_reset_expiry': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return jsonify({'valid': False}), 200
        
        return jsonify({'valid': True}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
