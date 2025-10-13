import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import { useAppDispatch, useAppSelector } from './store';
import { initializeAuth, clearCredentials, updateProfile } from './store/slices/authSlice';

// Import all screen components
import LandingPage from './components/LandingPage';
import AuthScreen from './components/AuthScreen';
import GoogleOAuthCallback from './components/GoogleOAuthCallback';
import CourseSelection from './components/CourseSelection';
import SubjectSelection from './components/SubjectSelection';
import MockTestPurchase from './components/MockTestPurchase';
import MCQTestScreen from './components/MCQTestScreen';
import MCQGenerator from './components/MCQGenerator';
import TestResultDashboard from './components/TestResultDashboard';
import TestCardDashboard from './components/TestCardDashboard';
import CommunityBlog from './components/CommunityBlog';
import PostDetails from './components/PostDetails';
import AIChatbot from './components/AIChatbot';

import UserProfile from './components/UserProfile';
import AccountManagement from './components/AccountManagement';
import LogoutConfirmation from './components/LogoutConfirmation';

// Admin screens
import AdminDashboard from './components/admin/AdminDashboard';
import ManageCourses from './components/admin/ManageCourses';
import ManagePosts from './components/admin/ManagePosts';
import ManageUsers from './components/admin/ManageUsers';
import PaymentHistory from './components/admin/PaymentHistory';

export default function App() {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const isAdmin = user?.is_admin || false;

  useEffect(() => {
    // Initialize auth state from localStorage
    dispatch(initializeAuth());
  }, [dispatch]);

  // Initialize theme from user preferences
  useEffect(() => {
    if (user?.color_theme) {
      document.documentElement.classList.toggle('dark', user.color_theme === 'dark');
    }
  }, [user?.color_theme]);

  const handleLogin = (userData: any) => {
    // This is now handled by Redux actions in AuthScreen
    // Keep for compatibility with existing components
  };

  const handleUpdateUser = async (userData: any) => {
    try {
      await dispatch(updateProfile(userData)).unwrap();
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const handleLogout = () => {
    dispatch(clearCredentials());
  };

  return (
    <Router>
      <Toaster />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/auth"
          element={
            isAuthenticated ?
            <Navigate to={isAdmin ? "/admin" : "/courses"} /> :
            <AuthScreen onLogin={handleLogin} />
          }
        />
        <Route
          path="/auth/google/callback"
          element={<GoogleOAuthCallback onLogin={handleLogin} />}
        />
        
        {/* Protected User Routes */}
        <Route
          path="/courses"
          element={isAuthenticated ? <CourseSelection user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/subjects/:courseId"
          element={isAuthenticated ? <SubjectSelection user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/purchase"
          element={isAuthenticated ? <MockTestPurchase user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/test/:testId"
          element={isAuthenticated ? <MCQTestScreen user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/test"
          element={isAuthenticated ? <MCQTestScreen user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/results"
          element={isAuthenticated ? <TestResultDashboard user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/test-cards"
          element={isAuthenticated ? <TestCardDashboard user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/dashboard"
          element={isAuthenticated ? <Navigate to="/results" /> : <Navigate to="/auth" />}
        />
        <Route
          path="/community"
          element={isAuthenticated ? <CommunityBlog user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/post/:postId"
          element={isAuthenticated ? <PostDetails user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/chatbot"
          element={isAuthenticated ? <AIChatbot user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/mcq-generator"
          element={isAuthenticated && !isAdmin ? <MCQGenerator user={user} /> : <Navigate to="/auth" />}
        />

        <Route
          path="/profile"
          element={isAuthenticated ? <UserProfile user={user} onUpdateUser={handleUpdateUser} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/account"
          element={isAuthenticated ? <AccountManagement user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/logout"
          element={isAuthenticated ? <LogoutConfirmation onLogout={handleLogout} /> : <Navigate to="/auth" />}
        />

        {/* Protected Admin Routes */}
        <Route
          path="/admin"
          element={isAuthenticated && isAdmin ? <AdminDashboard user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/admin/courses"
          element={isAuthenticated && isAdmin ? <ManageCourses user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/admin/posts"
          element={isAuthenticated && isAdmin ? <ManagePosts user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/admin/users"
          element={isAuthenticated && isAdmin ? <ManageUsers user={user} /> : <Navigate to="/auth" />}
        />
        <Route
          path="/admin/payments"
          element={isAuthenticated && isAdmin ? <PaymentHistory user={user} /> : <Navigate to="/auth" />}
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}
