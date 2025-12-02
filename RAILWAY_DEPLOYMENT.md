# Railway Deployment Guide for ProjectAlpha v1

## Issue Fixed
The healthcheck was failing because `/api/` endpoint didn't exist. Fixed by:
1. Created dedicated health endpoint at `/api/health/`
2. Updated `railway.toml` to use `/api/health/` for healthcheck
3. Fixed working directory in start commands (added `cd projectalphav1`)

## Required Railway Environment Variables

### Database
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```
**IMPORTANT**: For Neon PostgreSQL, use the **UNPOOLED** connection string (without `-pooler` in hostname)

### Django Configuration
```bash
DJANGO_SECRET_KEY=<your-secret-key>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=.railway.app,your-domain.com
DJANGO_SETTINGS_MODULE=projectalphav1.settings
PYTHONUNBUFFERED=1
```

### CORS & CSRF Configuration
```bash
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app,https://your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend.railway.app,https://your-domain.com
DJANGO_CORS_ALLOW_ALL_ORIGINS=0
```

### Database Selection (Optional - defaults to 'dev')
```bash
DJANGO_DB=prod  # Options: dev, newdev, prod, local
```

### External Services (Required for full functionality)
```bash
# Egnyte Document Management
EGNYTE_DOMAIN=projectalpha.egnyte.com
EGNYTE_API_TOKEN=<your-token>

# AI Services
ANTHROPIC_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>

# Microsoft Graph (Outlook integration)
MICROSOFT_CLIENT_ID=<your-client-id>
MICROSOFT_CLIENT_SECRET=<your-secret>
MICROSOFT_TENANT_ID=<your-tenant-id>

# FRED API (Economic data)
FRED_API_KEY=<your-key>

# Geocoding
GEOCODIO_API_KEY=<your-key>
```

## Deployment Steps

### 1. Set Environment Variables in Railway
In Railway Dashboard → Service → Variables, add all required variables above.

### 2. Deploy
```bash
# Railway will automatically deploy on git push if connected to GitHub
git push origin main

# Or deploy manually with Railway CLI
railway up
```

### 3. Monitor Deployment
The healthcheck will verify:
- Django application is running
- Database connection is working
- Service responds at `/api/health/`

### 4. Verify Deployment
```bash
# Check health endpoint
curl https://your-app.railway.app/api/health/

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "debug": false
}
```

## Common Issues & Solutions

### Issue: Healthcheck Failing
**Symptoms**: Deployment shows "service unavailable" after build
**Solution**: 
- Verify DATABASE_URL is set correctly
- Check logs: `railway logs`
- Ensure PORT environment variable is available ($PORT)

### Issue: Static Files Not Loading
**Symptoms**: Frontend loads but has no styling/images
**Solution**:
- Verify collectstatic ran during deployment
- Check ALLOWED_HOSTS includes Railway domain
- Ensure WhiteNoise is in MIDDLEWARE (already configured)

### Issue: Database Connection Errors
**Symptoms**: 503 errors, "database disconnected" in health check
**Solution**:
- Use UNPOOLED Neon connection (remove `-pooler` from hostname)
- Verify DATABASE_URL format
- Check database credentials

### Issue: CSRF/CORS Errors
**Symptoms**: Frontend can't make API requests
**Solution**:
- Add Railway frontend URL to DJANGO_CORS_ALLOWED_ORIGINS
- Add Railway frontend URL to DJANGO_CSRF_TRUSTED_ORIGINS
- Ensure both use `https://` prefix

## Docker Build Warnings (Can be ignored for now)
The Docker build shows warnings about secrets in ARG/ENV. These are not critical for Railway deployment but should be fixed for production by using Railway's secret management instead of build args.

## Health Endpoint Details
- **URL**: `/api/health/`
- **Method**: GET
- **Authentication**: None required
- **Response Codes**:
  - 200: Service healthy, database connected
  - 503: Service unhealthy, database issue

## Notes
- Railway automatically provides $PORT variable
- Gunicorn binds to 0.0.0.0:$PORT
- Migrations run automatically on deployment
- Static files collected automatically on deployment
- Frontend Vue app served by Django for SPA routing

