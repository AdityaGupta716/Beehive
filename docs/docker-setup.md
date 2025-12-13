
## Run with Docker

### 1. Clone Repository
```bash
git clone https://github.com/kathiravelulab/Beehive.git
cd Beehive
```

### 2. Configure Environment & Authentication

**Clerk Setup:**
- Sign up at [clerk.dev](https://clerk.dev) and create an application
- Get your Publishable and Secret Keys
- Navigate to **Configure** → **Sessions** → **Claims** and add:
```json
{
    "role": "{{user.public_metadata.role || 'user'}}"
}
```

**Grant Admin Access for Local Development:**
To access the admin dashboard in your local development environment:

**Prerequisite:** Make sure the session claim is configured in Clerk Dashboard (Configure → Sessions → Claims) with `{"role": "{{user.public_metadata.role || 'user'}}"}` as mentioned above.

1. Go to [Clerk Dashboard](https://dashboard.clerk.dev/)
2. Navigate to **Users** (not Organizations)
3. Find your user account (search by your email address)
4. Click on your user profile
5. Go to **Metadata** section
6. Under **Public metadata**, add:
   ```json
   {
     "role": "admin"
   }
   ```
7. Click **Save**
8. **Logout and login again** from the application to refresh your session token

**Note:** This admin access is for local development only and uses your local Docker MongoDB instance, separate from production.

**Verification:**
After logging in again, you can verify your role in the browser console:
```javascript
console.log(user?.publicMetadata?.role)
// Should show: "admin"
```

**Accessing Admin Dashboard:**
- Navigate to `http://localhost:5173/admin`
- You should now have access to:
  - Admin Dashboard (`/admin`)
  - User Management (`/admin/users`)
  - Analytics (`/admin/analytics`)

**Google OAuth:**
- Create OAuth credentials in Google Cloud Console
- Download `client_secret.json` to project root
- Add redirect URI: `http://localhost:5000/admin/login/callback`

**Root `.env`:**
```env
MONGODB_CONNECTION_STRING=mongodb://mongo:27017/beehive
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
REDIRECT_URI=http://localhost:5000/admin/login/callback
ADMIN_EMAILS=admin1@example.com,admin2@example.com
CLERK_SECRET_KEY=your-clerk-secret-key
FLASK_SECRET_KEY=your_custom_flask_secret
```

**`frontend/.env`:**
```env
VITE_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
```

### 3. Run Docker

**Start:**
```bash
docker compose up --build
```

**Access:**
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:5173`
- Admin Dashboard: `http://localhost:5173/admin` (requires admin role setup - see Clerk Setup above)
- MongoDB: `localhost:27017` (containerized)


**Stop:** `Ctrl+C` or `docker compose down`

**Restart:** `docker compose up`

