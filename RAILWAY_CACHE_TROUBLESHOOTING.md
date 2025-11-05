# Railway Cache Troubleshooting

## When Railway Cache Causes Issues

Railway caches build artifacts to speed up deployments. However, sometimes stale cache causes problems:

### Symptoms:
- ❌ Django errors about missing models/fields that exist locally
- ❌ Import errors that don't happen locally
- ❌ Database relationship errors (e.g., "Invalid field name")
- ❌ Mysterious 500 errors in production that work locally

---

## How to Fix Stale Cache Issues

### Option 1: Clear Cache in Railway Dashboard (Recommended)
1. Go to Railway Dashboard → Your Project
2. Click on your Django service
3. Go to **Settings** tab
4. Scroll down to **Danger Zone**
5. Click **"Clear Build Cache"**
6. Click **"Redeploy"** or push a new commit

### Option 2: Force Clean Build via Code (Temporary)
Edit `railway.toml`:
```toml
[build.nixpacksPhase]
cmds = [
    "python -m pip install --upgrade pip",
    "pip install --no-cache-dir -r requirements.txt"  # Add --no-cache-dir
]
```
⚠️ **Remember to remove `--no-cache-dir` after** - it makes builds much slower!

### Option 3: Modify requirements.txt (Automatic Cache Bust)
Railway automatically clears cache if `requirements.txt` changes:
- Add a new dependency
- Update a version number
- Even just add/remove a comment

---

## Prevention Best Practices

### ✅ DO:
- Use Railway's normal caching (it's fast!)
- Clear cache manually when you see weird issues
- Run migrations automatically in `startCommand`
- Test major changes locally before pushing

### ❌ DON'T:
- Keep `--no-cache-dir` permanently (too slow)
- Manually delete Python bytecode (Railway handles this)
- Skip migrations in production

---

## When Cache Issues Happen

Cache issues typically occur after:
- 🔄 Major Django model changes
- 📦 Switching database providers (like Railway → Neon)
- 🏗️ Restructuring apps/imports
- 🔧 Changing INSTALLED_APPS

**Quick fix:** Clear cache in Railway Dashboard!

---

## Current Setup
- **Build cache:** ✅ Enabled (fast builds)
- **Auto migrations:** ✅ Enabled in `railway.toml`
- **Database:** Neon PostgreSQL
- **Clean rebuild trigger:** Change `requirements.txt` or clear cache manually


