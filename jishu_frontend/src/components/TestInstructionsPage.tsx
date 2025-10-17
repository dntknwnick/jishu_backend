import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle, CheckCircle2, Clock, BookOpen } from 'lucide-react';
import Header from './Header';
import { userTestsApi } from '@/services/api';
import { toast } from 'sonner';

interface TestInstructionsPageProps {
  user?: any;
}

const TestInstructionsPage: React.FC<TestInstructionsPageProps> = ({ user }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const [isLoading, setIsLoading] = useState(true);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [isGenerationComplete, setIsGenerationComplete] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [canStartTest, setCanStartTest] = useState(false);

  const mockTestId = location.state?.mockTestId;
  const generationSessionId = location.state?.generationSessionId;
  const subjectName = location.state?.subjectName;
  const testNumber = location.state?.testNumber;

  // Poll generation status
  useEffect(() => {
    if (!mockTestId || !generationSessionId) {
      setErrorMessage('Invalid test session');
      setHasError(true);
      setIsLoading(false);
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const response = await userTestsApi.getGenerationProgress(generationSessionId);

        if (response.data.success) {
          const { progress, is_complete, has_error, error_message, can_use_partial } = response.data;

          setGenerationProgress(progress);

          if (has_error) {
            setHasError(true);
            setErrorMessage(error_message || 'Generation failed');
            setIsLoading(false);
            clearInterval(pollInterval);
          } else if (is_complete) {
            setIsGenerationComplete(true);
            setCanStartTest(true);
            setIsLoading(false);
            clearInterval(pollInterval);
            toast.success('Test questions are ready!');
          } else if (can_use_partial && progress >= 10) {
            // Can start test with partial questions
            setCanStartTest(true);
          }
        }
      } catch (error) {
        console.error('Error polling generation status:', error);
        setHasError(true);
        setErrorMessage('Failed to check generation status');
        setIsLoading(false);
        clearInterval(pollInterval);
      }
    }, 1000); // Poll every second

    return () => clearInterval(pollInterval);
  }, [mockTestId, generationSessionId, toast]);

  const handleStartTest = async () => {
    try {
      setIsLoading(true);

      // Call start endpoint with generation session ID
      const response = await userTestsApi.startTestCard(mockTestId);

      // Navigate to test screen
      navigate('/test', {
        state: {
          sessionId: response.data.session_id,
          mockTestId: response.data.mock_test_id,
          attemptNumber: response.data.attempt_number,
          remainingAttempts: response.data.remaining_attempts,
          questionsGenerated: response.data.questions_generated,
          testNumber,
          subjectName,
          isReAttempt: false
        }
      });
    } catch (error) {
      console.error('Failed to start test:', error);
      toast.error('Failed to start test. Please try again.');
      setIsLoading(false);
    }
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Test Instructions
            </h1>
            <p className="text-muted-foreground">
              {subjectName} - Test #{testNumber}
            </p>
          </div>

          {/* Error State */}
          {hasError && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {/* Instructions Card */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                Test Guidelines
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-300">
                    1
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Total Questions</h3>
                    <p className="text-sm text-muted-foreground">
                      You will have 50 multiple choice questions to answer
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-300">
                    2
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Time Limit</h3>
                    <p className="text-sm text-muted-foreground">
                      You have 60 minutes to complete the test
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-300">
                    3
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Marking Scheme</h3>
                    <p className="text-sm text-muted-foreground">
                      +1 mark for correct answer, 0 marks for wrong/unanswered
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-300">
                    4
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Review & Submit</h3>
                    <p className="text-sm text-muted-foreground">
                      You can review and change your answers before submitting
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generation Status Card */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Preparing Your Test
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoading && !hasError ? (
                <>
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    <span className="text-foreground">
                      Generating test questions...
                    </span>
                  </div>
                  <Progress value={generationProgress} className="h-2" />
                  <p className="text-sm text-muted-foreground">
                    {Math.round(generationProgress)}% complete
                  </p>
                </>
              ) : isGenerationComplete && !hasError ? (
                <div className="flex items-center gap-3 text-green-600 dark:text-green-400">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-semibold">
                    All questions are ready! You can start the test now.
                  </span>
                </div>
              ) : null}
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleGoBack}
              disabled={isLoading}
              className="flex-1"
            >
              Go Back
            </Button>
            <Button
              onClick={handleStartTest}
              disabled={!canStartTest || isLoading || hasError}
              className="flex-1 !bg-slate-900 !text-white hover:!bg-slate-800 dark:!bg-slate-700 dark:hover:!bg-slate-600"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Preparing...
                </>
              ) : (
                'Start Test'
              )}
            </Button>
          </div>

          {/* Info Message */}
          {!isLoading && !canStartTest && !hasError && (
            <Alert className="mt-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Questions are being generated. Please wait...
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestInstructionsPage;

