import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner@2.0.3';
import { useAppDispatch } from '../store';
import { setCredentials } from '../store/slices/authSlice';

interface GoogleOAuthCallbackProps {
  onLogin: (userData: any) => void;
}

export default function GoogleOAuthCallback({ onLogin }: GoogleOAuthCallbackProps) {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        toast.error('Google OAuth was cancelled or failed');
        navigate('/auth');
        return;
      }

      if (!code) {
        toast.error('No authorization code received from Google');
        navigate('/auth');
        return;
      }

      try {
        // Send the authorization code to our backend
        const response = await fetch('http://localhost:5000/api/auth/google/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        });

        const data = await response.json();

        if (data.success && data.data) {
          // Store tokens and user data
          localStorage.setItem('access_token', data.data.access_token);
          localStorage.setItem('refresh_token', data.data.refresh_token);
          localStorage.setItem('jishu_user', JSON.stringify(data.data.user));

          // Update Redux state
          dispatch(setCredentials({
            user: data.data.user,
            token: data.data.access_token,
          }));

          // Call the onLogin callback
          onLogin(data.data.user);

          toast.success('Successfully logged in with Google!');
          
          // Navigate based on user role
          navigate(data.data.user.is_admin ? '/admin' : '/courses');
        } else {
          toast.error(data.message || 'Google OAuth failed');
          navigate('/auth');
        }
      } catch (error) {
        console.error('Google OAuth callback error:', error);
        toast.error('Failed to complete Google OAuth');
        navigate('/auth');
      }
    };

    handleCallback();
  }, [searchParams, navigate, dispatch, onLogin]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
        <h2 className="text-2xl font-semibold mb-2">Completing Google Sign In</h2>
        <p className="text-gray-600">Please wait while we verify your account...</p>
      </div>
    </div>
  );
}
