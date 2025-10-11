import React, { useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { Button } from './ui/button';
import { useAppDispatch, useAppSelector } from '../store';
import { updateProfile } from '../store/slices/authSlice';
import { toast } from 'sonner';

export default function ThemeToggle() {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const [isUpdating, setIsUpdating] = useState(false);

  const currentTheme = user?.color_theme || 'light';

  const toggleTheme = async () => {
    if (!user) return;

    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setIsUpdating(true);

    try {
      await dispatch(updateProfile({ color_theme: newTheme })).unwrap();
      
      // Apply theme to document
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
      
      toast.success(`Switched to ${newTheme} mode`);
    } catch (error) {
      toast.error('Failed to update theme');
    } finally {
      setIsUpdating(false);
    }
  };

  // Apply theme on component mount
  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', currentTheme === 'dark');
  }, [currentTheme]);

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleTheme}
      disabled={isUpdating}
      className="w-9 h-9 p-0"
      title={`Switch to ${currentTheme === 'light' ? 'dark' : 'light'} mode`}
    >
      {currentTheme === 'light' ? (
        <Moon className="h-4 w-4" />
      ) : (
        <Sun className="h-4 w-4" />
      )}
    </Button>
  );
}
