import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { userTestsApi } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import {
  Trophy,
  Target,
  Clock,
  Play,
  RotateCcw,
  CheckCircle2,
  Loader2,
  Brain,
  BookOpen,
  AlertCircle,
  Lock
} from 'lucide-react';

interface TestCard {
  id: number;
  purchase_id: number;
  test_number: number;
  max_attempts: number;
  attempts_used: number;
  remaining_attempts: number;
  questions_generated: boolean;
  latest_score: number;
  latest_percentage: number;
  latest_attempt_date: string | null;
  status: 'available' | 'in_progress' | 'completed' | 'disabled';
  is_available: boolean;
}

interface SubjectTestCards {
  subject_id: number;
  subject_name: string;
  course_name: string;
  total_cards: number;
  available_cards: number;
  completed_cards: number;
  disabled_cards: number;
  cards: TestCard[];
}

interface TestCardDashboardProps {
  user: any;
}

export default function TestCardDashboard({ user }: TestCardDashboardProps) {
  const navigate = useNavigate();
  const [testCardsBySubject, setTestCardsBySubject] = useState<SubjectTestCards[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState<number | null>(null);
  const [isStartingTest, setIsStartingTest] = useState(false);
  const [startingTestId, setStartingTestId] = useState<number | null>(null);

  useEffect(() => {
    loadTestCards();
  }, [user.id]);

  const loadTestCards = async () => {
    setIsLoading(true);
    try {
      const response = await userTestsApi.getTestCards();
      setTestCardsBySubject(response.data?.test_cards_by_subject || []);
    } catch (error) {
      console.error('Failed to load test cards:', error);
      toast.error('Failed to load test cards');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartTest = async (testCard: TestCard) => {
    setIsStartingTest(true);
    setStartingTestId(testCard.id);
    
    try {
      const response = await userTestsApi.startTestCard(testCard.id);
      
      // Navigate to test screen with session info
      navigate('/test', {
        state: {
          sessionId: response.data.session_id,
          mockTestId: response.data.mock_test_id,
          attemptNumber: response.data.attempt_number,
          remainingAttempts: response.data.remaining_attempts,
          questionsGenerated: response.data.questions_generated,
          testNumber: testCard.test_number,
          subjectName: testCardsBySubject.find(s => 
            s.cards.some(c => c.id === testCard.id)
          )?.subject_name
        }
      });
    } catch (error) {
      console.error('Failed to start test:', error);
      toast.error('Failed to start test');
    } finally {
      setIsStartingTest(false);
      setStartingTestId(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'disabled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return <Play className="w-4 h-4" />;
      case 'in_progress': return <Clock className="w-4 h-4" />;
      case 'completed': return <CheckCircle2 className="w-4 h-4" />;
      case 'disabled': return <Lock className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never attempted';
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
            <p>Loading your test cards...</p>
          </div>
        </div>
      </div>
    );
  }

  if (testCardsBySubject.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl text-gray-600 mb-2">No test cards available</h3>
            <p className="text-gray-500 mb-4">Purchase a course to get access to 50 test cards per subject</p>
            <Link to="/courses">
              <Button>Browse Courses</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Test Card Dashboard</h1>
          <p className="text-gray-600">
            Access your test cards with up to 3 attempts each. Latest attempt scores count for analytics.
          </p>
        </div>

        <Tabs defaultValue="all" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="all">All Subjects</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-6">
            {testCardsBySubject.map((subject) => (
              <Card key={subject.subject_id} className="overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">{subject.subject_name}</CardTitle>
                      <p className="text-sm text-gray-600">{subject.course_name}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {subject.completed_cards}/{subject.total_cards}
                      </div>
                      <p className="text-sm text-gray-600">Tests Completed</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-600">{subject.available_cards}</div>
                      <p className="text-xs text-gray-600">Available</p>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-blue-600">{subject.completed_cards}</div>
                      <p className="text-xs text-gray-600">Completed</p>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-red-600">{subject.disabled_cards}</div>
                      <p className="text-xs text-gray-600">Disabled</p>
                    </div>
                  </div>
                  
                  <Progress 
                    value={(subject.completed_cards / subject.total_cards) * 100} 
                    className="mt-4"
                  />
                </CardHeader>

                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {subject.cards.map((card) => (
                      <Card 
                        key={card.id} 
                        className={`relative transition-all duration-200 hover:shadow-md ${
                          card.is_available ? 'cursor-pointer' : 'opacity-60'
                        }`}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-3">
                            <div className="text-lg font-bold text-gray-900">
                              Test #{card.test_number}
                            </div>
                            <Badge className={getStatusColor(card.status)}>
                              <div className="flex items-center gap-1">
                                {getStatusIcon(card.status)}
                                <span className="capitalize">{card.status}</span>
                              </div>
                            </Badge>
                          </div>

                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Attempts:</span>
                              <span className="font-medium">
                                {card.attempts_used}/{card.max_attempts}
                              </span>
                            </div>
                            
                            {card.latest_score > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Latest Score:</span>
                                <span className="font-medium text-blue-600">
                                  {card.latest_score}/50 ({card.latest_percentage}%)
                                </span>
                              </div>
                            )}
                            
                            <div className="flex justify-between">
                              <span className="text-gray-600">Last Attempt:</span>
                              <span className="font-medium text-xs">
                                {formatDate(card.latest_attempt_date)}
                              </span>
                            </div>
                          </div>

                          {card.is_available && (
                            <Button
                              onClick={() => handleStartTest(card)}
                              disabled={isStartingTest}
                              className="w-full mt-4"
                              size="sm"
                            >
                              {isStartingTest && startingTestId === card.id ? (
                                <>
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                  Starting...
                                </>
                              ) : (
                                <>
                                  {card.attempts_used > 0 ? (
                                    <>
                                      <RotateCcw className="w-4 h-4 mr-2" />
                                      Re-attempt ({card.remaining_attempts} left)
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
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>Performance Analytics</CardTitle>
                <p className="text-sm text-gray-600">
                  Analytics are based on your latest attempt scores only
                </p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Analytics feature coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
