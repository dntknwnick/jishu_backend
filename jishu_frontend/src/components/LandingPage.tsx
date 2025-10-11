import { Link } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { BookOpen, Brain, BarChart3, Users, CheckCircle, Award, Target, Zap } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

export default function LandingPage() {
  const features = [
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "Mock Tests",
      description: "Practice with thousands of MCQ questions designed by experts"
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "AI Doubt Solver",
      description: "Get instant answers to your questions with our intelligent chatbot"
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Learning Analytics",
      description: "Track your progress with detailed insights and performance metrics"
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Community Blog",
      description: "Connect with fellow students, share tips and stay motivated"
    }
  ];

  const exams = [
    { name: "NEET", icon: "🩺" },
    { name: "JEE Advanced", icon: "🔬" },
    { name: "CET", icon: "📐" },
    { name: "JEE Mains", icon: "⚛️" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Jishu App
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-gray-700 hover:text-blue-600 transition">Features</a>
            <a href="#exams" className="text-gray-700 hover:text-blue-600 transition">Exams</a>
            <a href="#about" className="text-gray-700 hover:text-blue-600 transition">About</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/auth">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link to="/auth">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 md:py-28">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full">
              <Zap className="w-4 h-4" />
              <span className="text-sm">Trusted by 50,000+ Students</span>
            </div>
            <h1 className="text-5xl md:text-6xl">
              Ace Your <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Competitive Exams</span> with Confidence
            </h1>
            <p className="text-xl text-gray-600">
              Prepare for NEET, JEE, CET and more with AI-powered mock tests, detailed analytics, and a supportive community.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/auth">
                <Button size="lg" className="w-full sm:w-auto">
                  Start Free Trial
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                Watch Demo
              </Button>
            </div>
            <div className="flex items-center gap-8 pt-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-gray-600">No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-600" />
                <span className="text-gray-600">Expert-crafted tests</span>
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-400 rounded-3xl blur-3xl opacity-20"></div>
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1639548538099-6f7f9aec3b92?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50cyUyMHN0dWR5aW5nJTIwZWR1Y2F0aW9ufGVufDF8fHx8MTc2MDAwNDg3MXww&ixlib=rb-4.1.0&q=80&w=1080"
              alt="Students studying"
              className="relative rounded-3xl shadow-2xl w-full h-[500px] object-cover"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl mb-4">Everything You Need to Succeed</h2>
            <p className="text-xl text-gray-600">Comprehensive tools designed for serious exam preparation</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-none shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6 space-y-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center text-blue-600">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Exams Section */}
      <section id="exams" className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl mb-4">Prepare for All Major Exams</h2>
            <p className="text-xl text-gray-600">Comprehensive test series for every competitive exam</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {exams.map((exam, index) => (
              <Card key={index} className="hover:shadow-lg transition-all cursor-pointer hover:scale-105">
                <CardContent className="p-8 text-center space-y-3">
                  <div className="text-5xl">{exam.icon}</div>
                  <h3 className="text-xl">{exam.name}</h3>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-5xl mb-2">50K+</div>
              <div className="text-blue-100">Active Students</div>
            </div>
            <div>
              <div className="text-5xl mb-2">10K+</div>
              <div className="text-blue-100">Mock Tests</div>
            </div>
            <div>
              <div className="text-5xl mb-2">95%</div>
              <div className="text-blue-100">Success Rate</div>
            </div>
            <div>
              <div className="text-5xl mb-2">24/7</div>
              <div className="text-blue-100">AI Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-xl">
            <CardContent className="p-12 text-center space-y-6">
              <h2 className="text-4xl">Ready to Start Your Journey?</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Join thousands of students who are already preparing smarter, not harder
              </p>
              <Link to="/auth">
                <Button size="lg" className="mt-4">
                  Create Free Account
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl text-white">Jishu App</span>
              </div>
              <p className="text-sm">Empowering students to achieve their dreams through smart exam preparation.</p>
            </div>
            <div>
              <h4 className="text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Mock Tests</a></li>
                <li><a href="#" className="hover:text-white transition">AI Chatbot</a></li>
                <li><a href="#" className="hover:text-white transition">Analytics</a></li>
                <li><a href="#" className="hover:text-white transition">Community</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white mb-4">Exams</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">NEET</a></li>
                <li><a href="#" className="hover:text-white transition">JEE Advanced</a></li>
                <li><a href="#" className="hover:text-white transition">JEE Mains</a></li>
                <li><a href="#" className="hover:text-white transition">CET</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">About Us</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
                <li><a href="#" className="hover:text-white transition">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>© 2025 Jishu App. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
