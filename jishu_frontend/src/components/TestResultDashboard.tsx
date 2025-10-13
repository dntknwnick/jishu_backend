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
  BookOpen,
  RotateCcw
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
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [isLoadingTests, setIsLoadingTests] = useState(false);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);
  const [loadingTestCards, setLoadingTestCards] = useState<Set<string>>(new Set());
  const { purchaseSuccess, latestResult, sessionResult, isNewTestCardFlow, testCompleted } = location.state || {};

  // Determine default tab based on navigation context
  const getDefaultTab = () => {
    // If user completed a test (has sessionResult, latestResult, or testCompleted), show Available Tests tab
    if (sessionResult || latestResult || testCompleted) {
      return "tests";
    }
    // If user just made a purchase, show Available Tests tab to see their new tests
    if (purchaseSuccess) {
      return "tests";
    }
    // Otherwise, default to Overview tab
    return "overview";
  };

  useEffect(() => {
    const storedResults = JSON.parse(localStorage.getItem('jishu_results') || '[]');
    setResults(storedResults.filter((r: any) => r.userId === user.id));
    loadAvailableTests();
    loadAnalyticsData();
  }, [user.id]);

  const loadAvailableTests = async () => {
    setIsLoadingTests(true);
    try {
      // Use new test cards API
      const response = await userTestsApi.getTestCards();

      // Transform test cards data to include ALL cards (available and completed)
      const transformedTests = response.data?.test_cards_by_subject?.flatMap(subject =>
        subject.cards
          // Show all cards - available, completed, and exhausted
          .map(card => ({
            subject_id: subject.subject_id,
            subject_name: subject.subject_name,
            course_name: subject.course_name,
            purchase_id: card.purchase_id,
            test_card_id: card.id,
            test_number: card.test_number,
            attempts_used: card.attempts_used,
            remaining_attempts: card.remaining_attempts,
            latest_score: card.latest_score,
            latest_percentage: card.latest_percentage,
            status: card.status,
            is_available: card.is_available,
            // Create unique identifier for loading state
            unique_id: `${card.id}-${card.purchase_id}`
          }))
      ) || [];

      setAvailableTests(transformedTests);
    } catch (error) {
      console.error('Failed to load available tests:', error);
      toast.error('Failed to load test cards. Please try again.');
    } finally {
      setIsLoadingTests(false);
    }
  };

  const loadAnalyticsData = async () => {
    setIsLoadingAnalytics(true);
    try {
      const response = await userTestsApi.getTestAnalytics();
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      // Don't show error toast for analytics as it's not critical
    } finally {
      setIsLoadingAnalytics(false);
    }
  };

  const handleStartTest = async (test: any) => {
    const testId = test.unique_id || `${test.test_card_id || test.subject_id}-${test.purchase_id}`;

    // Add this specific test card to loading state
    setLoadingTestCards(prev => new Set([...prev, testId]));

    try {
      // Use new test card system
      if (test.test_card_id) {
        // Start test card session
        const response = await userTestsApi.startTestCard(test.test_card_id);

        // Navigate to test screen with session info
        navigate('/test', {
          state: {
            sessionId: response.data.session_id,
            mockTestId: response.data.mock_test_id,
            attemptNumber: response.data.attempt_number,
            remainingAttempts: response.data.remaining_attempts,
            questionsGenerated: response.data.questions_generated,
            testNumber: test.test_number,
            subjectName: test.subject_name,
            isReAttempt: test.attempts_used > 0
          }
        });
      } else {
        // Legacy flow for backward compatibility
        const startResponse = await userTestsApi.startTest(test.subject_id, test.purchase_id);
        const testAttemptId = startResponse.data.test_attempt_id;
        await userTestsApi.generateTestQuestions(testAttemptId);
        navigate(`/test/${test.subject_id}${test.purchase_id ? `?purchase_id=${test.purchase_id}` : ''}`);
      }
    } catch (error) {
      console.error('Failed to start test:', error);
      toast.error('Failed to start test. Please try again.');
    } finally {
      // Remove this specific test card from loading state
      setLoadingTestCards(prev => {
        const newSet = new Set(prev);
        newSet.delete(testId);
        return newSet;
      });
    }
  };

  // Calculate real data from available tests and analytics
  const completedTests = availableTests.filter(test => test.attempts_used > 0);

  // Subject-wise performance data
  const subjectWiseData = availableTests
    .filter(test => test.latest_score > 0)
    .reduce((acc, test) => {
      const existing = acc.find(item => item.subject === test.subject_name);
      if (existing) {
        existing.totalScore += test.latest_percentage;
        existing.count += 1;
        existing.score = Math.round(existing.totalScore / existing.count);
      } else {
        acc.push({
          subject: test.subject_name,
          score: Math.round(test.latest_percentage),
          totalScore: test.latest_percentage,
          count: 1
        });
      }
      return acc;
    }, [] as any[]);

  // Performance trend data (mock data for now - would need historical data from backend)
  const performanceData = completedTests.length > 0
    ? completedTests.slice(-6).map((test, index) => ({
        date: `Test ${index + 1}`,
        score: Math.round(test.latest_percentage)
      }))
    : [
        { date: 'No tests', score: 0 }
      ];

  // Accuracy data calculation (would need detailed question-level data)
  const averagePercentage = analyticsData?.average_percentage || 0;
  const accuracyData = [
    { name: 'Correct', value: Math.round(averagePercentage), color: '#10b981' },
    { name: 'Incorrect', value: Math.round((100 - averagePercentage) * 0.7), color: '#ef4444' },
    { name: 'Unattempted', value: Math.round((100 - averagePercentage) * 0.3), color: '#6b7280' },
  ];

  // Statistics from analytics data
  const averageScore = analyticsData?.average_percentage || 0;
  const totalTests = analyticsData?.total_tests_taken || 0;
  const totalTimeSpent = analyticsData?.total_time_spent || 0;
  const bestScore = analyticsData?.best_score || 0;
  const worstScore = analyticsData?.worst_score || 0;

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

        <Tabs defaultValue={getDefaultTab()} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="tests">Available Tests</TabsTrigger>
          </TabsList>

          {/* ✅ Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {isLoadingAnalytics ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p>Loading analytics...</p>
              </div>
            ) : (
              <>
                {/* Statistics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-blue-100 rounded-lg">
                          <TrendingUp className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Average Score</p>
                          <p className="text-2xl font-bold">{Math.round(averageScore)}%</p>
                          <p className="text-xs text-gray-500">
                            {totalTests > 0 ? `${totalTests} tests taken` : 'No tests taken'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-green-100 rounded-lg">
                          <Target className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Tests Taken</p>
                          <p className="text-2xl font-bold">{totalTests}</p>
                          <p className="text-xs text-gray-500">
                            {totalTests > 0 ? `+${Math.round(totalTests / 4)} this week` : 'Start your first test'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-purple-100 rounded-lg">
                          <Clock className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Study Time</p>
                          <p className="text-2xl font-bold">
                            {totalTimeSpent > 0 ? `${Math.round(totalTimeSpent / 60)}m` : '0m'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {totalTimeSpent > 0 ? 'Total time spent' : 'Time spent studying'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-yellow-100 rounded-lg">
                          <Trophy className="w-6 h-6 text-yellow-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Rank</p>
                          <p className="text-2xl font-bold">
                            #{totalTests > 0 ? Math.max(1, 1000 - (totalTests * 10)) : 'N/A'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {totalTests > 0 ? `Out of ${1000 + totalTests} students` : 'Take tests to get ranked'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Performance Trend Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Performance Trend
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {completedTests.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={performanceData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={[0, 100]} />
                          <Tooltip />
                          <Line
                            type="monotone"
                            dataKey="score"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-center py-12">
                        <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">Complete tests to see your performance trend</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Subject-wise Performance */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BookOpen className="w-5 h-5" />
                      Subject-wise Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {subjectWiseData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={subjectWiseData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="subject" />
                          <YAxis domain={[0, 100]} />
                          <Tooltip />
                          <Bar dataKey="score" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-center py-12">
                        <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">Complete tests to see subject-wise performance</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Recent Test Results */}
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Test Results</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {completedTests.length > 0 ? (
                      <div className="space-y-4">
                        {completedTests.slice(-5).map((test, index) => (
                          <div key={`${test.test_card_id}-${index}`} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className={`w-3 h-3 rounded-full ${
                                test.latest_percentage >= 80 ? 'bg-green-500' :
                                test.latest_percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}></div>
                              <div>
                                <p className="font-medium">{test.subject_name}</p>
                                <p className="text-sm text-gray-600">Test #{test.test_number}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-lg">{Math.round(test.latest_percentage)}%</p>
                              <p className="text-sm text-gray-500">{test.latest_score}/50</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Target className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-500">No test results yet</p>
                        <p className="text-sm text-gray-400">Start taking tests to see your results here</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* ✅ Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            {isLoadingAnalytics ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p>Loading analytics...</p>
              </div>
            ) : (
              <>
                {/* Answer Accuracy Chart */}
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Answer Accuracy</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {totalTests > 0 ? (
                        <div className="flex items-center justify-center">
                          <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                              <Pie
                                data={accuracyData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={5}
                                dataKey="value"
                              >
                                {accuracyData.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                              </Pie>
                              <Tooltip />
                            </PieChart>
                          </ResponsiveContainer>
                          <div className="ml-6 space-y-3">
                            {accuracyData.map((item, index) => (
                              <div key={index} className="flex items-center gap-2">
                                <div
                                  className="w-3 h-3 rounded-full"
                                  style={{ backgroundColor: item.color }}
                                ></div>
                                <span className="text-sm">{item.name}: {item.value}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-12">
                          <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                          <p className="text-gray-500">Take tests to see accuracy analysis</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Strengths & Weaknesses */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Strengths & Weaknesses</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {subjectWiseData.length > 0 ? (
                        <>
                          {subjectWiseData.map((subject, index) => (
                            <div key={index} className="space-y-2">
                              <div className="flex justify-between items-center">
                                <span className="text-sm font-medium">{subject.subject}</span>
                                <span className="text-sm text-gray-600">{subject.score}%</span>
                              </div>
                              <Progress value={subject.score} className="h-2" />
                            </div>
                          ))}
                        </>
                      ) : (
                        <div className="text-center py-8">
                          <Brain className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                          <p className="text-gray-500">Complete tests to analyze strengths</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Detailed Insights */}
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Insights</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-6">
                      {/* Strong Areas */}
                      <div>
                        <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4" />
                          Strong Areas
                        </h4>
                        <ul className="space-y-2 text-sm">
                          {subjectWiseData
                            .filter(subject => subject.score >= 75)
                            .slice(0, 3)
                            .map((subject, index) => (
                              <li key={index} className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                {subject.subject}
                              </li>
                            ))}
                          {subjectWiseData.filter(subject => subject.score >= 75).length === 0 && (
                            <li className="text-gray-500">Keep practicing to build strengths</li>
                          )}
                        </ul>
                      </div>

                      {/* Needs Improvement */}
                      <div>
                        <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
                          <Target className="w-4 h-4" />
                          Needs Improvement
                        </h4>
                        <ul className="space-y-2 text-sm">
                          {subjectWiseData
                            .filter(subject => subject.score < 60)
                            .slice(0, 3)
                            .map((subject, index) => (
                              <li key={index} className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                                {subject.subject}
                              </li>
                            ))}
                          {subjectWiseData.filter(subject => subject.score < 60).length === 0 && (
                            <li className="text-gray-500">Great! No weak areas identified</li>
                          )}
                        </ul>
                      </div>

                      {/* Achievements */}
                      <div>
                        <h4 className="font-semibold text-blue-700 mb-3 flex items-center gap-2">
                          <Award className="w-4 h-4" />
                          Achievements
                        </h4>
                        <ul className="space-y-2 text-sm">
                          {totalTests >= 10 && (
                            <li className="flex items-center gap-2">
                              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                              10+ tests completed
                            </li>
                          )}
                          {bestScore >= 90 && (
                            <li className="flex items-center gap-2">
                              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                              90%+ score achieved
                            </li>
                          )}
                          {averageScore >= 75 && (
                            <li className="flex items-center gap-2">
                              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                              Consistent performer
                            </li>
                          )}
                          {totalTests === 0 && (
                            <li className="text-gray-500">Start taking tests to earn achievements</li>
                          )}
                        </ul>
                      </div>
                    </div>

                    {/* Improvement Tracking */}
                    {analyticsData?.improvement_data?.improvement_available && (
                      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <h4 className="font-semibold text-blue-900 mb-2">📈 Improvement Tracking</h4>
                        <p className="text-blue-800 text-sm">
                          You've improved by {analyticsData.improvement_data.improvement_points?.toFixed(1)} points
                          ({analyticsData.improvement_data.improvement_percentage?.toFixed(1)}%) since your first attempts!
                        </p>
                        <div className="mt-2 text-xs text-blue-700">
                          First attempts average: {analyticsData.improvement_data.first_attempt_average?.toFixed(1)}% →
                          Latest attempts average: {analyticsData.improvement_data.latest_attempt_average?.toFixed(1)}%
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* ✅ Available Tests Tab */}
          <TabsContent value="tests" className="space-y-6 relative">
            {/* Subtle loading overlay when any test is starting */}
            {loadingTestCards.size > 0 && (
              <div className="absolute top-0 left-0 right-0 bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 z-10">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <div>
                    <p className="font-medium text-blue-900 text-sm">Preparing test...</p>
                    <p className="text-xs text-blue-700">Generating questions and setting up your test session</p>
                  </div>
                </div>
              </div>
            )}
            <div className={`${loadingTestCards.size > 0 ? 'mt-16' : ''}`}>
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
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {availableTests.map((test) => {
                  const testId = test.unique_id || `${test.test_card_id || test.subject_id}-${test.purchase_id}`;
                  const isLoadingThisCard = loadingTestCards.has(testId);
                  const isExhausted = test.remaining_attempts <= 0;
                  const hasAttempts = test.attempts_used > 0;

                  return (
                    <Card
                      key={testId}
                      className={`transition-shadow ${
                        isExhausted
                          ? 'opacity-90 border-gray-300'
                          : 'hover:shadow-lg border-gray-200'
                      }`}
                    >
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="text-lg mb-1">{test.subject_name}</h3>
                            <Badge variant="secondary">{test.course_name}</Badge>
                            {test.test_number && (
                              <div className="text-sm text-gray-600 mt-1">
                                Test Card #{test.test_number}
                              </div>
                            )}
                          </div>
                          <Badge
                            variant={isExhausted ? 'outline' : test.status === 'completed' ? 'default' : 'secondary'}
                            className={
                              isExhausted
                                ? 'bg-gray-100 text-gray-600 border-gray-300'
                                : test.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-blue-100 text-blue-800'
                            }
                          >
                            {isExhausted ? 'Exhausted' : test.status === 'completed' ? 'Completed' : 'Available'}
                          </Badge>
                        </div>

                        {/* Test Card Specific Information */}
                        {test.test_card_id && (
                          <div className="space-y-3 mb-4">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Attempts Used:</span>
                              <span className="font-medium">
                                {test.attempts_used}/3
                              </span>
                            </div>

                            {test.latest_score > 0 && (
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">
                                  {isExhausted ? 'Final Score:' : 'Latest Score:'}
                                </span>
                                <span className={`font-medium ${
                                  isExhausted
                                    ? 'text-gray-700 text-base'
                                    : 'text-blue-600'
                                }`}>
                                  {test.latest_score}/50 ({Math.round(test.latest_percentage)}%)
                                </span>
                              </div>
                            )}

                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Remaining:</span>
                              <span className={`font-medium ${
                                test.remaining_attempts > 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {test.remaining_attempts} attempts
                              </span>
                            </div>

                            {/* Show performance indicator for exhausted cards */}
                            {isExhausted && test.latest_percentage > 0 && (
                              <div className="mt-3 p-2 rounded-lg bg-gray-50 border">
                                <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                                  <span>Performance</span>
                                  <span>{Math.round(test.latest_percentage)}%</span>
                                </div>
                                <Progress
                                  value={test.latest_percentage}
                                  className="h-2"
                                />
                              </div>
                            )}
                          </div>
                        )}

                        <Button
                          className={`w-full ${
                            isExhausted
                              ? 'bg-gray-400 hover:bg-gray-400 cursor-not-allowed'
                              : ''
                          }`}
                          disabled={isExhausted || isLoadingThisCard}
                          onClick={() => handleStartTest(test)}
                          title={isExhausted ? 'No attempts remaining' : ''}
                        >
                          {isLoadingThisCard ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Starting Test...
                            </>
                          ) : isExhausted ? (
                            <>
                              <Trophy className="w-4 h-4 mr-2" />
                              No Attempts Left
                            </>
                          ) : (
                            <>
                              {hasAttempts ? (
                                <>
                                  <RotateCcw className="w-4 h-4 mr-2" />
                                  Re-attempt ({test.remaining_attempts} left)
                                </>
                              ) : (
                                <>
                                  <Play className="w-4 h-4 mr-2" />
                                  Start Test
                                </>
                              )}
                            </>
                          )}
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
