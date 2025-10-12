# Google OAuth Fix Guide

## 🔍 **Problem Identified**

The `invalid_grant` error was caused by a **redirect URI mismatch** between the Google OAuth configuration and the actual OAuth flow.

### **Root Cause**
- **Backend Configuration**: `GOOGLE_REDIRECT_URI` was set to `http://localhost:5000/auth/google/callback`
- **Frontend Flow**: Google was redirecting to `http://localhost:3000/auth/google/callback`
- **Result**: Authorization code generated for one URI was being used with a different URI configuration

## ✅ **Solution Implemented**

### **1. Fixed Configuration (`config.py`)**
```python
# OLD (Incorrect)
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')

# NEW (Correct)
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/google/callback')
```

### **2. Enhanced Debugging**
Added comprehensive logging to help diagnose OAuth issues:

**Backend (`app.py`)**:
```python
print(f"🔄 Processing Google OAuth verification...")
print(f"🔧 Authorization code received: {authorization_code[:20]}...")
print(f"🔧 Google OAuth redirect URI: {google_oauth.redirect_uri}")
```

**Google OAuth Service (`shared/utils/google_oauth.py`)**:
```python
print(f"🔄 Exchanging authorization code for token...")
print(f"🔧 Using redirect URI: {self.redirect_uri}")
print(f"🔧 Authorization code length: {len(authorization_code) if authorization_code else 0}")
```

### **3. Verification**
Backend now correctly initializes with:
```
🔧 Creating Google OAuth service with redirect URI: http://localhost:3000/auth/google/callback
🔧 GoogleOAuthService initialized with redirect_uri: http://localhost:3000/auth/google/callback
```

## 🚀 **OAuth Flow (Now Working)**

### **Step-by-Step Process**
1. **User clicks "Continue with Google"** in frontend
2. **Frontend calls** `GET http://localhost:5000/auth/google`
3. **Backend returns** Google authorization URL with correct redirect URI
4. **User redirected to Google** for consent
5. **Google redirects back** to `http://localhost:3000/auth/google/callback?code=...`
6. **Frontend receives** authorization code
7. **Frontend sends code** to `POST http://localhost:5000/api/auth/google/verify`
8. **Backend exchanges code** for user info using matching redirect URI
9. **Success!** User authenticated and tokens returned

## 🔧 **Additional Requirements**

### **Google Cloud Console Configuration**
Ensure your Google Cloud Console OAuth 2.0 Client has the correct redirect URI:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > Credentials**
3. Edit your OAuth 2.0 Client ID
4. In **Authorized redirect URIs**, add:
   ```
   http://localhost:3000/auth/google/callback
   ```
5. Remove any old redirect URIs pointing to `:5000`

### **Environment Variables**
Set these environment variables or use the defaults:
```bash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

## 🧪 **Testing the Fix**

### **Test Steps**
1. **Start Backend**: `python app.py` (should show correct redirect URI in logs)
2. **Start Frontend**: Navigate to auth page
3. **Click "Continue with Google"**
4. **Complete OAuth flow**
5. **Check backend logs** for debugging information

### **Expected Logs**
```
🔧 Creating Google OAuth service with redirect URI: http://localhost:3000/auth/google/callback
🔄 Processing Google OAuth verification...
🔧 Authorization code received: 4/0AeaYSHABC123...
🔧 Using redirect URI: http://localhost:3000/auth/google/callback
✅ Successfully obtained credentials
✅ Successfully fetched user info: user@example.com
```

## ❌ **Common Issues & Solutions**

### **1. Still Getting `invalid_grant`**
- **Check Google Cloud Console**: Ensure redirect URI matches exactly
- **Clear Browser Cache**: OAuth state might be cached
- **Check Environment Variables**: Verify `GOOGLE_REDIRECT_URI` is set correctly

### **2. `Google OAuth not configured`**
- **Missing Credentials**: Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- **Check Logs**: Look for "Google OAuth not configured - missing credentials"

### **3. `Authorization code not provided`**
- **Frontend Issue**: Check if code is being extracted from URL parameters
- **Network Issue**: Verify frontend can reach backend

### **4. `Failed to fetch user information`**
- **Scope Issues**: Ensure OAuth scopes include email and profile
- **Token Expiry**: Authorization codes expire quickly (10 minutes)

## 🎯 **Status**

✅ **Configuration Fixed**: Redirect URI now points to frontend
✅ **Debugging Added**: Comprehensive logging for troubleshooting  
✅ **Backend Running**: OAuth service initialized correctly
✅ **Ready for Testing**: OAuth flow should now work properly

The Google OAuth `invalid_grant` error should now be resolved. Test the OAuth flow and check the backend logs for any remaining issues.
