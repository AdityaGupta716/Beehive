# Password Reset Feature Implementation (Issue #482)

## Overview
This PR implements a complete "Forget Password" feature for the Beehive application, allowing users to reset their password securely.

## Changes Made

### Backend Changes

#### 1. New File: `routes/auth_routes.py`
Implements three new API endpoints for password reset functionality:

- **POST `/api/auth/forgot-password`**
  - Initiates password reset process
  - Accepts: `{ "email": "user@example.com" }`
  - Generates secure reset token and stores in database
  - Sends reset email to user (currently disabled by default)
  - Returns success message regardless of email existence (security best practice)

- **POST `/api/auth/verify-reset-token`**
  - Verifies that reset token is valid and not expired
  - Accepts: `{ "token": "<reset_token>" }`
  - Returns: User email if token is valid
  - 1-hour token expiration

- **POST `/api/auth/reset-password`**
  - Completes password reset with new password
  - Accepts: `{ "token": "<reset_token>", "password": "<new_password>", "confirmPassword": "<confirm_password>" }`
  - Validates password strength (min 8 characters)
  - Hashes password using bcrypt
  - Clears reset token after successful reset

#### 2. New File: `database/passwordreset_handler.py`
Utility functions for password reset operations:

- `generate_reset_token()` - Creates secure token
- `create_password_reset_request()` - Creates reset request in database
- `verify_reset_token()` - Validates token and expiration
- `reset_user_password()` - Updates password securely
- `clear_expired_reset_tokens()` - Cleanup function
- `get_user_by_email()` - User lookup utility
- `has_active_reset_request()` - Check for active reset

### Frontend Changes

#### 1. New File: `frontend/src/components/ForgotPassword.tsx`
React component for password reset request form:
- Email input field
- Form validation
- Loading state during submission
- Success/error messaging
- Automatic redirect to login after success
- Back to Login button

#### 2. New File: `frontend/src/components/ResetPassword.tsx`
React component for password reset form:
- Token verification on mount
- Password and confirm password fields
- Password strength validation (min 8 chars)
- Token expiration handling
- Success messaging with redirect
- Secure password handling

## Integration Notes

### Database Requirements
The implementation expects the `beehive_user_collection` to support these fields:
- `email` - User email address
- `password_reset_token` - Reset token string
- `password_reset_expires` - Token expiration datetime
- `password` - Hashed user password

### Route Registration
To enable these routes, register the auth blueprint in `app.py`:
```python
from routes.auth_routes import auth_bp
app.register_blueprint(auth_bp)
```

### Frontend Routes
Add routes to your React router configuration:
```typescript
<Route path="/forgot-password" element={<ForgotPassword />} />
<Route path="/reset-password" element={<ResetPassword />} />
```

### Email Configuration
To enable email sending, configure these environment variables:
```
FRONTEND_URL=http://localhost:5173  # or your production URL
SENDER_EMAIL=your-email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_PASSWORD=your-app-password
```

Then uncomment the email sending code in `auth_routes.py`.

## Security Features
- Secure token generation using `secrets.token_urlsafe()`
- 1-hour token expiration
- Password hashing with bcrypt
- Timing-safe email checks (no user enumeration)
- CSRF protection ready (can add to routes if needed)
- Password strength validation

## Testing Recommendations
1. Test forgot password flow with valid email
2. Test forgot password flow with non-existent email
3. Test token expiration (wait 1 hour or modify for testing)
4. Test password reset with valid token
5. Test password reset with expired token
6. Test password reset with mismatched passwords
7. Test password reset with weak password (<8 chars)
8. Verify token is cleared after successful reset

## Future Enhancements
- Email template customization
- Configurable token expiration time
- Rate limiting on forgot password endpoint
- Password reset history logging
- Two-factor authentication integration
- SMS-based reset option

## Files Modified
- Created: `routes/auth_routes.py`
- Created: `database/passwordreset_handler.py`
- Created: `frontend/src/components/ForgotPassword.tsx`
- Created: `frontend/src/components/ResetPassword.tsx`
- To be modified: `app.py` (to register auth blueprint)
- To be modified: Frontend route configuration

## References
Issue #482: Forget password feature request
