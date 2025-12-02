# Railway Deployment Healthcheck Fixes - Summary

## Problem
Railway healthcheck was failing with "service unavailable" because:
1. ❌ Healthcheck path `/api/` didn't exist (no endpoint at that URL)
2. ❌ Local `.env` file was being deployed to Railway, conflicting with Railway environment variables
3. ❌ Working directory not set correctly for Django commands

## Solutions Implemented

### 1. ✅ Created Health Endpoint
**File**: `projectalphav1/core/views/view_co_health.py`
- New dedicated health check endpoint at `/api/health/`
- Tests database connectivity
- Returns 200 OK if healthy, 503 if database issues
- No authentication required

**File**: `projectalphav1/projectalphav1/urls.py`
- Added route: `path('api/health/', health_check, name='health-check')`

### 2. ✅ Updated Railway Configuration
**File**: `railway.toml`
- Changed healthcheck path from `/api/` to `/api/health/`
- Fixed start command to change to correct directory: `cd projectalphav1`
- Added `DJANGO_DEBUG=0` to environment variables

**File**: `Procfile`
- Updated to include `cd projectalphav1` for both release and web commands

### 3. ✅ Prevented .env Deployment
**File**: `.dockerignore` (NEW)
- Blocks `.env` and `.env.*` files from being deployed
- Railway will now use only OS environment variables
- Local `.env` still works for development

### 4. ✅ Improved Environment Variable Logging
**File**: `projectalphav1/projectalphav1/settings.py`
- Added startup logs showing:
  - Whether .env files are loaded (for debugging)
  - Which database connection is being used
  - Clear indication when using Railway env vars vs local .env

### 5. ✅ Created Reference Documentation
**File**: `railway.env.template`
- Template showing all required Railway environment variables
- Includes notes about using UNPOOLED Neon connections
- Reference for setting up new Railway deployments

**File**: `RAILWAY_DEPLOYMENT.md`
- Complete deployment guide
- Troubleshooting steps
- Common issues and solutions

## What You Need to Do

### In Railway Dashboard:

1. **Verify Environment Variables** are set (Variables tab):
   ```
   DATABASE_URL=postgresql://neondb_owner:...@ep-sweet-unit-afg5w70r.us-west-2.aws.neon.tech/neondb
   DJANGO_SECRET_KEY=<your-secret-key>
   DJANGO_DEBUG=0
   DJANGO_DB=prod
   DJANGO_ALLOWED_HOSTS=.railway.app,your-domain.com
   DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app
   DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend.railway.app
   (and all other API keys)
   ```

2. **Important**: Use UNPOOLED Neon connection for DATABASE_URL
   - ❌ Wrong: `...@ep-sweet-unit-afg5w70r-pooler.us-west-2...`
   - ✅ Correct: `...@ep-sweet-unit-afg5w70r.us-west-2...` (no `-pooler`)

3. **Deploy**: Push changes or redeploy
   ```bash
   git add .
   git commit -m "Fix Railway healthcheck endpoint and environment config"
   git push origin main
   ```

4. **Verify Deployment**:
   - Wait for build to complete
   - Check logs for: `✅ Loaded .env` messages (should NOT appear in Railway)
   - Check logs for: `🗄️ Using explicit DATABASE_URL` (should appear in Railway)
   - Test health endpoint: `curl https://your-app.railway.app/api/health/`

## Expected Logs in Railway

You should see in Railway logs:
```
🔧 Django starting from: /app/projectalphav1
📝 Checking for .env files (Railway deployments use OS env vars instead)...
ℹ️  No .env found (expected for Railway deployment)
🗄️  Using explicit DATABASE_URL from environment
   → Connected to: Neon PROD branch
```

## Testing the Fix Locally

Before pushing, test locally:
```powershell
# Activate venv
& "B:\Garrett_Local_Share\ProjectAlpha_v1\.venv\Scripts\Activate.ps1"

# Test health endpoint
cd projectalphav1
python manage.py runserver

# In another terminal:
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "debug": true
}
```

## Files Changed

1. ✏️ `projectalphav1/core/views/view_co_health.py` - NEW health check view
2. ✏️ `projectalphav1/projectalphav1/urls.py` - Added health endpoint route
3. ✏️ `railway.toml` - Updated healthcheck path and start command
4. ✏️ `Procfile` - Fixed working directory
5. ✏️ `.dockerignore` - NEW, prevents .env deployment
6. ✏️ `projectalphav1/projectalphav1/settings.py` - Better logging
7. 📄 `railway.env.template` - NEW reference template
8. 📄 `RAILWAY_DEPLOYMENT.md` - NEW deployment guide

## Next Steps

1. ✅ Push changes to GitHub
2. ✅ Verify Railway environment variables are set correctly
3. ✅ Wait for automatic deployment or trigger manually
4. ✅ Check Railway logs for successful startup
5. ✅ Test the health endpoint
6. ✅ Verify your app is accessible

## Troubleshooting

If healthcheck still fails:
- Check Railway logs: `railway logs` (if CLI is linked)
- Verify DATABASE_URL is UNPOOLED connection
- Ensure all required env vars are set
- Check that DJANGO_ALLOWED_HOSTS includes Railway domain
- Verify $PORT is not manually set (Railway provides it automatically)

