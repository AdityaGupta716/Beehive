"""Password reset utility functions for handling password reset operations."""

from datetime import datetime, timedelta
from database import databaseConfig
import secrets
import bcrypt

beehive_user_collection = databaseConfig.get_beehive_user_collection()

def generate_reset_token():
    """
    Generate a secure reset token for password reset.
    """
    return secrets.token_urlsafe(32)

def create_password_reset_request(user_id, email):
    """
    Create a password reset request for a user.
    Returns the reset token.
    """
    try:
        reset_token = generate_reset_token()
        reset_expires = datetime.now() + timedelta(hours=1)
        
        beehive_user_collection.update_one(
            {'_id': user_id},
            {'$set': {
                'password_reset_token': reset_token,
                'password_reset_expires': reset_expires,
                'reset_request_time': datetime.now()
            }}
        )
        
        return reset_token
    except Exception as e:
        print(f"Error creating password reset request: {str(e)}")
        return None

def verify_reset_token(token):
    """
    Verify if a reset token is valid and not expired.
    Returns the user if valid, None otherwise.
    """
    try:
        user = beehive_user_collection.find_one({
            'password_reset_token': token,
            'password_reset_expires': {'$gt': datetime.now()}
        })
        return user
    except Exception as e:
        print(f"Error verifying reset token: {str(e)}")
        return None

def reset_user_password(user_id, new_password):
    """
    Reset the user's password and clear the reset token.
    """
    try:
        # Validate password strength
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password and clear reset fields
        result = beehive_user_collection.update_one(
            {'_id': user_id},
            {'$set': {
                'password': hashed_password,
                'password_reset_token': None,
                'password_reset_expires': None,
                'password_changed_at': datetime.now()
            }}
        )
        
        return result.modified_count > 0, "Password reset successfully"
    except Exception as e:
        return False, f"Error resetting password: {str(e)}"

def clear_expired_reset_tokens():
    """
    Clear all expired password reset tokens.
    """
    try:
        result = beehive_user_collection.update_many(
            {'password_reset_expires': {'$lt': datetime.now()}},
            {'$set': {
                'password_reset_token': None,
                'password_reset_expires': None
            }}
        )
        return result.modified_count
    except Exception as e:
        print(f"Error clearing expired tokens: {str(e)}")
        return 0

def get_user_by_email(email):
    """
    Get user by email address.
    """
    try:
        user = beehive_user_collection.find_one({'email': email})
        return user
    except Exception as e:
        print(f"Error getting user by email: {str(e)}")
        return None

def has_active_reset_request(user_id):
    """
    Check if user has an active reset request.
    """
    try:
        user = beehive_user_collection.find_one({
            '_id': user_id,
            'password_reset_token': {'$ne': None},
            'password_reset_expires': {'$gt': datetime.now()}
        })
        return user is not None
    except Exception as e:
        print(f"Error checking active reset request: {str(e)}")
        return False
