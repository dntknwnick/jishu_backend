import { useState, useRef, useEffect } from 'react';
import Header from './Header';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles,
  BookOpen,
  Calculator,
  Beaker,
  Atom,
  Lightbulb
} from 'lucide-react';

interface AIChatbotProps {
  user: any;
}

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const quickQuestions = [
  { icon: <Atom className="w-4 h-4" />, text: 'Explain Newton\'s Laws', category: 'Physics' },
  { icon: <Beaker className="w-4 h-4" />, text: 'What is Chemical Bonding?', category: 'Chemistry' },
  { icon: <BookOpen className="w-4 h-4" />, text: 'Explain Photosynthesis', category: 'Biology' },
  { icon: <Calculator className="w-4 h-4" />, text: 'Solve Quadratic Equations', category: 'Maths' },
];

const aiResponses: { [key: string]: string } = {
  'newton': "Newton's Laws of Motion are three fundamental principles that describe the relationship between motion and forces:\n\n1. **First Law (Law of Inertia)**: An object at rest stays at rest, and an object in motion stays in motion with the same speed and direction unless acted upon by an external force.\n\n2. **Second Law**: Force = Mass × Acceleration (F = ma). This shows that force is directly proportional to acceleration and inversely proportional to mass.\n\n3. **Third Law**: For every action, there is an equal and opposite reaction.\n\nThese laws are fundamental to understanding mechanics and are frequently tested in competitive exams!",
  
  'bonding': "Chemical bonding is the force that holds atoms together in molecules and compounds. There are three main types:\n\n1. **Ionic Bonding**: Transfer of electrons between atoms (typically metal + non-metal). Example: NaCl\n\n2. **Covalent Bonding**: Sharing of electrons between atoms (typically non-metal + non-metal). Example: H₂O\n\n3. **Metallic Bonding**: Electrons are delocalized across metal atoms. Example: Iron, Copper\n\nUnderstanding bonding helps explain properties like melting point, conductivity, and solubility!",
  
  'photosynthesis': "Photosynthesis is the process by which plants convert light energy into chemical energy stored in glucose.\n\n**Equation**: 6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂\n\n**Two Stages**:\n1. **Light Reactions** (Thylakoid): Light energy splits water, producing ATP, NADPH, and O₂\n2. **Calvin Cycle** (Stroma): CO₂ is fixed using ATP and NADPH to produce glucose\n\n**Key Points**:\n- Occurs in chloroplasts\n- Requires chlorophyll\n- Main source of oxygen in atmosphere\n- Foundation of food chains",
  
  'quadratic': "A quadratic equation is in the form: ax² + bx + c = 0\n\n**Methods to Solve**:\n\n1. **Factoring**: Factor the equation into (x + p)(x + q) = 0\n\n2. **Quadratic Formula**: x = [-b ± √(b² - 4ac)] / 2a\n   - The discriminant (b² - 4ac) determines:\n   - > 0: Two real solutions\n   - = 0: One real solution\n   - < 0: No real solutions\n\n3. **Completing the Square**: Transform to (x + h)² = k form\n\n**Example**: x² - 5x + 6 = 0\nFactoring: (x - 2)(x - 3) = 0\nSolutions: x = 2 or x = 3"
};

