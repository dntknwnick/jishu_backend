import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Stethoscope, Atom, Calculator, Beaker, Users, BookOpen, Trophy, Loader2 } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchCourses } from '../store/slices/coursesSlice';

interface CourseSelectionProps {
  user: any;
}

export default function CourseSelection({ user }: CourseSelectionProps) {
  const dispatch = useAppDispatch();
  const { courses, isLoading, error } = useAppSelector((state) => state.courses);

  useEffect(() => {
    dispatch(fetchCourses());
  }, [dispatch, user]);

  // Icon mapping for different course types
  const getIconForCourse = (courseName: string) => {
    const name = courseName.toLowerCase();
    if (name.includes('neet')) return <Stethoscope className="w-8 h-8" />;
    if (name.includes('jee') && name.includes('advanced')) return <Atom className="w-8 h-8" />;
    if (name.includes('jee')) return <Beaker className="w-8 h-8" />;
    if (name.includes('cet')) return <Calculator className="w-8 h-8" />;
    return <BookOpen className="w-8 h-8" />;
  };



  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading courses...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4">Error Loading Courses</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => dispatch(fetchCourses())}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl mb-2">Welcome back, {user?.name}! 👋</h1>
              <p className="text-xl text-gray-600">Choose your exam course to get started</p>
            </div>
            {user?.is_admin && (
              <div className="flex flex-col gap-2">
                <Link to="/admin/courses">
                  <Button variant="outline" className="gap-2">
                    <BookOpen className="w-4 h-4" />
                    Manage Courses (Admin)
                  </Button>
                </Link>
                <Link to="/admin">
                  <Button variant="outline" className="gap-2">
                    <Users className="w-4 h-4" />
                    Admin Dashboard
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl">{courses.length}</p>
                <p className="text-sm text-gray-600">Available Courses</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl">{courses.reduce((total, course) => total + (course.subjects?.length || 0), 0)}</p>
                <p className="text-sm text-gray-600">Total Subjects</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Trophy className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl">Expert</p>
                <p className="text-sm text-gray-600">Quality Content</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Course Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {courses.map((course, index) => {
            // Use the same color scheme system as admin interface
            const colorSchemes = [
              { header: 'from-pink-500 to-pink-600', icon: 'from-pink-500 to-pink-600', iconBg: 'bg-pink-100 text-pink-600' },
              { header: 'from-blue-500 to-blue-600', icon: 'from-blue-500 to-blue-600', iconBg: 'bg-blue-100 text-blue-600' },
              { header: 'from-purple-500 to-purple-600', icon: 'from-purple-500 to-purple-600', iconBg: 'bg-purple-100 text-purple-600' },
              { header: 'from-green-500 to-green-600', icon: 'from-green-500 to-green-600', iconBg: 'bg-green-100 text-green-600' },
              { header: 'from-orange-500 to-orange-600', icon: 'from-orange-500 to-orange-600', iconBg: 'bg-orange-100 text-orange-600' },
              { header: 'from-teal-500 to-teal-600', icon: 'from-teal-500 to-teal-600', iconBg: 'bg-teal-100 text-teal-600' }
            ];
            const colorScheme = colorSchemes[index % colorSchemes.length];
            const icon = getIconForCourse(course.course_name);
            const subjectCount = course.subjects?.length || 0;
            const testCount = course.subjects?.reduce((total, subject) => total + (subject.total_mock || 50), 0) || (subjectCount * 50);
            const studentCount = Math.floor(Math.random() * 20000) + 5000; // Mock student count

            return (
              <Card key={course.id} className="overflow-hidden hover:shadow-xl transition-all duration-300 group">
                {/* Colored Header */}
                <div className={`h-2 bg-gradient-to-r ${colorScheme.header}`}></div>

                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className={`w-16 h-16 ${colorScheme.iconBg} rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                      {icon}
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <span className="font-medium">{testCount}</span>
                      <span>Tests</span>
                    </div>
                  </div>

                  <div>
                    <CardTitle className="text-2xl mb-2">{course.course_name}</CardTitle>
                    <CardDescription className="text-gray-600 text-sm mb-3">{course.description}</CardDescription>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  {/* Subject Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {course.subjects && course.subjects.length > 0 ? (
                      course.subjects.slice(0, 3).map((subject) => (
                        <span key={subject.id} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                          {subject.subject_name}
                        </span>
                      ))
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md">
                        No subjects available
                      </span>
                    )}
                    {subjectCount > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md">
                        +{subjectCount - 3} more
                      </span>
                    )}
                  </div>

                  {/* Student Count */}
                  <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                    <Users className="w-4 h-4" />
                    <span>{studentCount.toLocaleString()} students</span>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <BookOpen className="w-4 h-4" />
                      <span>Comprehensive preparation</span>
                    </div>
                    <Link to={`/subjects/${course.id}`}>
                      <Button className={`bg-gradient-to-r ${colorScheme.icon} text-white hover:opacity-90 border-0`}>
                        Select Course
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Info Section */}
        <Card className="mt-8 bg-gradient-to-br from-blue-50 to-purple-50 border-none">
          <CardContent className="p-8">
            <h3 className="text-2xl mb-4">Why Choose Jishu App?</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <h4 className="mb-2">📚 Expert Content</h4>
                <p className="text-gray-600 text-sm">Questions crafted by subject matter experts and previous toppers</p>
              </div>
              <div>
                <h4 className="mb-2">📊 Detailed Analytics</h4>
                <p className="text-gray-600 text-sm">Track your progress with comprehensive performance insights</p>
              </div>
              <div>
                <h4 className="mb-2">🤖 AI Assistant</h4>
                <p className="text-gray-600 text-sm">Get instant doubt resolution with our intelligent chatbot</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
