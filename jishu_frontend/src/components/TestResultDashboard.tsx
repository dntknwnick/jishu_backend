import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import Header from './Header';
import { userTestsApi } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import {
  Trophy,
  TrendingUp,
  Target,
  Clock,
  Award,
  Play,
  BarChart3,
  CheckCircle2,
  Loader2,
  Brain,
  BookOpen
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface TestResultDashboardProps {
  user: any;
}

export default function TestResultDashboard({ user }: TestResultDashboardProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState<any[]>([]);
  const [availableTests, setAvailableTests] = useState<any[]>([]);
  const [isLoadingTests, setIsLoadingTests] = useState(false);
  const [isGeneratingTest, setIsGeneratingTest] = useState(false);
  const [generatingSubjectId, setGeneratingSubjectId] = useState<number | null>(null);
  const { purchaseSuccess, latestResult } = location.state || {};

  useEffect(() => {
    const storedResults = JSON.parse(localStorage.getItem('jishu_results') || '[]');
    setResults(storedResults.filter((r: any) => r.userId === user.id));
    loadAvailableTests();
  }, [user.id]);

  const loadAvailableTests = async () => {
    setIsLoadingTests(true);
    try {
      const response = await userTestsApi.getAvailableTests();
      setAvailableTests(response.data?.available_tests || []);

      // Show development mode indicator if using dev endpoint
      if (response.data?.dev_mode) {
        console.log('🔧 Development Mode: Using demo data for available tests');
      }
    } catch (error) {
      console.error('Failed to load available tests:', error);
    } finally {
      setIsLoadingTests(false);
    }
  };

  const handleStartTest = async (subjectId: number, purchaseId?: number) => {
    setIsGeneratingTest(true);
    setGeneratingSubjectId(subjectId);

    try {
      // First, start the test attempt
      const startResponse = await userTestsApi.startTest(subjectId, purchaseId);
      const testAttemptId = startResponse.data.test_attempt_id;

      // Then generate questions for this test attempt
      await userTestsApi.generateTestQuestions(testAttemptId);

      // Navigate to the test screen only after successful generation
      navigate(`/test/${subjectId}${purchaseId ? `?purchase_id=${purchaseId}` : ''}`);
    } catch (error) {
      console.error('Failed to start test:', error);
      toast.error('Failed to generate test questions. Please try again.');
    } finally {
      setIsGeneratingTest(false);
      setGeneratingSubjectId(null);
    }
  };

  const performanceData = [
    { date: 'Week 1', score: 65 },
    { date: 'Week 2', score: 70 },
    { date: 'Week 3', score: 75 },
    { date: 'Week 4', score: 80 },
    { date: 'Week 5', score: 82 },
    { date: 'Week 6', score: 85 },
  ];

  const subjectWiseData = [
    { subject: 'Physics', score: 80 },
    { subject: 'Chemistry', score: 75 },
    { subject: 'Biology', score: 85 },
    { subject: 'Maths', score: 78 },
  ];

  const accuracyData = [
    { name: 'Correct', value: 75, color: '#10b981' },
    { name: 'Incorrect', value: 15, color: '#ef4444' },
    { name: 'Unattempted', value: 10, color: '#6b7280' },
  ];

  const averageScore =
    results.length > 0
      ? Math.round(
          results.reduce((acc, r) => acc + (r.score / r.totalQuestions) * 100, 0) /
            results.length
        )
      : 0;

  const totalTests = results.length;
  const totalTimeSpent = results.reduce((acc, r) => acc + (r.timeSpent || 0), 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        {purchaseSuccess && (
          <Card className="mb-8 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-6 flex items-center gap-4">
              <CheckCircle2 className="w-12 h-12 text-green-600" />
              <div>
                <h3 className="text-xl text-green-900 mb-1">Purchase Successful! 🎉</h3>
                <p className="text-green-700">
                  Your mock tests are now available. Start practicing below!
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {latestResult && (
          <Card className="mb-8 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
            <CardContent className="p-8 text-center space-y-4">
              <Trophy className="w-16 h-16 text-yellow-500 mx-auto" />
              <h2 className="text-3xl">Test Completed!</h2>
              <div className="text-6xl">
                {Math.round((latestResult.score / latestResult.totalQuestions) * 100)}%
              </div>
              <p className="text-xl text-gray-600">
                You scored {latestResult.score} out of {latestResult.totalQuestions} questions
              </p>
              <Button size="lg">View Detailed Analysis</Button>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="tests">Available Tests</TabsTrigger>
          </TabsList>

          {/* ✅ Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* (overview content unchanged — keep your existing code) */}
          </TabsContent>

          {/* ✅ Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            {/* (analytics content unchanged — keep your existing code) */}
          </TabsContent>

          {/* ✅ Available Tests Tab */}
          <TabsContent value="tests" className="space-y-6">
            {isGeneratingTest && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <div>
                    <p className="font-medium text-blue-900">Generating Test Questions</p>
                    <p className="text-sm text-blue-700">Please wait while we prepare your test using AI...</p>
                  </div>
                </div>
              </div>
            )}
            {isLoadingTests ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p>Loading available tests...</p>
              </div>
            ) : availableTests.length === 0 ? (
              <div className="text-center py-12">
                <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl text-gray-600 mb-2">No tests available</h3>
                <p className="text-gray-500 mb-4">Purchase a course to access mock tests</p>
                <Link to="/courses">
                  <Button>Browse Courses</Button>
                </Link>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {availableTests.map((test) => (
                  <Card
                    key={`${test.subject_id}-${test.purchase_id}`}
                    className="hover:shadow-lg transition-shadow"
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg mb-1">{test.subject_name}</h3>
                          <Badge variant="secondary">{test.course_name}</Badge>
                        </div>
                        <Badge
                          variant={
                            test.purchase_type === 'full_course' ? 'default' : 'secondary'
                          }
                        >
                          {test.purchase_type === 'full_course'
                            ? 'Full Course'
                            : 'Individual'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                        <span className="flex items-center gap-1">
                          <Target className="w-4 h-4" />
                          {test.available_tests} Available
                        </span>
                        <span className="flex items-center gap-1">
                          <BarChart3 className="w-4 h-4" />
                          {test.total_mock_tests} Total
                        </span>
                      </div>
                      <div className="mb-4">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Tests Used</span>
                          <span>
                            {test.mock_tests_used}/{test.total_mock_tests}
                          </span>
                        </div>
                        <Progress
                          value={(test.mock_tests_used / test.total_mock_tests) * 100}
                          className="h-2"
                        />
                      </div>
                      {test.purchase_type === 'full_course' ? (
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600 mb-2">Choose a subject:</p>
                          {test.subjects?.map((subject: any, index: number) => (
                            <Button
                              key={index}
                              className="w-full mb-1"
                              variant="outline"
                              disabled={test.available_tests <= 0 || isGeneratingTest}
                              onClick={() => handleStartTest(subject.id, test.purchase_id)}
                            >
                              {isGeneratingTest && generatingSubjectId === subject.id ? (
                                <>
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                                  Generating Test...
                                </>
                              ) : (
                                <>
                                  <Play className="w-4 h-4 mr-2" />
                                  {subject.name}
                                </>
                              )}
                            </Button>
                          ))}
                        </div>
                      ) : (
                        <Button
                          className="w-full"
                          disabled={test.available_tests <= 0 || isGeneratingTest}
                          onClick={() => handleStartTest(test.subject_id, test.purchase_id)}
                        >
                          {isGeneratingTest && generatingSubjectId === test.subject_id ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                              Generating Test...
                            </>
                          ) : (
                            <>
                              <Play className="w-4 h-4 mr-2" />
                              {test.available_tests > 0
                                ? 'Start Test'
                                : 'No Tests Remaining'}
                            </>
                          )}
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
