# Jishu App - Troubleshooting Guide

## Recent Fixes Applied

### 1. Fixed AIChatbot Component
- **Issue**: ScrollArea ref was causing potential rendering issues
- **Fix**: Replaced ScrollArea with standard div and updated scroll behavior to use `messagesEndRef` with `scrollIntoView`

### 2. Fixed MCQTestScreen Timer
- **Issue**: Timer was calling `handleSubmit` which wasn't in the useEffect dependency array
- **Fix**: Separated auto-submit logic into its own useEffect with proper dependencies

### 3. Added Error Handling in App.tsx
- **Issue**: localStorage parsing could fail
- **Fix**: Added try-catch block around localStorage operations

## Component Structure

### User Flow
1. **Landing Page** (`/`) - Public marketing page
2. **Auth Screen** (`/auth`) - Login/Register with email/password, OTP, Google OAuth
3. **Course Selection** (`/courses`) - Choose exam (NEET, JEE, CET)
4. **Subject Selection** (`/subjects/:courseId`) - Choose subjects and packages
5. **Purchase** (`/purchase`) - Checkout and payment
6. **Test Screen** (`/test/:testId`) - Take MCQ tests
7. **Results** (`/results`) - View scores and analytics
8. **Community** (`/community`) - Blog posts and discussions
9. **Post Details** (`/post/:postId`) - Individual post with comments
10. **AI Chatbot** (`/chatbot`) - Educational AI assistant
11. **Profile** (`/profile`) - User profile management
12. **Account** (`/account`) - Account settings
13. **Logout** (`/logout`) - Logout confirmation

### Admin Flow
1. **Admin Dashboard** (`/admin`) - Overview with stats
2. **Manage Courses** (`/admin/courses`) - CRUD for test series
3. **Manage Posts** (`/admin/posts`) - Moderate blog posts/comments
4. **Manage Users** (`/admin/users`) - User management
5. **Payment History** (`/admin/payments`) - Transaction tracking

## Mock Login Credentials

### Admin Access
- Email: `admin@jishu.com`
- Password: `any password` (mock authentication)

### User Access
- Any other email with any password (mock authentication)
- Google OAuth button also available (mock)

## Known Mock Data

- All test results are stored in localStorage under `jishu_results`
- User data stored in localStorage under `jishu_user`
- No real backend - all data is client-side only

## Common Issues

### Issue: Page not loading
**Solution**: Clear localStorage and refresh
```javascript
localStorage.clear();
location.reload();
```

### Issue: Timer not working
**Solution**: Make sure you click "Start Test" on the instructions screen

### Issue: Tests not appearing in results
**Solution**: Complete and submit a test first - results are stored in localStorage

## Development Notes

- Built with React + TypeScript
- Tailwind CSS for styling
- ShadCN UI components
- Recharts for analytics
- React Router for navigation
- No real backend (all mock data)
