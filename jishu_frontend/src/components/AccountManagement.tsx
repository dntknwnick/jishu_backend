import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { 
  Lock, 
  Bell, 
  Shield, 
  Trash2, 
  Key,
  AlertTriangle,
  CheckCircle2,
  Mail
} from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from './ui/alert-dialog';
import { toast } from 'sonner@2.0.3';

interface AccountManagementProps {
  user: any;
  onLogout: () => void;
}

export default function AccountManagement({ user, onLogout }: AccountManagementProps) {
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    testReminders: true,
    communityUpdates: false,
    weeklyReport: true
  });

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }
    
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    
    // Simulate password change
    toast.success('Password changed successfully!');
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  const handleResetPassword = () => {
    toast.success('Password reset link sent to your email!');
  };

  const handleDeactivateAccount = () => {
    // Simulate account deactivation
    toast.success('Account deactivated. You can reactivate anytime by logging in.');
    setTimeout(() => {
      onLogout();
      navigate('/');
    }, 2000);
  };

  const handleDeleteAccount = () => {
    // Simulate account deletion
    toast.success('Account deletion request submitted. You will receive a confirmation email.');
    setTimeout(() => {
      onLogout();
      navigate('/');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Account Settings</h1>
          <p className="text-xl text-muted-foreground">Manage your account preferences and security</p>
        </div>

        <div className="space-y-6">
          {/* Security Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security
              </CardTitle>
              <CardDescription>Manage your password and security settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Change Password */}
              <div>
                <h3 className="text-lg mb-4 flex items-center gap-2">
                  <Lock className="w-5 h-5" />
                  Change Password
                </h3>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="currentPassword">Current Password</Label>
                    <Input
                      id="currentPassword"
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Enter current password"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="newPassword">New Password</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm New Password</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit">Update Password</Button>
                    <Button type="button" variant="outline" onClick={handleResetPassword}>
                      <Mail className="w-4 h-4 mr-2" />
                      Email Reset Link
                    </Button>
                  </div>
                </form>
              </div>

              <Separator />

              {/* Two-Factor Authentication */}
              <div>
                <h3 className="text-lg mb-2 flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  Two-Factor Authentication
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Add an extra layer of security to your account
                </p>
                <Button variant="outline">
                  Enable 2FA
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notifications
              </CardTitle>
              <CardDescription>Manage how you receive updates and notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="email-notif">Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                </div>
                <Switch
                  id="email-notif"
                  checked={notifications.email}
                  onCheckedChange={(checked) => setNotifications({ ...notifications, email: checked })}
                />
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="push-notif">Push Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive push notifications in browser</p>
                </div>
                <Switch
                  id="push-notif"
                  checked={notifications.push}
                  onCheckedChange={(checked) => setNotifications({ ...notifications, push: checked })}
                />
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="test-reminders">Test Reminders</Label>
                  <p className="text-sm text-muted-foreground">Get reminders for scheduled tests</p>
                </div>
                <Switch
                  id="test-reminders"
                  checked={notifications.testReminders}
                  onCheckedChange={(checked) => setNotifications({ ...notifications, testReminders: checked })}
                />
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="community-updates">Community Updates</Label>
                  <p className="text-sm text-muted-foreground">Notifications from community posts</p>
                </div>
                <Switch
                  id="community-updates"
                  checked={notifications.communityUpdates}
                  onCheckedChange={(checked) => setNotifications({ ...notifications, communityUpdates: checked })}
                />
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="weekly-report">Weekly Progress Report</Label>
                  <p className="text-sm text-muted-foreground">Receive weekly summary of your progress</p>
                </div>
                <Switch
                  id="weekly-report"
                  checked={notifications.weeklyReport}
                  onCheckedChange={(checked) => setNotifications({ ...notifications, weeklyReport: checked })}
                />
              </div>
            </CardContent>
          </Card>

          {/* Privacy & Data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Privacy & Data
              </CardTitle>
              <CardDescription>Manage your data and privacy preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  Data Privacy
                </h4>
                <p className="text-sm text-muted-foreground">
                  Your data is encrypted and secure. We never share your personal information with third parties.
                </p>
              </div>
              
              <div className="flex gap-2">
                <Button variant="outline">Download My Data</Button>
                <Button variant="outline">Privacy Policy</Button>
              </div>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="w-5 h-5" />
                Danger Zone
              </CardTitle>
              <CardDescription>Irreversible actions for your account</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Deactivate Account */}
              <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
                <h4 className="mb-2">Deactivate Account</h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Temporarily disable your account. You can reactivate it anytime by logging back in.
                </p>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline">Deactivate Account</Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Deactivate your account?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Your account will be temporarily disabled. Your data will be preserved and you can reactivate anytime by logging in.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleDeactivateAccount}>
                        Deactivate
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>

              {/* Delete Account */}
              <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
                <h4 className="mb-2 text-red-600">Delete Account Permanently</h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Permanently delete your account and all associated data. This action cannot be undone.
                </p>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" className="gap-2">
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete your account and remove all your data from our servers including:
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          <li>All test results and progress</li>
                          <li>Purchase history</li>
                          <li>Community posts and comments</li>
                          <li>Personal information</li>
                        </ul>
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction 
                        onClick={handleDeleteAccount}
                        className="bg-red-600 hover:bg-red-700"
                      >
                        Yes, Delete My Account
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
