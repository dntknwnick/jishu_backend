import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
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
  Loader2,
  RotateCcw
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
  const location = useLocation();
  const dispatch = useAppDispatch();

  // Get session info from navigation state (new test card flow)
  const sessionInfo = location.state as {
    sessionId?: number;
    mockTestId?: number;
    attemptNumber?: number;
    remainingAttempts?: number;
    questionsGenerated?: boolean;
    testNumber?: number;
    subjectName?: string;
    isReAttempt?: boolean;
  } | null;

  // Legacy: Get purchase_id from query parameters if present
  const urlParams = new URLSearchParams(window.location.search);
  const purchaseId = urlParams.get('purchase_id');

  const { questions, currentTest, isLoading, error } = useAppSelector((state) => state.tests);

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  // Determine if we should show instructions based on attempt type
  const shouldShowInstructions = !sessionInfo?.isReAttempt; // Skip instructions for re-attempts
  const [showInstructions, setShowInstructions] = useState(shouldShowInstructions);
  const [autoSubmit, setAutoSubmit] = useState(false);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);
  const [hasLoadedSession, setHasLoadedSession] = useState(false);

  // Chunked generation state
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [generationProgress, setGenerationProgress] = useState<any>(null);
  const [isUsingChunkedGeneration, setIsUsingChunkedGeneration] = useState(false);
  const [progressPollingInterval, setProgressPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Debug: Check Redux state (after state declarations)
  console.log('🔍 Redux State Debug:');
  console.log('- currentTest:', currentTest);
  console.log('- currentTest.questions length:', currentTest?.questions?.length);
  console.log('- currentTest.timeLeft:', currentTest?.timeLeft, 'type:', typeof currentTest?.timeLeft);
  console.log('- showInstructions:', showInstructions);
  console.log('- isLoadingQuestions:', isLoadingQuestions);
  console.log('- sessionInfo?.isReAttempt:', sessionInfo?.isReAttempt);
  console.log('- shouldShowInstructions:', shouldShowInstructions);

  useEffect(() => {
    if (sessionInfo?.sessionId && !hasLoadedSession) {
      // New test card flow - check if re-attempt or first attempt
      if (sessionInfo.isReAttempt) {
        // Re-attempt: Use existing flow (questions already exist)
        console.log('🔄 Initializing re-attempt flow');
        loadTestSession();
      } else {
        // First attempt: Use chunked generation
        console.log('🔄 Initializing chunked generation flow');
        startChunkedGeneration(undefined, sessionInfo.sessionId);
        setHasLoadedSession(true);
      }
    } else if (testId && !hasLoadedSession) {
      // Legacy flow - use chunked generation for new tests
      console.log('🔄 Initializing legacy chunked generation flow');
      const subjectId = parseInt(testId);
      // Start test attempt first, then use chunked generation
      startLegacyChunkedFlow(subjectId);
    } else if (!sessionInfo?.sessionId && !testId) {
      // No valid test identifier - redirect to results
      console.log('❌ No valid test identifier found, redirecting to results');
      toast.error('Invalid test session. Please start a new test.');
      navigate('/results');
    }
  }, [testId, sessionInfo, hasLoadedSession]);

  const loadTestSession = async () => {
    if (!sessionInfo?.sessionId || hasLoadedSession) {
      console.log('❌ Skipping loadTestSession:', { sessionId: sessionInfo?.sessionId, hasLoadedSession });
      return;
    }

    console.log('🚀 Starting loadTestSession for session:', sessionInfo.sessionId);
    setIsLoadingQuestions(true);
    setHasLoadedSession(true);
    try {

      // Use the proper test session endpoint for new test card system
      console.log('📡 Calling test session questions API for session:', sessionInfo.sessionId);
      const questionsResponse = await userTestsApi.getTestQuestions(sessionInfo.sessionId);
      console.log('✅ Test Session Response:', questionsResponse);

      const generatedQuestions = questionsResponse.data.questions;
      console.log('📝 AI Generated Questions Count:', generatedQuestions.length);

      // Convert to the format expected by the test slice (new API format)
      console.log('🔍 Full API response:', questionsResponse);
      console.log('🔍 Generated questions array:', generatedQuestions);
      console.log('🔍 Sample question data (first question):', generatedQuestions[0]);
      console.log('🔍 All question keys:', Object.keys(generatedQuestions[0] || {}));

      const formattedQuestions = generatedQuestions.map((q: any, index: number) => {
        console.log(`🔍 Question ${index + 1} raw data:`, q);
        console.log(`🔍 Question ${index + 1} keys:`, Object.keys(q));

        // Try multiple possible formats
        let options = [];
        if (q.options && typeof q.options === 'object') {
          // Format: { A: "text", B: "text", C: "text", D: "text" }
          options = [q.options.A, q.options.B, q.options.C, q.options.D];
          console.log(`🔍 Using options object format:`, options);
        } else if (q.option_1) {
          // Format: option_1, option_2, option_3, option_4
          options = [q.option_1, q.option_2, q.option_3, q.option_4];
          console.log(`🔍 Using option_X format:`, options);
        } else if (Array.isArray(q.options)) {
          // Format: ["text1", "text2", "text3", "text4"]
          options = q.options;
          console.log(`🔍 Using options array format:`, options);
        } else {
          console.log(`❌ No valid options format found for question ${index + 1}`);
          options = ['Option A', 'Option B', 'Option C', 'Option D']; // Fallback
        }

        const questionData = {
          id: q.id,
          question: q.question,
          options: options,
          correct_answer: q.correct_answer,
          explanation: q.explanation || ''
        };

        console.log(`🔍 Question ${index + 1} formatted:`, questionData);
        return questionData;
      });

      console.log('🔄 Formatted Questions Count:', formattedQuestions.length);

      // Start the test with session info
      const testData = {
        testId: sessionInfo.sessionId.toString(),
        questions: formattedQuestions,
        duration: 3600, // 60 minutes (Redux expects 'duration', not 'timeLimit')
        sessionInfo: sessionInfo
      };

      console.log('🎯 Dispatching startTest with:', testData);
      console.log('🎯 Duration being set:', testData.duration);
      dispatch(startTest(testData));

      console.log('✅ Questions loaded successfully!');

      // Handle navigation based on attempt type
      if (sessionInfo.isReAttempt) {
        // Re-attempt: Skip instructions and go directly to test
        setShowInstructions(false);
        toast.info(`This is attempt ${sessionInfo.attemptNumber}/3. Questions are reused from your first attempt.`);
      } else {
        // First attempt: Show instructions (already set by default)
        toast.success('Questions generated successfully! Review the instructions and start your test.');
      }

    } catch (error) {
      console.error('Failed to load test session:', error);
      toast.error('Failed to load test questions. Please try again.');
      setHasLoadedSession(false); // Reset on error so user can retry
      navigate('/results');
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  const startTestAttempt = async () => {
    if (hasLoadedSession) {
      console.log('❌ Skipping startTestAttempt: already loaded');
      return;
    }

    console.log('🚀 Starting legacy test attempt for subject:', testId);
    setIsLoadingQuestions(true);
    setHasLoadedSession(true);

    try {
      const subjectId = parseInt(testId!);
      const purchaseIdNum = purchaseId ? parseInt(purchaseId) : undefined;

      // Check if we already have an active test for this subject
      if (currentTest.isActive && currentTest.questions.length > 0) {
        console.log('Test already active with questions, skipping generation');
        setIsLoadingQuestions(false);
        return;
      }

      console.log('MCQTestScreen: Loading test for subject', subjectId);

      // Legacy flow: start test attempt and generate questions
      const startResponse = await userTestsApi.startTest(subjectId, purchaseIdNum);
      const testAttemptId = startResponse.data.test_attempt_id;

      // Generate questions (backend should handle duplicate calls gracefully)
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
        duration: 3600 // 60 minutes (use 'duration' for consistency)
      }));

      console.log('✅ Legacy test started successfully!');
      toast.success('Questions generated successfully! Review the instructions and start your test.');

    } catch (error) {
      console.error('Failed to start test:', error);
      toast.error('Failed to start test. Please try again.');
      setHasLoadedSession(false); // Reset on error so user can retry
      navigate('/results');
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  // Chunked MCQ Generation Functions
  const startChunkedGeneration = async (testAttemptId?: number, sessionId?: number) => {
    try {
      console.log('🚀 Starting chunked MCQ generation');
      setIsLoadingQuestions(true);
      setIsUsingChunkedGeneration(true);

      const response = await userTestsApi.startChunkedGeneration({
        test_attempt_id: testAttemptId,
        session_id: sessionId
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to start chunked generation');
      }

      const { generation_id, initial_questions, progress, background_generation_started } = response.data;

      setGenerationId(generation_id);
      setGenerationProgress(progress);

      // Start the test with initial questions
      const formattedQuestions = initial_questions.map((q: any) => ({
        id: q.id,
        question: q.question,
        options: [q.options.A, q.options.B, q.options.C, q.options.D],
        correct_answer: q.correct_answer,
        explanation: q.explanation
      }));

      dispatch(startTest({
        testId: (testAttemptId || sessionId)?.toString() || 'chunked',
        questions: formattedQuestions,
        duration: 3600
      }));

      // Navigate to instructions immediately with initial questions
      setShowInstructions(true);
      setIsLoadingQuestions(false);

      // Start polling for progress if background generation is running
      if (background_generation_started) {
        startProgressPolling(generation_id);
      }

      toast.success(`Initial ${initial_questions.length} questions ready! More questions loading in background.`);

    } catch (error) {
      console.error('Failed to start chunked generation:', error);
      toast.error('Failed to start test. Please try again.');
      setIsLoadingQuestions(false);
      setIsUsingChunkedGeneration(false);
      navigate('/results');
    }
  };

  const startProgressPolling = (genId: string) => {
    if (progressPollingInterval) {
      clearInterval(progressPollingInterval);
    }

    const interval = setInterval(async () => {
      try {
        const response = await userTestsApi.getGenerationProgress(genId);

        if (response.data.success) {
          const { progress, questions, is_complete, has_error, can_use_partial } = response.data;
          setGenerationProgress(progress);

          // Update questions in Redux if we have new ones
          if (questions.length > currentTest.questions.length) {
            const formattedQuestions = questions.map((q: any) => ({
              id: q.id,
              question: q.question,
              options: [q.options.A, q.options.B, q.options.C, q.options.D],
              correct_answer: q.correct_answer,
              explanation: q.explanation
            }));

            // Update the test with new questions
            dispatch(startTest({
              testId: currentTest.id,
              questions: formattedQuestions,
              duration: currentTest.timeLeft
            }));
          }

          // Handle completion or errors
          if (is_complete) {
            clearInterval(interval);
            setProgressPollingInterval(null);
            toast.success('All questions loaded successfully!');
          } else if (has_error) {
            clearInterval(interval);
            setProgressPollingInterval(null);

            if (can_use_partial) {
              toast.warning(`Question generation encountered an issue, but you can continue with ${questions.length} questions available.`);
            } else {
              toast.error('Question generation failed. Please refresh and try again.');
            }
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
        // Continue polling despite errors, but limit retries
      }
    }, 3000); // Poll every 3 seconds

    setProgressPollingInterval(interval);
  };



  // Legacy chunked flow - start test attempt then use chunked generation
  const startLegacyChunkedFlow = async (subjectId: number) => {
    try {
      setIsLoadingQuestions(true);
      setHasLoadedSession(true);

      const purchaseIdNum = purchaseId ? parseInt(purchaseId) : undefined;

      // Start test attempt first
      const startResponse = await userTestsApi.startTest(subjectId, purchaseIdNum);
      const testAttemptId = startResponse.data.test_attempt_id;

      // Then use chunked generation
      await startChunkedGeneration(testAttemptId, undefined);

    } catch (error) {
      console.error('Failed to start legacy chunked flow:', error);
      toast.error('Failed to start test. Please try again.');
      setIsLoadingQuestions(false);
      setHasLoadedSession(false);
      navigate('/results');
    }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (progressPollingInterval) {
        clearInterval(progressPollingInterval);
      }
    };
  }, [progressPollingInterval]);

  useEffect(() => {
    if (autoSubmit && currentTest) {
      // Auto-submit when time is up
      handleSubmit();
      toast.warning('Time is up! Test auto-submitted.');
    }
  }, [autoSubmit, currentTest]);

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
    // Handle invalid or undefined seconds
    if (!seconds || isNaN(seconds) || seconds < 0) {
      return '01:00:00'; // Default to 1 hour
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswer = (questionId: number, answerIndex: number) => {
    console.log('🎯 Answer selected:', { questionId, answerIndex, option: ['A', 'B', 'C', 'D'][answerIndex] });
    dispatch(answerQuestion({ questionId, answerIndex }));
  };

  const handleToggleFlag = (questionId: number) => {
    dispatch(toggleFlag(questionId));
  };

  const handleSubmit = async () => {
    try {
      if (sessionInfo?.sessionId) {
        // New test card flow - submit to session endpoint
        console.log('🚀 Submitting test with answers:', currentTest.answers);

        // Convert answers object to array format expected by API
        const answers = currentTest.questions.map((question) => ({
          question_id: question.id,
          selected_option: currentTest.answers[question.id] !== undefined
            ? ['A', 'B', 'C', 'D'][currentTest.answers[question.id]]
            : null
        }));

        console.log('🚀 Formatted answers for API:', answers);
        const timeTaken = 3600 - currentTest.timeLeft; // Calculate time taken
        console.log('🚀 Time taken:', timeTaken);

        const response = await userTestsApi.submitTestSession(
          sessionInfo.sessionId,
          answers,
          timeTaken
        );

        // Show results with session info
        navigate('/results', {
          state: {
            sessionResult: response.data,
            sessionInfo: sessionInfo,
            isNewTestCardFlow: true
          }
        });

        toast.success(`Test submitted! Score: ${response.data.score}/50 (${response.data.percentage}%)`);

        if (response.data.is_final_attempt) {
          toast.info('This was your final attempt for this test card.');
        } else if (response.data.remaining_attempts > 0) {
          toast.info(`You have ${response.data.remaining_attempts} attempts remaining.`);
        }

      } else {
        // Legacy flow
        dispatch(submitTest());
        toast.success('Test submitted successfully!');
        navigate('/results', {
          state: {
            testCompleted: true
          }
        });
      }
    } catch (error) {
      console.error('Failed to submit test:', error);
      toast.error('Failed to submit test. Please try again.');
    }
  };

  // Add loading and error states
  if (isLoading || isLoadingQuestions) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <Card className="w-full max-w-md">
            <CardContent className="p-8 text-center space-y-4">
              <div className="flex justify-center">
                <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold">
                  {isUsingChunkedGeneration ? 'Preparing Your Test' : 'Generating Test Questions'}
                </h3>
                <p className="text-muted-foreground">
                  {sessionInfo?.isReAttempt
                    ? 'Loading your previous questions...'
                    : isUsingChunkedGeneration
                    ? 'Generating initial questions to get you started...'
                    : 'Creating new questions for your test...'}
                </p>
                {isUsingChunkedGeneration && generationProgress ? (
                  <div className="space-y-2">
                    <Progress
                      value={Math.min(generationProgress.progress_percentage, 100)}
                      className="w-full"
                    />
                    <p className="text-sm text-muted-foreground">
                      {generationProgress.questions_generated_count} of {generationProgress.total_questions_needed} questions ready
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground">This may take a few moments</p>
                )}
              </div>
              {sessionInfo && (
                <div className="pt-4 border-t border-border">
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground">
                    Test Card #{sessionInfo.testNumber} - {sessionInfo.subjectName}
                  </p>
                  {sessionInfo.isReAttempt && (
                    <Badge variant="outline" className="mt-2">
                      Re-attempt {sessionInfo.attemptNumber}/3
                    </Badge>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background dark:bg-slate-900">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4 text-foreground">Error Loading Test</h2>
            <p className="text-muted-foreground dark:text-muted-foreground mb-4">{error}</p>
            <Button onClick={() => navigate('/courses')}>
              Back to Courses
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentTest || !currentTest.questions || currentTest.questions.length === 0) {
    return (
      <div className="min-h-screen bg-background dark:bg-slate-900">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4 text-foreground">No Test Available</h2>
            <p className="text-muted-foreground dark:text-muted-foreground mb-4">No questions found for this test.</p>
            <Button onClick={() => navigate('/courses')}>
              Back to Courses
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const answeredCount = Object.keys(currentTest.answers).length;
  const unansweredCount = currentTest.questions.length - answeredCount;
  const progressPercentage = (answeredCount / currentTest.questions.length) * 100;

  if (showInstructions) {
    return (
      <div className="min-h-screen bg-background dark:bg-slate-900">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <Card>
            <CardContent className="p-8 space-y-6">
              <div className="text-center">
                <h1 className="text-3xl mb-2 text-foreground">Test Instructions</h1>
                {sessionInfo ? (
                  <div className="space-y-2">
                    <p className="text-muted-foreground dark:text-muted-foreground">Test Card #{sessionInfo.testNumber} - {sessionInfo.subjectName}</p>
                    {sessionInfo.isReAttempt && (
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-200 rounded-full text-sm">
                        <RotateCcw className="w-4 h-4" />
                        Re-attempt {sessionInfo.attemptNumber}/3 - Same questions as first attempt
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-muted-foreground dark:text-muted-foreground">Please read carefully before starting</p>
                )}
              </div>

              {/* Show loading state while questions are being generated */}
              {isLoadingQuestions ? (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600 dark:text-blue-400" />
                    <div>
                      <h4 className="font-medium text-foreground dark:text-blue-200">Preparing Your Test</h4>
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        {sessionInfo?.isReAttempt
                          ? 'Loading your previous questions...'
                          : 'Generating fresh questions for your test...'}
                      </p>
                    </div>
                  </div>
                </div>
              ) : currentTest?.questions?.length > 0 && (
                <div className={`border rounded-lg p-4 ${
                  isUsingChunkedGeneration && generationProgress?.generation_status !== 'completed'
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-green-50 border-green-200'
                }`}>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      {isUsingChunkedGeneration && generationProgress?.generation_status !== 'completed' ? (
                        <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                      ) : (
                        <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
                          <svg className="w-3 h-3 text-primary-foreground" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                      <div className="flex-1">
                        <h4 className={`font-medium ${
                          isUsingChunkedGeneration && generationProgress?.generation_status !== 'completed'
                            ? 'text-foreground'
                            : 'text-green-900'
                        }`}>
                          {isUsingChunkedGeneration && generationProgress?.generation_status !== 'completed'
                            ? 'Questions Loading...'
                            : 'Test Ready!'}
                        </h4>
                        <p className={`text-sm ${
                          isUsingChunkedGeneration && generationProgress?.generation_status !== 'completed'
                            ? 'text-blue-700'
                            : 'text-green-700'
                        }`}>
                          {isUsingChunkedGeneration && generationProgress ? (
                            <>
                              {generationProgress.questions_generated_count} of {generationProgress.total_questions_needed} questions ready
                              {generationProgress.generation_status !== 'completed' && ' - More questions loading in background'}
                            </>
                          ) : (
                            `${currentTest.questions.length} questions have been prepared for your test.`
                          )}
                        </p>
                      </div>
                    </div>

                    {isUsingChunkedGeneration && generationProgress && generationProgress.generation_status !== 'completed' && (
                      <div className="space-y-2">
                        <Progress
                          value={Math.min(generationProgress.progress_percentage, 100)}
                          className="w-full h-2"
                        />
                        <p className="text-xs text-blue-600">
                          You can start the test now with {currentTest.questions.length} questions.
                          Remaining questions will be available as you progress.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-200 flex-shrink-0 mt-0.5">
                    1
                  </div>
                  <div>
                    <h3 className="mb-1 text-foreground">Total Questions</h3>
                    <p className="text-sm text-muted-foreground dark:text-muted-foreground">
                      This test contains {currentTest?.questions?.length || 50} multiple choice questions
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-200 flex-shrink-0 mt-0.5">
                    2
                  </div>
                  <div>
                    <h3 className="mb-1 text-foreground">Time Limit</h3>
                    <p className="text-sm text-muted-foreground dark:text-muted-foreground">You have 60 minutes to complete the test</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-200 flex-shrink-0 mt-0.5">
                    3
                  </div>
                  <div>
                    <h3 className="mb-1 text-foreground">Marking Scheme</h3>
                    <p className="text-sm text-muted-foreground dark:text-muted-foreground">+4 marks for correct answer, 0 marks for incorrect/unattempted</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-200 flex-shrink-0 mt-0.5">
                    4
                  </div>
                  <div>
                    <h3 className="mb-1 text-foreground">Navigation</h3>
                    <p className="text-sm text-muted-foreground dark:text-muted-foreground">You can navigate between questions and flag them for review</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-200 flex-shrink-0 mt-0.5">
                    5
                  </div>
                  <div>
                    <h3 className="mb-1 text-foreground">Auto Submit</h3>
                    <p className="text-sm text-muted-foreground dark:text-muted-foreground">Test will be automatically submitted when time runs out</p>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 flex gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="text-yellow-800 dark:text-yellow-200 mb-1">Important Note</p>
                  <p className="text-yellow-700 dark:text-yellow-300">Once you start the test, the timer will begin. Make sure you have a stable internet connection and won't be disturbed.</p>
                </div>
              </div>

              <Button
                size="lg"
                className="w-full"
                onClick={() => setShowInstructions(false)}
                disabled={isLoadingQuestions || !currentTest?.questions?.length}
              >
                {isLoadingQuestions ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Preparing Questions...
                  </>
                ) : !currentTest?.questions?.length ? (
                  'Loading...'
                ) : (
                  'Start Test'
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const question = currentTest.questions[currentQuestion];

  return (
    <div className="min-h-screen bg-background dark:bg-slate-900">
      {/* Top Bar */}
      <div className="bg-background dark:bg-card border-b border-border sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {sessionInfo ? (
                <div className="flex items-center gap-3">
                  <h2 className="text-lg">Test Card #{sessionInfo.testNumber}</h2>
                  <Badge variant="secondary">{sessionInfo.subjectName}</Badge>
                  {sessionInfo.isReAttempt && (
                    <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                      <RotateCcw className="w-3 h-3 mr-1" />
                      Attempt {sessionInfo.attemptNumber}/3
                    </Badge>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <h2 className="text-lg">Mock Test #{testId}</h2>
                  <Badge variant="secondary">Test</Badge>
                </div>
              )}
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
                  <span>{answeredCount} / {currentTest.questions.length} answered</span>
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
                    <p className="text-xl">{question.question}</p>
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
                    {(() => {
                      console.log('🎨 Rendering question:', question);
                      console.log('🎨 Question options:', question.options);
                      console.log('🎨 Options type:', typeof question.options);
                      console.log('🎨 Options length:', question.options?.length);
                      return question.options.map((option, idx) => {
                        console.log(`🎨 Rendering option ${idx}:`, option);
                        return (
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
                        );
                      });
                    })()}
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
                onClick={() => setCurrentQuestion(Math.min(currentTest.questions.length - 1, currentQuestion + 1))}
                disabled={currentQuestion === currentTest.questions.length - 1}
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
                    <span>Flagged ({currentTest.flagged.length})</span>
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
              You have answered {answeredCount} out of {currentTest.questions.length} questions.
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
