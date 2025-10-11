import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Header from './Header';
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
  Calendar,
  CheckCircle2
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
  Cell,
  Legend
} from 'recharts';

interface TestResultDashboardProps {
  user: any;
}

export default function TestResultDashboard({ user }: TestResultDashboardProps) {
  const location = useLocation();
  const [results, setResults] = useState<any[]>([]);
  const { purchaseSuccess, latestResult } = location.state || {};

  useEffect(() => {
    // Load results from localStorage
    const storedResults = JSON.parse(localStorage.getItem('jishu_results') || '[]');
    setResults(storedResults.filter((r: any) => r.userId === user.id));
  }, [user.id]);

  // Mock data for charts
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

  const mockTests = [
    { id: 1, name: 'Physics Mock Test 1', subject: 'Physics', questions: 30, duration: 60, difficulty: 'Medium' },
    { id: 2, name: 'Chemistry Full Test', subject: 'Chemistry', questions: 40, duration: 90, difficulty: 'Hard' },
    { id: 3, name: 'Biology Chapter 1-5', subject: 'Biology', questions: 25, duration: 45, difficulty: 'Easy' },
    { id: 4, name: 'Mathematics Advanced', subject: 'Maths', questions: 35, duration: 75, difficulty: 'Hard' },
  ];

  const averageScore = results.length > 0 
    ? Math.round(results.reduce((acc, r) => acc + (r.score / r.totalQuestions * 100), 0) / results.length)
    : 0;
  
  const totalTests = results.length;
  const totalTimeSpent = results.reduce((acc, r) => acc + (r.timeSpent || 0), 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Success Message */}
        {purchaseSuccess && (
          <Card className="mb-8 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-6 flex items-center gap-4">
              <CheckCircle2 className="w-12 h-12 text-green-600" />
              <div>
                <h3 className="text-xl text-green-900 mb-1">Purchase Successful! 🎉</h3>
                <p className="text-green-700">Your mock tests are now available. Start practicing below!</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Latest Result */}
        {latestResult && (
          <Card className="mb-8 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
            <CardContent className="p-8">
              <div className="text-center space-y-4">
                <Trophy className="w-16 h-16 text-yellow-500 mx-auto" />
                <h2 className="text-3xl">Test Completed!</h2>
                <div className="text-6xl">
                  {Math.round((latestResult.score / latestResult.totalQuestions) * 100)}%
                </div>
                <p className="text-xl text-gray-600">
                  You scored {latestResult.score} out of {latestResult.totalQuestions} questions
                </p>
                <Button size="lg">View Detailed Analysis</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="tests">Available Tests</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Average Score</span>
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="text-3xl mb-1">{averageScore}%</div>
                  <Progress value={averageScore} className="h-2" />
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Tests Taken</span>
                    <Target className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-3xl mb-1">{totalTests}</div>
                  <p className="text-xs text-gray-500">+3 this week</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Study Time</span>
                    <Clock className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="text-3xl mb-1">{Math.round(totalTimeSpent / 60)}m</div>
                  <p className="text-xs text-gray-500">Total time spent</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Rank</span>
                    <Award className="w-5 h-5 text-yellow-600" />
                  </div>
                  <div className="text-3xl mb-1">#342</div>
                  <p className="text-xs text-gray-500">Out of 10,540 students</p>
                </CardContent>
              </Card>
            </div>

            {/* Performance Overview */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="score" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        dot={{ fill: '#3b82f6', r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Subject-wise Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={subjectWiseData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="subject" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="score" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Recent Tests */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Test Results</CardTitle>
              </CardHeader>
              <CardContent>
                {results.length === 0 ? (
                  <div className="text-center py-12">
                    <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl text-gray-600 mb-2">No tests taken yet</h3>
                    <p className="text-gray-500 mb-4">Start taking mock tests to track your progress</p>
                    <Link to="/courses">
                      <Button>Browse Tests</Button>
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.slice(0, 5).map((result, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-4">
                          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                            (result.score / result.totalQuestions * 100) >= 75 ? 'bg-green-100 text-green-600' :
                            (result.score / result.totalQuestions * 100) >= 50 ? 'bg-yellow-100 text-yellow-600' :
                            'bg-red-100 text-red-600'
                          }`}>
                            {Math.round((result.score / result.totalQuestions) * 100)}%
                          </div>
                          <div>
                            <h4>Mock Test #{result.testId}</h4>
                            <p className="text-sm text-gray-600">
                              {result.score}/{result.totalQuestions} correct
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600">
                            {new Date(result.timestamp).toLocaleDateString()}
                          </p>
                          <Button variant="ghost" size="sm">View Details</Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Answer Accuracy</CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={accuracyData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {accuracyData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Strengths & Weaknesses</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm">Physics</span>
                      <span className="text-sm">80%</span>
                    </div>
                    <Progress value={80} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm">Chemistry</span>
                      <span className="text-sm">75%</span>
                    </div>
                    <Progress value={75} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm">Biology</span>
                      <span className="text-sm">85%</span>
                    </div>
                    <Progress value={85} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm">Mathematics</span>
                      <span className="text-sm">78%</span>
                    </div>
                    <Progress value={78} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Detailed Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <h4 className="flex items-center gap-2 text-green-600">
                      <TrendingUp className="w-5 h-5" />
                      Strong Areas
                    </h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• Organic Chemistry</li>
                      <li>• Cell Biology</li>
                      <li>• Calculus</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="flex items-center gap-2 text-red-600">
                      <Target className="w-5 h-5" />
                      Needs Improvement
                    </h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• Thermodynamics</li>
                      <li>• Genetics</li>
                      <li>• Trigonometry</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="flex items-center gap-2 text-blue-600">
                      <Award className="w-5 h-5" />
                      Achievements
                    </h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• 7-day streak 🔥</li>
                      <li>• Top 5% scorer</li>
                      <li>• 50 tests completed</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Available Tests Tab */}
          <TabsContent value="tests" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
              {mockTests.map((test) => (
                <Card key={test.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg mb-1">{test.name}</h3>
                        <Badge variant="secondary">{test.subject}</Badge>
                      </div>
                      <Badge variant={
                        test.difficulty === 'Easy' ? 'default' :
                        test.difficulty === 'Medium' ? 'secondary' :
                        'destructive'
                      }>
                        {test.difficulty}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                      <span className="flex items-center gap-1">
                        <BarChart3 className="w-4 h-4" />
                        {test.questions} Questions
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {test.duration} mins
                      </span>
                    </div>
                    <Link to={`/test/${test.id}`}>
                      <Button className="w-full">
                        <Play className="w-4 h-4 mr-2" />
                        Start Test
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
