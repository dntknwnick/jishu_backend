import { useState } from 'react';
import Header from './Header';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  User, 
  Mail, 
  Phone, 
  Calendar,
  MapPin,
  School,
  Award,
  BookOpen,
  Target,
  Trophy,
  Edit2,
  Save,
  X
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface UserProfileProps {
  user: any;
  onUpdateUser: (user: any) => void;
}

export default function UserProfile({ user, onUpdateUser }: UserProfileProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '+91 98765 43210',
    dateOfBirth: '2005-03-15',
    city: 'Mumbai',
    state: 'Maharashtra',
    school: 'ABC Senior Secondary School',
    targetExam: 'NEET 2025',
    targetScore: '650+'
  });

  const stats = [
    { label: 'Tests Taken', value: '47', icon: <BookOpen className="w-5 h-5 text-blue-600" /> },
    { label: 'Average Score', value: '82%', icon: <Target className="w-5 h-5 text-green-600" /> },
    { label: 'Rank', value: '#342', icon: <Trophy className="w-5 h-5 text-yellow-600" /> },
    { label: 'Study Streak', value: '12 days', icon: <Award className="w-5 h-5 text-purple-600" /> },
  ];

  const purchases = [
    { id: 1, course: 'NEET Physics Bundle', date: '2025-01-15', amount: 499, status: 'Active' },
    { id: 2, course: 'NEET Chemistry Bundle', date: '2025-01-20', amount: 499, status: 'Active' },
    { id: 3, course: 'NEET Biology Bundle', date: '2025-02-01', amount: 499, status: 'Active' },
  ];

  const achievements = [
    { title: 'First Test Completed', icon: '🎯', date: 'Jan 10, 2025' },
    { title: 'Week Streak Master', icon: '🔥', date: 'Jan 20, 2025' },
    { title: 'Top 1% Scorer', icon: '🏆', date: 'Feb 5, 2025' },
    { title: 'Community Contributor', icon: '💬', date: 'Feb 8, 2025' },
  ];

  const handleSave = () => {
    const updatedUser = {
      ...user,
      name: formData.name,
      email: formData.email
    };
    onUpdateUser(updatedUser);
    localStorage.setItem('jishu_user', JSON.stringify(updatedUser));
    setIsEditing(false);
    toast.success('Profile updated successfully!');
  };

  const handleCancel = () => {
    setFormData({
      ...formData,
      name: user?.name || '',
      email: user?.email || ''
    });
    setIsEditing(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Profile Card */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardContent className="p-6 text-center space-y-4">
                <Avatar className="w-32 h-32 mx-auto">
                  <AvatarImage src={user?.avatar} alt={user?.name} />
                  <AvatarFallback className="text-3xl">{user?.name?.charAt(0)}</AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-2xl mb-1">{user?.name}</h2>
                  <p className="text-muted-foreground">{formData.targetExam} Aspirant</p>
                  <Badge className="mt-2">Premium Member</Badge>
                </div>
                <Separator />
                <div className="space-y-2 text-sm text-left">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Mail className="w-4 h-4" />
                    <span>{user?.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Phone className="w-4 h-4" />
                    <span>{formData.phone}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <MapPin className="w-4 h-4" />
                    <span>{formData.city}, {formData.state}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    <span>Member since Jan 2025</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats Card */}
            <Card>
              <CardHeader>
                <CardTitle>Your Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats.map((stat, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        {stat.icon}
                      </div>
                      <span className="text-sm text-muted-foreground">{stat.label}</span>
                    </div>
                    <span>{stat.value}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Achievements */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Achievements</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {achievements.slice(0, 3).map((achievement, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className="text-2xl">{achievement.icon}</span>
                    <div className="flex-1">
                      <h4 className="text-sm">{achievement.title}</h4>
                      <p className="text-xs text-muted-foreground">{achievement.date}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Personal Information</CardTitle>
                  {!isEditing ? (
                    <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit Profile
                    </Button>
                  ) : (
                    <div className="flex gap-2">
                      <Button onClick={handleSave} size="sm">
                        <Save className="w-4 h-4 mr-2" />
                        Save
                      </Button>
                      <Button onClick={handleCancel} variant="outline" size="sm">
                        <X className="w-4 h-4 mr-2" />
                        Cancel
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth</Label>
                    <Input
                      id="dob"
                      type="date"
                      value={formData.dateOfBirth}
                      onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State</Label>
                    <Input
                      id="state"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Academic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Academic Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="school">School/College</Label>
                    <Input
                      id="school"
                      value={formData.school}
                      onChange={(e) => setFormData({ ...formData, school: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="targetExam">Target Exam</Label>
                    <Input
                      id="targetExam"
                      value={formData.targetExam}
                      onChange={(e) => setFormData({ ...formData, targetExam: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="targetScore">Target Score</Label>
                    <Input
                      id="targetScore"
                      value={formData.targetScore}
                      onChange={(e) => setFormData({ ...formData, targetScore: e.target.value })}
                      disabled={!isEditing}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Purchase History */}
            <Card>
              <CardHeader>
                <CardTitle>Purchase History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {purchases.map((purchase) => (
                    <div key={purchase.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                          <BookOpen className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <h4>{purchase.course}</h4>
                          <p className="text-sm text-muted-foreground">{purchase.date}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="mb-1">₹{purchase.amount}</p>
                        <Badge variant="secondary">{purchase.status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* All Achievements */}
            <Card>
              <CardHeader>
                <CardTitle>All Achievements</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-3">
                  {achievements.map((achievement, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                      <span className="text-3xl">{achievement.icon}</span>
                      <div>
                        <h4>{achievement.title}</h4>
                        <p className="text-xs text-muted-foreground">{achievement.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
