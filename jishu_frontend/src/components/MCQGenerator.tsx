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
  // Form state
  const [topic, setTopic] = useState('');
  const [subject, setSubject] = useState('');
  const [content, setContent] = useState('');
  const [numQuestions, setNumQuestions] = useState('5');
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [usePdfContent, setUsePdfContent] = useState(true);
  const [saveToDatabase, setSaveToDatabase] = useState(false);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState<MCQQuestion[]>([]);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'text' | 'pdf'>('pdf');

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

  // Generate MCQ from text content
  const generateFromText = async () => {
    if (!content.trim()) {
      toast.error('Please enter content to generate questions from');
      return;
    }

    if (content.trim().length < 100) {
      toast.error('Content must be at least 100 characters long');
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

      const response = await mcqGenerationApi.generateFromText({
        content: content.trim(),
        num_questions: numQuestionsInt,
        subject_name: subject.trim() || undefined,
        difficulty,
        save_to_database: saveToDatabase,
      });

      if (response.data.success && response.data.questions) {
        setQuestions(response.data.questions);
        toast.success(`Generated ${response.data.questions.length} questions successfully!`);
      } else {
        toast.error('Failed to generate questions', {
          description: response.data.error || 'Unknown error occurred'
        });
      }
    } catch (error: any) {
      toast.error('Failed to generate MCQ from text', {
        description: error.message || 'Unknown error occurred'
      });
    } finally {
      setLoading(false);
    }
  };

  // Generate MCQ from PDFs
  const generateFromPDFs = async () => {
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
        subject_name: subject.trim() || undefined,
        difficulty,
        save_to_database: saveToDatabase,
      });

      if (response.data.success && response.data.questions) {
        setQuestions(response.data.questions);
        toast.success(`Generated ${response.data.questions.length} questions from ${response.data.total_pdfs_processed || 0} PDF files!`);
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

          {/* Generation Mode Tabs */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Generation Mode</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 mb-6">
                <Button
                  variant={activeTab === 'pdf' ? 'default' : 'outline'}
                  onClick={() => setActiveTab('pdf')}
                  className="flex-1"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  From PDFs
                </Button>
                <Button
                  variant={activeTab === 'text' ? 'default' : 'outline'}
                  onClick={() => setActiveTab('text')}
                  className="flex-1"
                >
                  <BookOpen className="w-4 h-4 mr-2" />
                  From Text
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Configuration Form */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Common Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject (Optional)</Label>
                  <Input
                    id="subject"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g., Biology, Mathematics, History"
                  />
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
                  <Label htmlFor="difficulty">Difficulty Level</Label>
                  <Select value={difficulty} onValueChange={(value: 'easy' | 'medium' | 'hard') => setDifficulty(value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select difficulty" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
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
              </div>

              {/* Text Content Field (only for text mode) */}
              {activeTab === 'text' && (
                <div className="space-y-2">
                  <Label htmlFor="content">Content *</Label>
                  <Textarea
                    id="content"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter the educational content from which you want to generate MCQs (minimum 100 characters)..."
                    rows={8}
                    className="resize-none"
                  />
                  <p className="text-sm text-gray-500">
                    Characters: {content.length} (minimum 100 required)
                  </p>
                </div>
              )}

              {/* Topic Field (only for PDF mode) */}
              {activeTab === 'pdf' && (
                <div className="space-y-2">
                  <Label htmlFor="topic">Topic (Optional)</Label>
                  <Input
                    id="topic"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., photosynthesis, algebra, history"
                  />
                  <p className="text-sm text-gray-500">
                    Leave empty to generate questions from all available PDF content
                  </p>
                </div>
              )}

              <Separator />

              {/* Action Buttons */}
              <div className="flex gap-4">
                {activeTab === 'text' ? (
                  <Button
                    onClick={generateFromText}
                    disabled={loading || !content.trim() || content.length < 100}
                    className="flex-1"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Brain className="w-4 h-4 mr-2" />
                    )}
                    Generate from Text
                  </Button>
                ) : (
                  <Button
                    onClick={generateFromPDFs}
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <FileText className="w-4 h-4 mr-2" />
                    )}
                    Generate from PDFs
                  </Button>
                )}
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