export default function AIChatbot({ user }: AIChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: 'assistant',
      content: `Hi ${user?.name}! 👋 I'm your AI study assistant. I can help you with:\n\n• Understanding concepts in Physics, Chemistry, Biology, and Maths\n• Solving problems step-by-step\n• Clarifying doubts\n• Exam preparation tips\n\nWhat would you like to learn about today?`,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [tokenStatus, setTokenStatus] = useState({
    tokens_used_today: 0,
    daily_limit: 50,
    remaining_tokens: 50,
    is_unlimited: false
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    // Fetch token status when component mounts
    const fetchTokenStatus = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const response = await fetch('http://localhost:5000/api/ai/token-status', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setTokenStatus(data.data);
          }
        }
      } catch (error) {
        console.error('Failed to fetch token status:', error);
      }
    };

    fetchTokenStatus();
  }, []);

  const generateResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Check for keywords in user message
    if (lowerMessage.includes('newton') || lowerMessage.includes('motion') || lowerMessage.includes('law')) {
      return aiResponses['newton'];
    } else if (lowerMessage.includes('bond') || lowerMessage.includes('ionic') || lowerMessage.includes('covalent')) {
      return aiResponses['bonding'];
    } else if (lowerMessage.includes('photosynthesis') || lowerMessage.includes('plant')) {
      return aiResponses['photosynthesis'];
    } else if (lowerMessage.includes('quadratic') || lowerMessage.includes('equation')) {
      return aiResponses['quadratic'];
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return "Hello! How can I help you with your studies today? Feel free to ask me anything about Physics, Chemistry, Biology, or Mathematics!";
    } else if (lowerMessage.includes('thank')) {
      return "You're welcome! Feel free to ask if you have any more questions. Happy studying! 📚";
    } else {
      return `I'd be happy to help you with that! For the most accurate answer, could you please provide more details about:\n\n• The specific topic or concept\n• What you're trying to understand\n• Any particular aspect that's confusing\n\nThis will help me give you a better explanation! 😊`;
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Check token limits before sending
    if (!tokenStatus.is_unlimited && tokenStatus.remaining_tokens <= 0) {
      alert('You have reached your daily token limit. Purchase a course or subject to get more tokens.');
      return;
    }

    const userMessage: Message = {
      id: messages.length + 1,
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);
    const currentInput = input;
    setInput('');
    setIsTyping(true);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch('http://localhost:5000/api/ai/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: currentInput,
          session_id: `session_${Date.now()}`
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          const aiMessage: Message = {
            id: messages.length + 2,
            role: 'assistant',
            content: data.data.response,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, aiMessage]);

          // Update token status
          if (data.data.token_info) {
            setTokenStatus(data.data.token_info);
          }
        } else {
          throw new Error(data.message || 'Failed to get AI response');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to get AI response');
      }
    } catch (error) {
      console.error('AI Chat Error:', error);
      const errorMessage: Message = {
        id: messages.length + 2,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-500" />
                  AI Assistant
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3 p-3 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4>Jishu AI</h4>
                    <Badge variant="secondary" className="text-xs">Always Online</Badge>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>✓ 24/7 Availability</p>
                  <p>✓ All Subjects</p>
                  <p>✓ Step-by-step Solutions</p>
                  <p>✓ Concept Explanations</p>
                </div>
              </CardContent>
            </Card>

            {/* Token Status Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-500" />
                  Daily Tokens
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Used Today</span>
                  <span className="font-medium">{tokenStatus.tokens_used_today}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Daily Limit</span>
                  <span className="font-medium">
                    {tokenStatus.is_unlimited ? 'Unlimited' : tokenStatus.daily_limit}
                  </span>
                </div>
                {!tokenStatus.is_unlimited && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Remaining</span>
                      <span className="font-medium text-green-600">{tokenStatus.remaining_tokens}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, (tokenStatus.tokens_used_today / tokenStatus.daily_limit) * 100)}%`
                        }}
                      ></div>
                    </div>
                  </>
                )}
                {tokenStatus.is_unlimited && (
                  <Badge variant="secondary" className="w-full justify-center">
                    Unlimited Access
                  </Badge>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-500" />
                  Quick Topics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickQuestions.map((q, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    className="w-full justify-start text-left h-auto py-3"
                    onClick={() => handleQuickQuestion(q.text)}
                  >
                    <div className="flex items-start gap-2 w-full">
                      {q.icon}
                      <div className="flex-1">
                        <p className="text-sm">{q.text}</p>
                        <Badge variant="secondary" className="text-xs mt-1">
                          {q.category}
                        </Badge>
                      </div>
                    </div>
                  </Button>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none">
              <CardContent className="p-4 space-y-2 text-sm">
                <h4 className="flex items-center gap-2">💡 Pro Tip</h4>
                <p className="text-gray-700">
                  Ask specific questions for better answers. For example: "Explain the Krebs cycle step by step"
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-12rem)] flex flex-col">
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="w-6 h-6 text-purple-600" />
                    AI Doubt Solver
                  </CardTitle>
                  <Badge>Chat History: {messages.length - 1}</Badge>
                </div>
              </CardHeader>
              
              {/* Messages */}
              <div className="flex-1 p-6 overflow-y-auto">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.role === 'assistant' && (
                        <Avatar className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500">
                          <AvatarFallback className="bg-transparent">
                            <Bot className="w-5 h-5 text-white" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                      
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        <span className={`text-xs mt-2 block ${
                          message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      
                      {message.role === 'user' && (
                        <Avatar className="w-8 h-8">
                          <AvatarFallback>
                            <User className="w-5 h-5" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex gap-3">
                      <Avatar className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500">
                        <AvatarFallback className="bg-transparent">
                          <Bot className="w-5 h-5 text-white" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-gray-100 rounded-2xl px-4 py-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* Input Area */}
              <div className="border-t p-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask me anything about Physics, Chemistry, Biology, or Maths..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleSend} 
                    disabled={!input.trim() || isTyping}
                    size="icon"
                    className="bg-gradient-to-r from-purple-600 to-pink-600"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Press Enter to send • AI responses are for educational guidance only
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
