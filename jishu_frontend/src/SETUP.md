# 🚀 Jishu App - Local Setup Guide

## Prerequisites

- **Node.js** version 18 or higher
- **npm**, **yarn**, or **pnpm** package manager

## Step-by-Step Installation

### 1. Clean Installation

If you've already run `npm install` before, clean up first:

```bash
# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Or on Windows
rmdir /s node_modules
del package-lock.json
```

### 2. Install Dependencies

```bash
npm install
```

**What this installs:**
- React 18 with TypeScript
- Tailwind CSS v3 (more stable than v4 for local dev)
- All shadcn/ui components
- React Router for navigation
- Recharts for analytics
- All necessary build tools

### 3. Start Development Server

```bash
npm run dev
```

You should see output like:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 4. Open in Browser

Navigate to `http://localhost:5173`

You should now see the **fully styled Jishu App** with:
- ✅ Gradient backgrounds
- ✅ Proper colors and spacing
- ✅ Working navigation
- ✅ All UI components styled correctly

## 🔍 Troubleshooting

### Problem: CSS Not Loading / Unstyled Content

**Solution 1: Clear Vite Cache**
```bash
# Stop the server (Ctrl+C)
rm -rf node_modules/.vite
npm run dev
```

**Solution 2: Hard Refresh Browser**
- Chrome/Edge: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Firefox: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)

**Solution 3: Check Console for Errors**
- Open browser DevTools (F12)
- Check Console tab for any errors
- Check Network tab to ensure CSS is loading

### Problem: TypeScript Errors

```bash
# Reinstall TypeScript dependencies
npm install --save-dev typescript @types/react @types/react-dom
```

### Problem: Port 5173 Already in Use

```bash
# Kill the process using that port (Linux/Mac)
lsof -ti:5173 | xargs kill -9

# Or use a different port
npm run dev -- --port 3000
```

### Problem: Module Not Found Errors

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

## 📁 Project Structure

```
jishu-app/
├── components/           # All React components
│   ├── admin/           # Admin dashboard components
│   ├── figma/           # Helper components
│   └── ui/              # shadcn/ui components
├── styles/
│   └── globals.css      # Tailwind CSS + custom styles
├── App.tsx              # Main app with routing
├── main.tsx             # React entry point
├── index.html           # HTML template
├── tailwind.config.js   # Tailwind configuration
├── vite.config.ts       # Vite configuration
└── package.json         # Dependencies

```

## 🎨 What You Should See

### Landing Page
- Hero section with gradient background
- "Ace Your with Confidence" heading
- Study image on the right
- CTA buttons (Start Free Trial, Watch Demo)
- Features showcase

### Navigation
- Header with logo and menu
- Routes working: Features, Exams, About, Login, Get Started

### All Screens Working
- Authentication
- Course Selection
- Subject Selection  
- Mock Test Purchase
- MCQ Test Interface
- Results Dashboard with charts
- Community Blog
- AI Chatbot
- User Profile
- Admin Dashboard

## 🛠️ Available Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🔐 Demo Credentials

### User Login
- Email: `user@example.com`
- Password: `any password` (mock auth)

### Admin Login  
- Email: `admin@jishu.com`
- Password: `any password` (mock auth)

## 📝 Notes

- This app uses **mock data** - no real backend yet
- All authentication is simulated
- Perfect for prototyping and frontend development
- Ready to connect to a real API when needed

## ✅ Success Checklist

After setup, verify:
- [ ] `npm install` completed without errors
- [ ] `npm run dev` starts server successfully
- [ ] Browser opens to landing page
- [ ] CSS styles are applied (gradients, colors, proper spacing)
- [ ] Navigation between pages works
- [ ] All components render correctly
- [ ] No console errors in browser DevTools

## 🆘 Still Having Issues?

If problems persist:

1. Check Node.js version: `node --version` (should be 18+)
2. Check npm version: `npm --version` (should be 8+)
3. Try with a different package manager:
   ```bash
   # Using yarn
   yarn install
   yarn dev
   
   # Using pnpm
   pnpm install
   pnpm dev
   ```

## 🎯 Next Steps

Once you have the app running:
1. Explore all the screens
2. Test the mock functionality
3. Customize colors/branding in `tailwind.config.js`
4. Add your own features
5. Connect to a real backend API

---

**Need help?** Check the main README.md or TROUBLESHOOTING.md files.
