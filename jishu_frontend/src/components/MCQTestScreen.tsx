import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Label } from './ui/label';
import {
  Clock,
  Flag,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  Loader2
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
} from './ui/alert-dialog';
import { toast } from 'sonner';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchQuestions, startTest, endTest, answerQuestion, toggleFlag, updateTimer, submitTest } from '../store/slices/testsSlice';
import { userTestsApi } from '../services/api';

interface MCQTestScreenProps {
  user: any;
}

// Mock questions removed - now using Redux state

export default function MCQTestScreen({ user }: MCQTestScreenProps) {
  const { testId } = useParams();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  // Get purchase_id from query parameters if present
  const urlParams = new URLSearchParams(window.location.search);
  const purchaseId = urlParams.get('purchase_id');

  const { questions, currentTest, isLoading, error } = useAppSelector((state) => state.tests);

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [showInstructions, setShowInstructions] = useState(true);
  const [autoSubmit, setAutoSubmit] = useState(false);

  useEffect(() => {
    if (testId) {
      // Start test attempt and generate questions for the specific subject
      startTestAttempt();
    }
  }, [testId]);

  const startTestAttempt = async () => {
    try {
      const subjectId = parseInt(testId!);
      const purchaseIdNum = purchaseId ? parseInt(purchaseId) : undefined;

      // Check if we already have an active test for this subject
      if (currentTest.isActive && currentTest.questions.length > 0) {
        console.log('Test already active with questions, skipping generation');
        return;
      }

      // First, start the test attempt
      const startResponse = await userTestsApi.startTest(subjectId, purchaseIdNum);
      const testAttemptId = startResponse.data.test_attempt_id;

      // Then generate questions for this test attempt
      const questionsResponse = await userTestsApi.generateTestQuestions(testAttemptId);
      const generatedQuestions = questionsResponse.data.questions;

      // Convert to the format expected by the test slice
      const formattedQuestions = generatedQuestions.map((q: any) => ({
        id: q.id,
        question: q.question,
        options: [q.options.A, q.options.B, q.options.C, q.options.D],
        correct_answer: q.correct_answer,
        explanation: q.explanation
      }));

      // Start the test with generated questions
      dispatch(startTest({
        testId: testAttemptId.toString(),
        questions: formattedQuestions,
        timeLimit: 3600 // 60 minutes
      }));

    } catch (error) {
      console.error('Failed to start test:', error);
      toast.error('Failed to start test. Please try again.');
      navigate('/results');
    }
  };

  useEffect(() => {
    if (autoSubmit && currentTest) {
      // Auto-submit when time is up
      dispatch(submitTest());
      toast.warning('Time is up! Test auto-submitted.');
      navigate('/results');
    }
  }, [autoSubmit, currentTest, dispatch, navigate]);

  useEffect(() => {
    if (!showInstructions && currentTest && currentTest.timeLeft > 0) {
      const timer = setInterval(() => {
        dispatch(updateTimer());
        if (currentTest.timeLeft <= 1) {
          setAutoSubmit(true);
        }
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [showInstructions, currentTest, dispatch]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswer = (questionId: number, answerIndex: number) => {
    dispatch(answerQuestion({ questionId, answerIndex }));
  };

  const handleToggleFlag = (questionId: number) => {
    dispatch(toggleFlag(questionId));
  };

  const handleSubmit = () => {
    dispatch(submitTest());
    toast.success('Test submitted successfully!');
    navigate('/results');
  };

  // Add loading and error states
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading test questions...</span>
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
            <h2 className="text-2xl mb-4">Error Loading Test</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => navigate('/courses')}>
              Back to Courses
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentTest || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4">No Test Available</h2>
            <p className="text-gray-600 mb-4">No questions found for this test.</p>
            <Button onClick={() => navigate('/courses')}>
              Back to Courses
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const answeredCount = Object.keys(currentTest.answers).length;
  const unansweredCount = questions.length - answeredCount;
  const progressPercentage = (answeredCount / questions.length) * 100;

  if (showInstructions) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <Card>
            <CardContent className="p-8 space-y-6">
              <div className="text-center">
                <h1 className="text-3xl mb-2">Test Instructions</h1>
                <p className="text-gray-600">Please read carefully before starting</p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 flex-shrink-0 mt-0.5">
                    1
                  </div>
                  <div>
                    <h3 className="mb-1">Total Questions</h3>
                    <p className="text-sm text-gray-600">This test contains {questions.length} multiple choice questions</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 flex-shrink-0 mt-0.5">
                    2
                  </div>
                  <div>
                    <h3 className="mb-1">Time Limit</h3>
                    <p className="text-sm text-gray-600">You have 60 minutes to complete the test</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 flex-shrink-0 mt-0.5">
                    3
                  </div>
                  <div>
                    <h3 className="mb-1">Marking Scheme</h3>
                    <p className="text-sm text-gray-600">+4 marks for correct answer, 0 marks for incorrect/unattempted</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 flex-shrink-0 mt-0.5">
                    4
                  </div>
                  <div>
                    <h3 className="mb-1">Navigation</h3>
                    <p className="text-sm text-gray-600">You can navigate between questions and flag them for review</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 flex-shrink-0 mt-0.5">
                    5
                  </div>
                  <div>
                    <h3 className="mb-1">Auto Submit</h3>
                    <p className="text-sm text-gray-600">Test will be automatically submitted when time runs out</p>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="text-yellow-800 mb-1">Important Note</p>
                  <p className="text-yellow-700">Once you start the test, the timer will begin. Make sure you have a stable internet connection and won't be disturbed.</p>
                </div>
              </div>

              <Button 
                size="lg" 
                className="w-full"
                onClick={() => setShowInstructions(false)}
              >
                Start Test
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Bar */}
      <div className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-lg">Mock Test #{testId}</h2>
              <Badge variant="secondary">{question.subject_name || 'Test'}</Badge>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                currentTest.timeLeft < 300 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
              }`}>
                <Clock className="w-5 h-5" />
                <span className="text-lg">{formatTime(currentTest.timeLeft)}</span>
              </div>
              <Button 
                variant="destructive" 
                onClick={() => setShowSubmitDialog(true)}
              >
                Submit Test
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Main Question Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Progress */}
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2 text-sm">
                  <span>Progress</span>
                  <span>{answeredCount} / {questions.length} answered</span>
                </div>
                <Progress value={progressPercentage} className="h-2" />
              </CardContent>
            </Card>

            {/* Question Card */}
            <Card>
              <CardContent className="p-8 space-y-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4">
                      <Badge>Question {currentQuestion + 1}</Badge>
                      <Badge variant="outline">{question.subject_name || 'Test'}</Badge>
                    </div>
                    <p className="text-xl">{question.question_text}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleToggleFlag(question.id)}
                  >
                    <Flag
                      className={`w-5 h-5 ${currentTest.flagged.includes(question.id) ? 'fill-red-500 text-red-500' : ''}`}
                    />
                  </Button>
                </div>

                <RadioGroup
                  value={currentTest.answers[question.id]?.toString()}
                  onValueChange={(value) => handleAnswer(question.id, parseInt(value))}
                >
                  <div className="space-y-3">
                    {[question.option_a, question.option_b, question.option_c, question.option_d].map((option, idx) => (
                      <div
                        key={idx}
                        className={`flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          currentTest.answers[question.id] === idx
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => handleAnswer(question.id, idx)}
                      >
                        <RadioGroupItem value={idx.toString()} id={`option-${idx}`} />
                        <Label
                          htmlFor={`option-${idx}`}
                          className="flex-1 cursor-pointer"
                        >
                          <span className="mr-3">{String.fromCharCode(65 + idx)}.</span>
                          {option}
                        </Label>
                      </div>
                    ))}
                  </div>
                </RadioGroup>
              </CardContent>
            </Card>

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>
              <Button
                onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
                disabled={currentQuestion === questions.length - 1}
              >
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>

          {/* Question Palette */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardContent className="p-6 space-y-4">
                <h3 className="text-lg">Question Palette</h3>
                
                <div className="grid grid-cols-5 gap-2">
                  {questions.map((q, idx) => (
                    <Button
                      key={q.id}
                      variant="outline"
                      size="sm"
                      className={`h-10 relative ${
                        currentQuestion === idx
                          ? 'ring-2 ring-blue-500'
                          : ''
                      } ${
                        currentTest.answers[q.id] !== undefined
                          ? 'bg-green-100 border-green-500 hover:bg-green-200'
                          : ''
                      }`}
                      onClick={() => setCurrentQuestion(idx)}
                    >
                      {idx + 1}
                      {currentTest.flagged.includes(q.id) && (
                        <Flag className="w-3 h-3 absolute -top-1 -right-1 fill-red-500 text-red-500" />
                      )}
                    </Button>
                  ))}
                </div>

                <div className="space-y-2 text-sm pt-4 border-t">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-green-100 border border-green-500 rounded"></div>
                    <span>Answered ({answeredCount})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 border-2 border-gray-300 rounded"></div>
                    <span>Not Answered ({unansweredCount})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Flag className="w-5 h-5 fill-red-500 text-red-500" />
                    <span>Flagged ({flagged.size})</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Submit Dialog */}
      <AlertDialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Submit Test?</AlertDialogTitle>
            <AlertDialogDescription>
              You have answered {answeredCount} out of {mockQuestions.length} questions.
              {unansweredCount > 0 && (
                <span className="block mt-2 text-yellow-600">
                  {unansweredCount} question(s) are still unanswered.
                </span>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Continue Test</AlertDialogCancel>
            <AlertDialogAction onClick={handleSubmit}>
              Submit
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
