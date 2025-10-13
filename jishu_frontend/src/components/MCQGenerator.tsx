import { useState } from 'react';
import Header from './Header';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { 
  Loader2, 
  Brain, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  BookOpen,
  Settings,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { mcqGenerationApi, MCQQuestion, AIStatusResponse } from '../services/api';

interface MCQGeneratorProps {
  user: any;
}

export default function MCQGenerator({ user }: MCQGeneratorProps) {
  // Form state - simplified to only use PDF content
  const [subject, setSubject] = useState('');
  const [numQuestions, setNumQuestions] = useState('5');
  // Removed difficulty options - always generate "hard" questions
  // Removed text content option - only PDF content allowed
  const [saveToDatabase, setSaveToDatabase] = useState(false);

  // UI state
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState<MCQQuestion[]>([]);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);

  // Check AI service status
  const checkAIStatus = async () => {
    try {
      setLoading(true);
      const response = await mcqGenerationApi.getAIStatus();
      setAiStatus(response.data);
      
      const statusMessage = `Status: ${response.data.status}\nOllama: ${response.data.dependencies.ollama ? 'Available' : 'Not Available'}\nPDF Files: ${response.data.pdfs_loaded || 0}`;
      toast.success('AI Status Retrieved', {
        description: statusMessage
      });
    } catch (error: any) {
      toast.error('Failed to check AI status', {
        description: error.message || 'Unknown error occurred'
      });
    } finally {
      setLoading(false);
    }
  };

  // Generate MCQ from subject PDFs only (removed text generation)

  // Generate MCQ from subject PDFs only - always hard difficulty
  const generateFromPDFs = async () => {
    if (!subject.trim()) {
      toast.error('Please enter a subject name to generate questions from PDFs');
      return;
    }

    const numQuestionsInt = parseInt(numQuestions);
    if (isNaN(numQuestionsInt) || numQuestionsInt < 1 || numQuestionsInt > 20) {
      toast.error('Number of questions must be between 1 and 20');
      return;
    }

    try {
      setLoading(true);
      setQuestions([]);

      const response = await mcqGenerationApi.generateFromPDFs({
        num_questions: numQuestionsInt,
        subject_name: subject.trim(),
        difficulty: 'hard', // Always generate hard questions
        save_to_database: saveToDatabase,
      });

      if (response.data.success && response.data.questions) {
        setQuestions(response.data.questions);
        toast.success(`Generated ${response.data.questions.length} hard questions from ${response.data.total_pdfs_processed || 0} PDF files!`);
      } else {
        toast.error('Failed to generate questions from PDFs', {
          description: response.data.error || 'Unknown error occurred'
        });
      }
    } catch (error: any) {
      toast.error('Failed to generate MCQ from PDFs', {
        description: error.message || 'Unknown error occurred'
      });
    } finally {
      setLoading(false);
    }
  };

  const renderQuestion = (question: MCQQuestion, index: number) => (
    <Card key={index} className="mb-6">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Question {index + 1}</CardTitle>
          {question.difficulty && (
            <Badge variant="outline">{question.difficulty}</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-lg font-medium">{question.question}</p>
        
        <div className="space-y-2">
          {question.options.map((option, optionIndex) => (
            <div 
              key={optionIndex} 
              className={`p-3 border rounded-lg ${
                option.startsWith(question.correct_answer) || 
                option.includes(question.correct_answer)
                  ? 'border-green-500 bg-green-50' 
                  : 'border-gray-200'
              }`}
            >
              <span className="font-medium mr-2">{String.fromCharCode(65 + optionIndex)}.</span>
              {option}
            </div>
          ))}
        </div>
        
        {question.explanation && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Explanation:</h4>
            <p className="text-blue-800">{question.explanation}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Brain className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold">MCQ Generator</h1>
              <Sparkles className="w-8 h-8 text-yellow-500" />
            </div>
            <p className="text-gray-600">Generate multiple-choice questions using AI from text content or PDF documents</p>
          </div>

          {/* AI Status Card */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                AI Service Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={checkAIStatus} 
                disabled={loading}
                className="w-full sm:w-auto"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle2 className="w-4 h-4 mr-2" />}
                Check AI Status
              </Button>
              
              {aiStatus && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>Status: <Badge variant={aiStatus.status === 'running' ? 'default' : 'destructive'}>{aiStatus.status}</Badge></div>
                    <div>PDFs Loaded: <Badge variant="outline">{aiStatus.pdfs_loaded}</Badge></div>
                    <div>Ollama: <Badge variant={aiStatus.dependencies.ollama ? 'default' : 'destructive'}>{aiStatus.dependencies.ollama ? 'Available' : 'Not Available'}</Badge></div>
                    <div>PDF Processing: <Badge variant={aiStatus.dependencies.PyPDF2 ? 'default' : 'destructive'}>{aiStatus.dependencies.PyPDF2 ? 'Available' : 'Not Available'}</Badge></div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Generation Mode - PDF Only */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                MCQ Generation from Subject PDFs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Generate hard-level MCQ questions from PDF textbooks in the pdfs/subjects/ directory.
              </p>
            </CardContent>
          </Card>

          {/* Configuration Form */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Configuration Fields - Simplified for PDF-only generation */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject Name *</Label>
                  <Input
                    id="subject"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g., Biology, Mathematics, History"
                    required
                  />
                  <p className="text-sm text-gray-500">
                    Must match a folder name in pdfs/subjects/ directory
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="numQuestions">Number of Questions (1-20)</Label>
                  <Input
                    id="numQuestions"
                    type="number"
                    min="1"
                    max="20"
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(e.target.value)}
                    placeholder="5"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="saveToDatabase"
                      checked={saveToDatabase}
                      onCheckedChange={setSaveToDatabase}
                    />
                    <Label htmlFor="saveToDatabase">Save to Database</Label>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium">Difficulty Level</Label>
                  <div className="p-3 bg-gray-50 rounded-md">
                    <span className="text-sm text-gray-600">Hard (Fixed)</span>
                    <p className="text-xs text-gray-500 mt-1">
                      All questions are generated at hard difficulty level
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Action Button - PDF Generation Only */}
              <div className="flex gap-4">
                <Button
                  onClick={generateFromPDFs}
                  disabled={loading || !subject.trim()}
                  className="flex-1"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <FileText className="w-4 h-4 mr-2" />
                  )}
                  Generate Hard MCQs from Subject PDFs
                </Button>
              </div>

              {loading && (
                <Alert>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <AlertDescription>
                    Generating questions... This may take a few moments.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Generated Questions */}
          {questions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  Generated Questions ({questions.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {questions.map(renderQuestion)}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
