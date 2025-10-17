import { useState, useEffect } from 'react';
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
  X,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { profileApi } from '../services/api';

interface ProfileData {
  user: any;
  stats: any;
  academics: any;
  purchases: any[];
}

export default function ProfilePage({ user: initialUser, onUpdateUser }: any) {
  const [profileData, setProfileData] = useState<ProfileData>({
    user: initialUser || {},
    stats: {},
    academics: {},
    purchases: []
  });

  const [loading, setLoading] = useState(true);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    // Personal info
    name: '',
    mobile_no: '',
    avatar: '',
    address: '',
    gender: '',
    date_of_birth: '',
    city: '',
    state: '',
    // Academic info
    school_college: '',
    grade_year: '',
    board_university: '',
    current_exam_target: ''
  });

  const [saving, setSaving] = useState(false);

  // Load all profile data
  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      const [profileRes, statsRes, academicsRes, purchasesRes] = await Promise.all([
        profileApi.getProfile(),
        profileApi.getStats(),
        profileApi.getAcademics(),
        profileApi.getPurchases()
      ]);

      const newData: ProfileData = {
        user: profileRes.data?.user || {},
        stats: statsRes.data?.stats || {},
        academics: academicsRes.data?.academics || {},
        purchases: purchasesRes.data?.purchases || []
      };

      setProfileData(newData);
      setFormData({
        name: newData.user.name || '',
        mobile_no: newData.user.mobile_no || '',
        avatar: newData.user.avatar || '',
        address: newData.user.address || '',
        gender: newData.user.gender || '',
        date_of_birth: newData.user.date_of_birth || '',
        city: newData.user.city || '',
        state: newData.user.state || '',
        school_college: newData.academics.school_college || '',
        grade_year: newData.academics.grade_year || '',
        board_university: newData.academics.board_university || '',
        current_exam_target: newData.academics.current_exam_target || ''
      });
    } catch (error) {
      console.error('Failed to load profile data:', error);
      toast.error('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePersonalInfo = async () => {
    try {
      setSaving(true);
      const updateData = {
        name: formData.name,
        mobile_no: formData.mobile_no,
        avatar: formData.avatar,
        address: formData.address,
        gender: formData.gender,
        date_of_birth: formData.date_of_birth,
        city: formData.city,
        state: formData.state
      };

      const response = await profileApi.updateProfile(updateData);
      setProfileData(prev => ({
        ...prev,
        user: response.data?.user || prev.user
      }));
      setEditingSection(null);
      toast.success('Personal information updated successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to update personal information');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAcademics = async () => {
    try {
      setSaving(true);
      const updateData = {
        school_college: formData.school_college,
        grade_year: formData.grade_year,
        board_university: formData.board_university,
        current_exam_target: formData.current_exam_target
      };

      const response = await profileApi.updateAcademics(updateData);
      setProfileData(prev => ({
        ...prev,
        academics: response.data?.academics || prev.academics
      }));
      setEditingSection(null);
      toast.success('Academic information updated successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to update academic information');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingSection(null);
    setFormData({
      name: profileData.user.name || '',
      mobile_no: profileData.user.mobile_no || '',
      avatar: profileData.user.avatar || '',
      address: profileData.user.address || '',
      gender: profileData.user.gender || '',
      date_of_birth: profileData.user.date_of_birth || '',
      city: profileData.user.city || '',
      state: profileData.user.state || '',
      school_college: profileData.academics.school_college || '',
      grade_year: profileData.academics.grade_year || '',
      board_university: profileData.academics.board_university || '',
      current_exam_target: profileData.academics.current_exam_target || ''
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={profileData.user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Profile Card & Stats */}
          <div className="lg:col-span-1 space-y-6">
            {/* Profile Card */}
            <Card>
              <CardContent className="p-6 text-center space-y-4">
                <Avatar className="w-32 h-32 mx-auto">
                  <AvatarImage src={profileData.user.avatar} alt={profileData.user.name} />
                  <AvatarFallback className="text-3xl">{profileData.user.name?.charAt(0)}</AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-2xl font-bold mb-1">{profileData.user.name}</h2>
                  <p className="text-muted-foreground">{profileData.academics.current_exam_target || 'Exam Aspirant'}</p>
                  {profileData.user.is_premium && <Badge className="mt-2">Premium Member</Badge>}
                </div>
                <Separator />
                <div className="space-y-2 text-sm text-left">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Mail className="w-4 h-4" />
                    <span>{profileData.user.email_id}</span>
                  </div>
                  {profileData.user.mobile_no && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Phone className="w-4 h-4" />
                      <span>{profileData.user.mobile_no}</span>
                    </div>
                  )}
                  {profileData.user.city && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <MapPin className="w-4 h-4" />
                      <span>{profileData.user.city}, {profileData.user.state}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    <span>Member since {new Date(profileData.user.created_at).toLocaleDateString()}</span>
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
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <BookOpen className="w-5 h-5 text-blue-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">Tests Taken</span>
                  </div>
                  <span className="font-semibold">{profileData.stats.total_tests_taken || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <Target className="w-5 h-5 text-green-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">Avg Score</span>
                  </div>
                  <span className="font-semibold">{profileData.stats.average_score?.toFixed(2) || 0}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                      <Trophy className="w-5 h-5 text-yellow-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">Highest Score</span>
                  </div>
                  <span className="font-semibold">{profileData.stats.highest_score || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Award className="w-5 h-5 text-purple-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">Current Streak</span>
                  </div>
                  <span className="font-semibold">{profileData.stats.current_streak || 0} days</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Editable Sections */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Personal Information</CardTitle>
                  {editingSection !== 'personal' ? (
                    <Button onClick={() => setEditingSection('personal')} variant="outline" size="sm">
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit
                    </Button>
                  ) : (
                    <div className="flex gap-2">
                      <Button onClick={handleSavePersonalInfo} size="sm" disabled={saving}>
                        {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                        Save
                      </Button>
                      <Button onClick={handleCancel} variant="outline" size="sm" disabled={saving}>
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
                      disabled={editingSection !== 'personal'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileData.user.email_id}
                      disabled
                      className="bg-gray-100"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={formData.mobile_no}
                      onChange={(e) => setFormData({ ...formData, mobile_no: e.target.value })}
                      disabled={editingSection !== 'personal'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth</Label>
                    <Input
                      id="dob"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                      disabled={editingSection !== 'personal'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="gender">Gender</Label>
                    <select
                      id="gender"
                      value={formData.gender}
                      onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                      disabled={editingSection !== 'personal'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md disabled:bg-gray-100"
                    >
                      <option value="">Select Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      disabled={editingSection !== 'personal'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State</Label>
                    <Input
                      id="state"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      disabled={editingSection !== 'personal'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="address">Address</Label>
                    <Input
                      id="address"
                      value={formData.address}
                      onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                      disabled={editingSection !== 'personal'}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Academic Information */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Academic Information</CardTitle>
                  {editingSection !== 'academic' ? (
                    <Button onClick={() => setEditingSection('academic')} variant="outline" size="sm">
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit
                    </Button>
                  ) : (
                    <div className="flex gap-2">
                      <Button onClick={handleSaveAcademics} size="sm" disabled={saving}>
                        {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                        Save
                      </Button>
                      <Button onClick={handleCancel} variant="outline" size="sm" disabled={saving}>
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
                    <Label htmlFor="school">School/College</Label>
                    <Input
                      id="school"
                      value={formData.school_college}
                      onChange={(e) => setFormData({ ...formData, school_college: e.target.value })}
                      disabled={editingSection !== 'academic'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="grade">Grade/Year</Label>
                    <Input
                      id="grade"
                      value={formData.grade_year}
                      onChange={(e) => setFormData({ ...formData, grade_year: e.target.value })}
                      disabled={editingSection !== 'academic'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="board">Board/University</Label>
                    <Input
                      id="board"
                      value={formData.board_university}
                      onChange={(e) => setFormData({ ...formData, board_university: e.target.value })}
                      disabled={editingSection !== 'academic'}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="target">Target Exam</Label>
                    <Input
                      id="target"
                      value={formData.current_exam_target}
                      onChange={(e) => setFormData({ ...formData, current_exam_target: e.target.value })}
                      disabled={editingSection !== 'academic'}
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
                {profileData.purchases.length > 0 ? (
                  <div className="space-y-3">
                    {profileData.purchases.map((purchase) => (
                      <div key={purchase.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <BookOpen className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <h4 className="font-semibold">{purchase.course_name || 'Course'}</h4>
                            <p className="text-sm text-muted-foreground">{new Date(purchase.purchase_date).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">₹{purchase.amount}</p>
                          <Badge variant={purchase.status === 'active' ? 'default' : 'secondary'}>{purchase.status}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">No purchases yet</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

