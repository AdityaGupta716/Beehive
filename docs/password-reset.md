# Password Reset Feature Documentation

## Overview

The password reset feature allows users to securely reset their passwords through an email-based reset link. This document outlines the implementation details, API endpoints, and frontend components involved.

## Architecture

### Backend Components

#### authroutes.py
Location: `routes/authroutes.py`

Contains Flask blueprint with the following endpoints:

- **POST /api/auth/request-password-reset**
  - Accepts email address
  - Generates secure reset token
  - Sets token expiry (1 hour)
  - Sends reset link via SMTP email
  - Returns generic response for security (doesn't reveal if email exists)

- **POST /api/auth/reset-password**
  - Accepts reset token, new password, and confirmation password
  - Validates token existence and expiry
  - Validates password requirements (min 8 characters)
  - Hashes new password using existing hash_password utility
  - Clears reset token after successful reset
  - Updates user in MongoDB

- **POST /api/auth/verify-reset-token**
  - Validates if a reset token is still valid
  - Checks token expiry
  - Returns validity status
  - Used by frontend before showing reset form

#### PasswordResetManager Class

Utility class for password reset operations:

- `generate_reset_token()`: Creates URL-safe random token (32 bytes)
- `send_reset_email()`: Sends HTML email with reset link using SMTP

### Frontend Components

#### PasswordReset.tsx
Location: `frontend/src/pages/auth/PasswordReset.tsx`

React component with multi-step flow:

1. **Request Step** - User enters email to request reset
   - Email validation
   - Loading state management
   - Error handling
   - Success message
   - Auto-redirect to signin after 3 seconds

2. **Reset Step** - User enters new password (only if token is valid)
   - Token verification on mount
   - Password input fields
   - Password confirmation validation
   - Minimum 8-character requirement
   - Error messages

3. **Success Step** - Confirmation display
   - Success checkmark icon
   - Message indicating password was reset
   - Auto-redirect to signin

## Security Features

1. **Token Security**
   - URL-safe random tokens (32 bytes)
   - Expiration set to 1 hour
   - Tokens stored in database (not in URL permanently)
   - Tokens cleared after successful reset

2. **Password Security**
   - Minimum 8-character requirement enforced
   - Passwords hashed using existing bcrypt utility
   - Password confirmation validation
   - No plain-text password storage

3. **Email Security**
   - SMTP with TLS encryption
   - Environment variables for credentials
   - Sender credentials not exposed in frontend

4. **Information Disclosure Prevention**
   - Generic response whether email exists or not
   - No indication of invalid tokens to prevent enumeration
   - Redirect to signin after operation

## API Usage

### Request Password Reset

```bash
POST /api/auth/request-password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}

Response (200):
{
  "message": "If an account exists, a reset link has been sent"
}
```

### Reset Password

```bash
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "<reset_token_from_email>",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}

Response (200):
{
  "message": "Password reset successfully"
}

Response (400):
{
  "error": "Invalid or expired reset token"
}
```

### Verify Reset Token

```bash
POST /api/auth/verify-reset-token
Content-Type: application/json

{
  "token": "<reset_token>"
}

Response (200):
{
  "valid": true
}
```

## Environment Configuration

Required environment variables in `.env` or `.env.local`:

```
# Backend
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000

# Frontend
VITE_API_URL=http://localhost:5000
```

## Integration Steps

1. **Add route to app router**
   - Import PasswordReset component
   - Add route `/reset-password` in App.tsx router configuration

2. **Update sign in component**
   - Add "Forgot password?" link pointing to `/reset-password`

3. **Email template**
   - Customize email template in `PasswordResetManager.send_reset_email()`
   - Update `FRONTEND_URL` to match production URL

4. **SMTP Configuration**
   - Set up email service (Gmail, SendGrid, etc.)
   - Generate app-specific password if using Gmail
   - Store credentials in environment variables

## Testing

### Backend Testing
```bash
# Test email request
curl -X POST http://localhost:5000/api/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Frontend Testing
1. Navigate to `/reset-password`
2. Test request flow with valid email
3. Test with reset token from database
4. Verify password validation
5. Test success redirect

## Error Handling

- Invalid token: User prompted to request new reset link
- Expired token: 1-hour expiration window
- Password mismatch: Clear error message
- Weak password: Minimum 8-character requirement enforced
- Email service down: Generic error message to user

## Database Schema Updates

User document now includes:
```javascript
{
  // existing fields...
  password_reset_token: String,
  password_reset_expiry: Date,
  updated_at: Date
}
```

## Future Enhancements

1. Resend reset email link
2. Track password reset attempts
3. Send email notification on successful reset
4. Support for multiple reset requests (invalidate previous tokens)
5. Rate limiting on reset requests
6. 2FA option during password reset
