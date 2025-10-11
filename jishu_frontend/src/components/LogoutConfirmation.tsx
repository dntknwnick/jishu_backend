import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { LogOut, Home } from 'lucide-react';

interface LogoutConfirmationProps {
  onLogout: () => void;
}

export default function LogoutConfirmation({ onLogout }: LogoutConfirmationProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  const handleCancel = () => {
    navigate(-1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardContent className="p-8 text-center space-y-6">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto">
            <LogOut className="w-10 h-10 text-white" />
          </div>
          
          <div className="space-y-2">
            <h2 className="text-3xl">Logout?</h2>
            <p className="text-gray-600">
              Are you sure you want to logout? Your progress will be saved.
            </p>
          </div>

          <div className="space-y-3">
            <Button 
              size="lg" 
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600"
              onClick={handleLogout}
            >
              <LogOut className="w-5 h-5 mr-2" />
              Yes, Logout
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="w-full"
              onClick={handleCancel}
            >
              <Home className="w-5 h-5 mr-2" />
              Stay Logged In
            </Button>
          </div>

          <p className="text-sm text-gray-500">
            You can always log back in anytime to continue your preparation
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
