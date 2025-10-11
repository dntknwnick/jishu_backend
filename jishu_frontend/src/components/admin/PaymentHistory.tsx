import { useState } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { 
  Search, 
  Download,
  DollarSign,
  TrendingUp,
  CreditCard,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  Filter,
  Calendar
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { toast } from 'sonner@2.0.3';

interface PaymentHistoryProps {
  user: any;
}

export default function PaymentHistory({ user }: PaymentHistoryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [methodFilter, setMethodFilter] = useState('all');

  const [transactions, setTransactions] = useState([
    {
      id: 'TXN001',
      user: 'Priya Sharma',
      email: 'priya@example.com',
      course: 'NEET Complete Bundle',
      amount: 1497,
      method: 'Card',
      status: 'completed',
      date: '2025-02-09 10:30',
      transactionId: 'pay_Abc123XyZ'
    },
    {
      id: 'TXN002',
      user: 'Rahul Kumar',
      email: 'rahul@example.com',
      course: 'JEE Physics Tests',
      amount: 499,
      method: 'UPI',
      status: 'completed',
      date: '2025-02-09 09:15',
      transactionId: 'pay_Def456UvW'
    },
    {
      id: 'TXN003',
      user: 'Ananya Patel',
      email: 'ananya@example.com',
      course: 'NEET Biology Bundle',
      amount: 499,
      method: 'Card',
      status: 'pending',
      date: '2025-02-09 08:45',
      transactionId: 'pay_Ghi789RsT'
    },
    {
      id: 'TXN004',
      user: 'Vikram Singh',
      email: 'vikram@example.com',
      course: 'JEE Mains Bundle',
      amount: 1198,
      method: 'NetBanking',
      status: 'failed',
      date: '2025-02-08 18:20',
      transactionId: 'pay_Jkl012OpQ'
    },
    {
      id: 'TXN005',
      user: 'Sneha Reddy',
      email: 'sneha@example.com',
      course: 'CET Complete Bundle',
      amount: 1197,
      method: 'UPI',
      status: 'completed',
      date: '2025-02-08 16:30',
      transactionId: 'pay_Mno345LmN'
    },
    {
      id: 'TXN006',
      user: 'Karan Shah',
      email: 'karan@example.com',
      course: 'NEET Chemistry Tests',
      amount: 499,
      method: 'Card',
      status: 'refunded',
      date: '2025-02-07 14:10',
      transactionId: 'pay_Pqr678IjK'
    }
  ]);

  const revenueData = [
    { date: 'Feb 3', revenue: 45000, transactions: 92 },
    { date: 'Feb 4', revenue: 52000, transactions: 108 },
    { date: 'Feb 5', revenue: 48000, transactions: 95 },
    { date: 'Feb 6', revenue: 61000, transactions: 124 },
    { date: 'Feb 7', revenue: 58000, transactions: 115 },
    { date: 'Feb 8', revenue: 64000, transactions: 132 },
    { date: 'Feb 9', revenue: 71000, transactions: 145 }
  ];

  const filteredTransactions = transactions.filter(txn => {
    const matchesSearch = 
      txn.user.toLowerCase().includes(searchQuery.toLowerCase()) ||
      txn.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      txn.transactionId.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || txn.status === statusFilter;
    const matchesMethod = methodFilter === 'all' || txn.method === methodFilter;
    return matchesSearch && matchesStatus && matchesMethod;
  });

  const totalRevenue = transactions
    .filter(t => t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0);

  const pendingAmount = transactions
    .filter(t => t.status === 'pending')
    .reduce((sum, t) => sum + t.amount, 0);

  const failedAmount = transactions
    .filter(t => t.status === 'failed')
    .reduce((sum, t) => sum + t.amount, 0);

  const refundedAmount = transactions
    .filter(t => t.status === 'refunded')
    .reduce((sum, t) => sum + t.amount, 0);

  const stats = [
    {
      label: 'Total Revenue',
      value: `₹${(totalRevenue / 1000).toFixed(1)}K`,
      change: '+23.5%',
      icon: <DollarSign className="w-6 h-6 text-green-600" />,
      color: 'bg-green-50'
    },
    {
      label: 'Completed',
      value: transactions.filter(t => t.status === 'completed').length,
      change: '+12.3%',
      icon: <CheckCircle2 className="w-6 h-6 text-blue-600" />,
      color: 'bg-blue-50'
    },
    {
      label: 'Pending',
      value: `₹${pendingAmount}`,
      change: transactions.filter(t => t.status === 'pending').length + ' txns',
      icon: <Clock className="w-6 h-6 text-yellow-600" />,
      color: 'bg-yellow-50'
    },
    {
      label: 'Failed',
      value: `₹${failedAmount}`,
      change: transactions.filter(t => t.status === 'failed').length + ' txns',
      icon: <XCircle className="w-6 h-6 text-red-600" />,
      color: 'bg-red-50'
    }
  ];

  const handleExportCSV = () => {
    toast.success('Exporting transactions to CSV...');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'refunded':
        return <AlertCircle className="w-4 h-4 text-orange-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2">Payment History & Reconciliation</h1>
            <p className="text-xl text-gray-600">Monitor transactions and revenue</p>
          </div>
          <Button onClick={handleExportCSV} className="gap-2">
            <Download className="w-4 h-4" />
            Export CSV
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => (
            <Card key={idx}>
              <CardContent className="p-6">
                <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center mb-4`}>
                  {stat.icon}
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className="text-3xl">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.change}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Revenue Chart */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Revenue Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    name="Revenue (₹)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Transaction Volume</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="transactions" fill="#3b82f6" name="Transactions" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="grid md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search transactions..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                  <SelectItem value="refunded">Refunded</SelectItem>
                </SelectContent>
              </Select>
              <Select value={methodFilter} onValueChange={setMethodFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Payment method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Methods</SelectItem>
                  <SelectItem value="Card">Card</SelectItem>
                  <SelectItem value="UPI">UPI</SelectItem>
                  <SelectItem value="NetBanking">Net Banking</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" className="gap-2">
                <Calendar className="w-4 h-4" />
                Date Range
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Transactions Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>All Transactions ({filteredTransactions.length})</CardTitle>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <TrendingUp className="w-4 h-4" />
                <span>Showing latest transactions</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Transaction ID</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Course</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Method</TableHead>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTransactions.map((txn) => (
                  <TableRow key={txn.id}>
                    <TableCell>
                      <div>
                        <p className="font-mono text-sm">{txn.id}</p>
                        <p className="text-xs text-gray-500 font-mono">{txn.transactionId}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p>{txn.user}</p>
                        <p className="text-xs text-gray-600">{txn.email}</p>
                      </div>
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <p className="truncate">{txn.course}</p>
                    </TableCell>
                    <TableCell>
                      <p className="text-lg">₹{txn.amount}</p>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        <CreditCard className="w-3 h-3 mr-1" />
                        {txn.method}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <p className="text-sm">{txn.date}</p>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          txn.status === 'completed' ? 'default' :
                          txn.status === 'pending' ? 'secondary' :
                          txn.status === 'refunded' ? 'outline' :
                          'destructive'
                        }
                        className="gap-1"
                      >
                        {getStatusIcon(txn.status)}
                        {txn.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm">
                          View
                        </Button>
                        {txn.status === 'completed' && (
                          <Button variant="ghost" size="sm">
                            Refund
                          </Button>
                        )}
                        {txn.status === 'pending' && (
                          <Button variant="ghost" size="sm">
                            Verify
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Reconciliation Summary */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Reconciliation Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  Successful Transactions
                </h4>
                <div className="pl-7 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Completed Payments:</span>
                    <span>{transactions.filter(t => t.status === 'completed').length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Amount:</span>
                    <span className="text-green-600">₹{totalRevenue.toLocaleString()}</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600" />
                  Issues & Refunds
                </h4>
                <div className="pl-7 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Failed Payments:</span>
                    <span className="text-red-600">{transactions.filter(t => t.status === 'failed').length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Refunded Amount:</span>
                    <span className="text-orange-600">₹{refundedAmount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Pending Verification:</span>
                    <span className="text-yellow-600">{transactions.filter(t => t.status === 'pending').length}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
