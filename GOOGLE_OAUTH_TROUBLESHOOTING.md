# Google OAuth Troubleshooting Guide

## 🔍 **Current Status**

✅ **Backend Configuration**: Correct
- Client ID: Set and valid
- Client Secret: Set
- Redirect URI: `http://localhost:3000/auth/google/callback`
- Scopes: email, profile, openid

❌ **Issue**: Still getting `invalid_grant` error

## 🎯 **Most Likely Causes & Solutions**

### **1. Google Cloud Console Configuration (Most Common)**

**Problem**: The redirect URI is not properly configured in Google Cloud Console.

**Solution**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > Credentials**
3. Find your OAuth 2.0 Client ID
4. Click **Edit**
5. In **Authorized redirect URIs**, ensure you have **EXACTLY**:
   ```
   http://localhost:3000/auth/google/callback
   ```
6. **Remove any other localhost redirect URIs** (like `:5000` ones)
7. **Save** the changes
8. **Wait 5-10 minutes** for changes to propagate

### **2. Authorization Code Expiry**

**Problem**: Authorization codes expire in 10 minutes and can only be used once.

**Solution**:
- Ensure you're testing the OAuth flow quickly after getting the code
- Don't refresh the callback page (generates new code)
- Clear browser cache if you've been testing repeatedly

### **3. Client ID/Secret Mismatch**

**Problem**: The credentials might be for a different project or environment.

**Solution**:
1. Verify the Client ID in Google Cloud Console matches: `450138266478-7t89vga...`
2. Regenerate Client Secret if needed
3. Update environment variables:
   ```bash
   GOOGLE_CLIENT_ID=your_actual_client_id
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   ```

### **4. Development vs Production Environment**

**Problem**: OAuth client might be configured for production domains.

**Solution**:
1. Create a **separate OAuth client** for development
2. Configure it specifically for localhost URLs
3. Use different credentials for dev vs prod

## 🔧 **Step-by-Step Fix**

### **Step 1: Verify Google Cloud Console**
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Go to **APIs & Services > Credentials**
3. Find OAuth 2.0 Client ID: `450138266478-7t89vga...`
4. Verify **Authorized redirect URIs** contains:
   ```
   http://localhost:3000/auth/google/callback
   ```

### **Step 2: Test OAuth URL Generation**
```bash
# Test that OAuth URL is generated correctly
curl http://localhost:5000/auth/google
```
Should return authorization URL with correct redirect_uri.

### **Step 3: Manual OAuth Test**
1. Get authorization URL from Step 2
2. Open it in browser
3. Complete Google OAuth consent
4. Note the `code` parameter in the callback URL
5. Test the verification endpoint manually:
   ```bash
   curl -X POST http://localhost:5000/api/auth/google/verify \
     -H "Content-Type: application/json" \
     -d '{"code":"YOUR_CODE_HERE"}'
   ```

### **Step 4: Check Backend Logs**
Look for these debug messages:
```
🔄 Processing Google OAuth verification...
🔧 Authorization code received: 4/0AeaYSH...
🔧 Using redirect URI: http://localhost:3000/auth/google/callback
🔄 Exchanging authorization code for token...
```

## 🚨 **Common Mistakes**

### **1. Wrong Redirect URI Format**
❌ `http://localhost:3000/auth/google/callback/`  (trailing slash)
❌ `https://localhost:3000/auth/google/callback`  (https instead of http)
❌ `http://127.0.0.1:3000/auth/google/callback`   (127.0.0.1 instead of localhost)
✅ `http://localhost:3000/auth/google/callback`   (correct)

### **2. Multiple Redirect URIs**
Having both `:3000` and `:5000` redirect URIs can cause confusion. Keep only the frontend one.

### **3. Cached OAuth State**
Clear browser cache and cookies for localhost to reset OAuth state.

## 🔍 **Advanced Debugging**

### **Enable Detailed Logging**
The backend now includes enhanced debugging. Watch for:
```
❌ Error exchanging code for token: (invalid_grant) Bad Request
🔧 Exception type: RefreshError
🔧 Exception details: [detailed error info]
🔧 Response text: [Google's error response]
```

### **Test with Different Browser**
Try the OAuth flow in an incognito window or different browser to rule out caching issues.

### **Check Network Tab**
In browser dev tools, check the Network tab during OAuth flow to see:
1. Initial redirect to Google
2. Callback with authorization code
3. POST to `/api/auth/google/verify`

## 🎯 **Next Steps**

1. **Verify Google Cloud Console** redirect URI configuration
2. **Wait 5-10 minutes** after making changes
3. **Test OAuth flow** in fresh browser session
4. **Check backend logs** for detailed error information
5. **Try manual OAuth test** to isolate the issue

The most common fix is ensuring the Google Cloud Console has the exact redirect URI: `http://localhost:3000/auth/google/callback`
