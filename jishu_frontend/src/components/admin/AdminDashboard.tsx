import { useEffect } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  Users,
  BookOpen,
  DollarSign,
  TrendingUp,
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2
} from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../store';
import { fetchUsers, fetchStats } from '../../store/slices/adminSlice';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface AdminDashboardProps {
  user: any;
}

export default function AdminDashboard({ user }: AdminDashboardProps) {
  const dispatch = useAppDispatch();
  const { users, stats, isLoading, error } = useAppSelector((state) => state.admin);

  useEffect(() => {
    dispatch(fetchUsers());
    dispatch(fetchStats());
  }, [dispatch]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading dashboard...</span>
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
            <h2 className="text-2xl mb-4">Error Loading Dashboard</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => {
              dispatch(fetchUsers());
              dispatch(fetchStats());
            }}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const dashboardStats = [
    {
      label: 'Total Users',
      value: stats?.totalUsers?.toString() || '0',
      change: '+12.5%',
      icon: <Users className="w-6 h-6" />,
      color: 'bg-blue-500'
    },
    {
      label: 'Active Tests',
      value: stats?.totalTests?.toString() || '0',
      change: '+8.2%',
      icon: <BookOpen className="w-6 h-6" />,
      color: 'bg-green-500'
    },
    {
      label: 'Monthly Revenue',
      value: `₹${stats?.totalRevenue ? (stats.totalRevenue / 100000).toFixed(1) + 'L' : '0'}`,
      change: '+23.1%',
      icon: <DollarSign className="w-6 h-6" />,
      color: 'bg-purple-500'
    },
    {
      label: 'Avg. Score',
      value: stats?.averageScore ? `${stats.averageScore.toFixed(1)}%` : '0%',
      change: '+3.2%',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'bg-yellow-500'
    }
  ];

  const revenueData = [
    { month: 'Jan', revenue: 18.5, users: 4200 },
    { month: 'Feb', revenue: 22.3, users: 5100 },
    { month: 'Mar', revenue: 19.8, users: 4800 },
    { month: 'Apr', revenue: 24.6, users: 5600 },
    { month: 'May', revenue: 26.2, users: 6200 },
    { month: 'Jun', revenue: 28.5, users: 6800 }
  ];

  const courseDistribution = [
    { name: 'NEET', value: 45, color: '#ef4444' },
    { name: 'JEE Advanced', value: 30, color: '#3b82f6' },
    { name: 'JEE Mains', value: 18, color: '#8b5cf6' },
    { name: 'CET', value: 7, color: '#10b981' }
  ];

  const recentUsers = [
    { id: 1, name: 'Priya Sharma', email: 'priya@example.com', course: 'NEET', joined: '2 hours ago', status: 'active' },
    { id: 2, name: 'Rahul Kumar', email: 'rahul@example.com', course: 'JEE Advanced', joined: '5 hours ago', status: 'active' },
    { id: 3, name: 'Ananya Patel', email: 'ananya@example.com', course: 'NEET', joined: '1 day ago', status: 'active' },
    { id: 4, name: 'Vikram Singh', email: 'vikram@example.com', course: 'JEE Mains', joined: '1 day ago', status: 'pending' },
    { id: 5, name: 'Sneha Reddy', email: 'sneha@example.com', course: 'CET', joined: '2 days ago', status: 'active' }
  ];

  const recentTransactions = [
    { id: 1, user: 'John Doe', amount: 1497, course: 'NEET Bundle', status: 'completed', time: '10 mins ago' },
    { id: 2, user: 'Jane Smith', amount: 499, course: 'Physics Tests', status: 'completed', time: '25 mins ago' },
    { id: 3, user: 'Mike Johnson', amount: 1797, course: 'JEE Bundle', status: 'pending', time: '1 hour ago' },
    { id: 4, user: 'Sarah Williams', amount: 499, course: 'Chemistry Tests', status: 'completed', time: '2 hours ago' },
    { id: 5, user: 'David Brown', amount: 399, course: 'Biology Tests', status: 'failed', time: '3 hours ago' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Admin Dashboard</h1>
          <p className="text-xl text-gray-600">Welcome back, {user?.name}</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardStats.map((stat, idx) => (
            <Card key={idx}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center text-white`}>
                    {stat.icon}
                  </div>
                  <Badge variant={stat.change.startsWith('+') ? 'default' : 'destructive'}>
                    {stat.change}
                  </Badge>
                </div>
                <div className="text-3xl mb-1">{stat.value}</div>
                <p className="text-sm text-gray-600">{stat.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue & User Growth</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#8b5cf6" 
                    strokeWidth={2}
                    name="Revenue (₹L)"
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="users" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="New Users"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Course Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Course Distribution</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={courseDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {courseDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Recent Users */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Users</CardTitle>
                <Button size="sm" variant="outline">View All</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentUsers.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="text-sm">{user.name}</h4>
                        <p className="text-xs text-gray-600">{user.email}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                        {user.status}
                      </Badge>
                      <p className="text-xs text-gray-600 mt-1">{user.joined}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Transactions */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Transactions</CardTitle>
                <Button size="sm" variant="outline">View All</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        transaction.status === 'completed' ? 'bg-green-100' :
                        transaction.status === 'pending' ? 'bg-yellow-100' :
                        'bg-red-100'
                      }`}>
                        {transaction.status === 'completed' ? <CheckCircle2 className="w-5 h-5 text-green-600" /> :
                         transaction.status === 'pending' ? <Clock className="w-5 h-5 text-yellow-600" /> :
                         <AlertCircle className="w-5 h-5 text-red-600" />}
                      </div>
                      <div>
                        <h4 className="text-sm">{transaction.user}</h4>
                        <p className="text-xs text-gray-600">{transaction.course}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="mb-1">₹{transaction.amount}</p>
                      <p className="text-xs text-gray-600">{transaction.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Status */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span>API Status</span>
                </div>
                <p className="text-2xl">Operational</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span>Database</span>
                </div>
                <p className="text-2xl">Healthy</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span>Server Load</span>
                </div>
                <p className="text-2xl">42%</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-5 h-5 text-blue-600" />
                  <span>Active Sessions</span>
                </div>
                <p className="text-2xl">8,542</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
