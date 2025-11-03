# Egnyte Integration - Quick Start Guide

## ❓ What is a REST API?

**REST API** = A way for applications to talk to each other over the internet using HTTP requests

Think of it like ordering food:
- **You (Vue)** → Tell waiter what you want
- **Waiter (HTTP)** → Takes order to kitchen
- **Kitchen (Django)** → Prepares it / calls Egnyte
- **Response** → Food comes back to you

## 🏗️ Your Architecture

```
Vue.js Frontend  ←→  Django Backend  ←→  Egnyte Cloud Storage
   (Browser)      (Your Server)         (Document Storage)
```

## ✅ Python SDK is Still Usable!

**To answer your question**: No, the notice doesn't mean you can't use Egnyte with Python!

### What the "No Longer Supported" Notice Means:
- ✅ **The REST API works fine** - Fully supported by Egnyte
- ✅ **You CAN use Python** - Use `requests` library to call the API
- ⚠️ **The Python SDK is unmaintained** - But you don't need it!
- ✅ **Better approach**: Call REST API directly (which I've set up for you)

### Why Direct REST API is Better:
1. More control over requests
2. No dependency on unmaintained code
3. Official Egnyte API is fully supported
4. Works with any programming language

## 🚀 What I Built For You

### 1. Django Backend (Python)
✅ `egnyte_service.py` - Calls Egnyte REST API using `requests` library
✅ `document_api.py` - REST API endpoints for Vue to call
✅ URL routes configured

### 2. Vue Frontend (JavaScript)
✅ `egnyteService.js` - Service to call Django API
✅ `DocumentManager.vue` - Complete UI component example

### 3. Documentation
✅ `EGNYTE_INTEGRATION_GUIDE.md` - Complete setup guide
✅ This quick start guide

## 📝 Setup in 3 Steps

### Step 1: Get Egnyte Credentials
1. Login to Egnyte
2. Settings → API → Create API Key
3. Copy your domain and token

### Step 2: Add to Django Settings
Edit `projectalphav1/projectalphav1/settings.py`:

```python
# Add these lines
EGNYTE_DOMAIN = 'yourcompany.egnyte.com'
EGNYTE_API_TOKEN = 'your-token-here'
```

### Step 3: Install Requests Library
```bash
pip install requests
```

## 🎯 How to Use in Your Vue App

### Upload a File:
```javascript
import egnyteService from '@/services/egnyteService';

// In your component method:
async uploadFile() {
  const response = await egnyteService.uploadDocument(
    this.selectedFile,
    '/Shared/Documents'
  );
  
  if (response.success) {
    alert('Uploaded!');
  }
}
```

### List Documents:
```javascript
const response = await egnyteService.listDocuments('/Shared');
const files = response.data.files;
```

### Download File:
```javascript
await egnyteService.downloadDocument('/Shared/Documents/file.pdf');
```

### Search Files:
```javascript
const response = await egnyteService.searchDocuments('invoice');
const results = response.results;
```

## 🔗 Available API Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `uploadDocument(file, folder)` | Upload file | Upload contract.pdf |
| `listDocuments(folder)` | List files | Show all in /Shared |
| `downloadDocument(path)` | Download file | Get report.pdf |
| `deleteDocument(path)` | Delete file | Remove old-file.pdf |
| `createFolder(path)` | New folder | Create /Shared/2024 |
| `searchDocuments(query)` | Search | Find "invoice" |
| `createShareLink(path)` | Share link | Get shareable URL |
| `getFileInfo(path)` | File details | Size, date, etc. |

## 🎨 Example Component

Use the included `DocumentManager.vue` component:

```vue
<template>
  <DocumentManager />
</template>

<script>
import DocumentManager from '@/components/DocumentManager.vue';

export default {
  components: {
    DocumentManager
  }
};
</script>
```

## 🔄 How REST API Works (Step by Step)

**Example: User uploads a file**

1. **User**: Selects file in Vue app
2. **Vue**: Calls `egnyteService.uploadDocument(file)`
3. **HTTP Request**: POST to `http://yourserver/api/core/documents/upload/`
4. **Django Receives**: Gets file and processes it
5. **Django → Egnyte**: POST to `https://yourcompany.egnyte.com/pubapi/v1/fs-content/...`
6. **Egnyte**: Stores file and returns success
7. **Egnyte → Django**: Returns JSON response
8. **Django → Vue**: Sends success response
9. **Vue**: Shows "Upload successful!" message

**All in less than 1 second!**

## 🧪 Testing

### Test Django Service:
```bash
python manage.py shell
```

```python
from core.services.serv_co_egnyteDoc import egnyte_service
result = egnyte_service.list_folder('/Shared')
print(result)
```

### Test API Endpoint:
```bash
# Start Django server
python manage.py runserver

# In another terminal (or use Postman):
curl http://localhost:8000/api/core/documents/list/?folder_path=/Shared \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📂 Files Created

```
projectalphav1/
├── core/
│   ├── services/
│   │   └── serv_co_egnyteDoc.py       ← Calls Egnyte REST API
│   ├── views/
│   │   └── view_co_egnyteDoc.py       ← Django REST endpoints
│   └── urls.py                        ← Updated with new routes
└── z.Admin/
    └── EGNYTE_INTEGRATION_GUIDE.md    ← Full documentation

frontend_vue/
└── src/
    ├── services/
    │   └── egnyteService.js            ← Vue API service
    └── components/
        └── DocumentManager.vue         ← Example component
```

## 🎓 Understanding REST API

### HTTP Methods:
- **GET**: Read/Retrieve data ("Show me the files")
- **POST**: Create/Upload ("Save this file")
- **PUT/PATCH**: Update ("Change this")
- **DELETE**: Remove ("Delete this file")

### Request/Response:
Every API call has two parts:

**Request** (Vue → Django):
```
POST /api/core/documents/upload/
Headers: Authorization, Content-Type
Body: {file: binary data, folder_path: '/Shared'}
```

**Response** (Django → Vue):
```json
{
  "success": true,
  "path": "/Shared/Documents/file.pdf",
  "message": "File uploaded successfully"
}
```

## 🔒 Security

✅ **DO**:
- Store API tokens in Django settings (backend only)
- Use environment variables in production
- Validate file types and sizes
- Require authentication on all endpoints

❌ **DON'T**:
- Never put Egnyte tokens in Vue code
- Never commit tokens to Git
- Never skip authentication

## 🚀 Next Steps

1. ✅ Add Egnyte credentials to Django settings
2. ✅ Test with `python manage.py shell`
3. ✅ Try the API endpoints with Postman
4. ✅ Import DocumentManager in your Vue app
5. ✅ Customize the UI to match your design
6. ✅ Add to your existing pages (like ValuationCenter.vue)

## 💡 Pro Tips

- **Start small**: Test one endpoint at a time
- **Use browser DevTools**: Watch Network tab to see API calls
- **Check Django logs**: They show detailed error messages
- **Read the guide**: Full documentation in `EGNYTE_INTEGRATION_GUIDE.md`

## ❓ Still Have Questions?

- Check `EGNYTE_INTEGRATION_GUIDE.md` for detailed explanations
- Egnyte API Docs: https://developers.egnyte.com/docs
- Test each layer separately (Django first, then Vue)

---

**You're all set! You can now use Egnyte as your document database provider with Python + Vue! 🎉**

