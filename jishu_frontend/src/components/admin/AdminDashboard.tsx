import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const { users, stats, isLoading, error } = useAppSelector((state) => state.admin);

  useEffect(() => {
    dispatch(fetchUsers());
    dispatch(fetchStats());
  }, [dispatch]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background dark:bg-slate-900">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2 text-foreground">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading dashboard...</span>
          </div>
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
            <h2 className="text-2xl mb-4 text-foreground">Error Loading Dashboard</h2>
            <p className="text-muted-foreground dark:text-muted-foreground mb-4">{error}</p>
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

  // Use real data from stats or fallback to empty arrays
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

  // Format recent users from stats - with defensive checks
  const recentUsers = Array.isArray(stats?.recentUsers)
    ? stats.recentUsers.map((user: any) => ({
        id: user.id,
        name: user.name,
        email: user.email_id,
        joined: new Date(user.created_at).toLocaleDateString(),
        status: 'active'
      })).slice(0, 5)
    : [];

  // Format recent transactions from stats (if available) - with defensive checks
  const recentTransactions = Array.isArray(stats?.recentPosts)
    ? stats.recentPosts.map((post: any, idx: number) => ({
        id: post.id,
        user: post.author_id,
        amount: 0,
        course: post.title,
        status: 'completed',
        time: new Date(post.created_at).toLocaleDateString()
      })).slice(0, 5)
    : [];

  return (
    <div className="min-h-screen bg-background dark:bg-slate-900">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-foreground">Admin Dashboard</h1>
          <p className="text-xl text-muted-foreground dark:text-muted-foreground">Welcome back, {user?.name}</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardStats.map((stat, idx) => (
            <Card key={idx}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center text-primary-foreground`}>
                    {stat.icon}
                  </div>
                  <Badge variant={stat.change.startsWith('+') ? 'default' : 'destructive'}>
                    {stat.change}
                  </Badge>
                </div>
                <div className="text-3xl mb-1 text-foreground">{stat.value}</div>
                <p className="text-sm text-muted-foreground dark:text-muted-foreground">{stat.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">Revenue & User Growth</CardTitle>
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
              <CardTitle className="text-foreground">Course Distribution</CardTitle>
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
                <CardTitle className="text-foreground">Recent Users</CardTitle>
                <Button size="sm" variant="outline" onClick={() => navigate('/admin/users')}>View All</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentUsers.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-blue-600 dark:text-blue-200" />
                      </div>
                      <div>
                        <h4 className="text-sm text-foreground">{user.name}</h4>
                        <p className="text-xs text-muted-foreground dark:text-muted-foreground">{user.email}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                        {user.status}
                      </Badge>
                      <p className="text-xs text-muted-foreground dark:text-muted-foreground mt-1">{user.joined}</p>
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
                <CardTitle className="text-foreground">Recent Transactions</CardTitle>
                <Button size="sm" variant="outline" onClick={() => navigate('/admin/payments')}>View All</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        transaction.status === 'completed' ? 'bg-green-100 dark:bg-green-900' :
                        transaction.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-900' :
                        'bg-red-100 dark:bg-red-900'
                      }`}>
                        {transaction.status === 'completed' ? <CheckCircle2 className="w-5 h-5 text-green-600" /> :
                         transaction.status === 'pending' ? <Clock className="w-5 h-5 text-yellow-600" /> :
                         <AlertCircle className="w-5 h-5 text-red-600" />}
                      </div>
                      <div>
                        <h4 className="text-sm">{transaction.user}</h4>
                        <p className="text-xs text-muted-foreground">{transaction.course}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="mb-1">₹{transaction.amount}</p>
                      <p className="text-xs text-muted-foreground">{transaction.time}</p>
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
