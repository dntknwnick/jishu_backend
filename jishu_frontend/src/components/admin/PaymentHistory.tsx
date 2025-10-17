import { useState, useEffect } from 'react';
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
  Calendar,
  Loader2,
  ChevronLeft,
  ChevronRight
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
import { adminApi } from '../../services/api';

interface PaymentHistoryProps {
  user: any;
}

export default function PaymentHistory({ user }: PaymentHistoryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage] = useState(10);

  const [purchases, setPurchases] = useState<any[]>([]);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch purchases from API
  useEffect(() => {
    const fetchPurchases = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // For now, we'll fetch all users and their purchases
        // In a real scenario, you'd have a dedicated endpoint for all purchases
        const response = await adminApi.getUsers(currentPage, perPage, searchQuery);

        // Transform user data to purchase-like format
        const purchaseData = response.data?.users?.map((user: any) => ({
          id: user.id,
          user_id: user.id,
          user_name: user.name,
          email: user.email_id,
          amount: 0,
          status: user.status === 'active' ? 'completed' : 'pending',
          purchase_date: user.created_at,
          purchase_type: user.is_premium ? 'premium' : 'free'
        })) || [];

        setPurchases(purchaseData);
        setPagination(response.data?.pagination || { page: 1, pages: 1, total: 0, per_page: 10 });
      } catch (err: any) {
        setError(err.message || 'Failed to fetch purchases');
        toast.error('Failed to load purchases');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPurchases();
  }, [currentPage, searchQuery, statusFilter, perPage]);

  const revenueData = [
    { date: 'Feb 3', revenue: 45000, transactions: 92 },
    { date: 'Feb 4', revenue: 52000, transactions: 108 },
    { date: 'Feb 5', revenue: 48000, transactions: 95 },
    { date: 'Feb 6', revenue: 61000, transactions: 124 },
    { date: 'Feb 7', revenue: 58000, transactions: 115 },
    { date: 'Feb 8', revenue: 64000, transactions: 132 },
    { date: 'Feb 9', revenue: 71000, transactions: 145 }
  ];

  const filteredPurchases = purchases.filter(purchase => {
    const matchesSearch =
      purchase.user_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      purchase.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || purchase.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalRevenue = purchases
    .filter(p => p.status === 'completed')
    .reduce((sum, p) => sum + (p.amount || 0), 0);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= pagination.pages) {
      setCurrentPage(newPage);
    }
  };

  const pendingAmount = purchases
    .filter(p => p.status === 'pending')
    .reduce((sum, p) => sum + (p.amount || 0), 0);

  const failedAmount = purchases
    .filter(p => p.status === 'failed')
    .reduce((sum, p) => sum + (p.amount || 0), 0);

  const stats = [
    {
      label: 'Total Users',
      value: pagination.total,
      change: '+12.3%',
      icon: <DollarSign className="w-6 h-6 text-green-600" />,
      color: 'bg-green-50'
    },
    {
      label: 'Active Users',
      value: purchases.filter(p => p.status === 'completed').length,
      change: '+8.5%',
      icon: <CheckCircle2 className="w-6 h-6 text-blue-600" />,
      color: 'bg-blue-50'
    },
    {
      label: 'Premium Users',
      value: purchases.filter(p => p.purchase_type === 'premium').length,
      change: '+5.2%',
      icon: <TrendingUp className="w-6 h-6 text-purple-600" />,
      color: 'bg-purple-50'
    },
    {
      label: 'Total Revenue',
      value: `₹${(totalRevenue / 1000).toFixed(1)}K`,
      change: '+23.5%',
      icon: <CreditCard className="w-6 h-6 text-orange-600" />,
      color: 'bg-orange-50'
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
    <div className="min-h-screen bg-background dark:bg-slate-900">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-foreground">Payment History & Reconciliation</h1>
            <p className="text-xl text-muted-foreground dark:text-muted-foreground">Monitor transactions and revenue</p>
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
                <div className={`w-12 h-12 ${stat.color} dark:bg-gray-800 rounded-lg flex items-center justify-center mb-4`}>
                  {stat.icon}
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground">{stat.label}</p>
                  <p className="text-3xl text-foreground">{stat.value}</p>
                  <p className="text-xs text-muted-foreground dark:text-muted-foreground">{stat.change}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Revenue Chart */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">Revenue Trend</CardTitle>
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
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
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
                  <SelectItem value="completed">Active</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Transactions Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>All Users ({pagination.total})</CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <TrendingUp className="w-4 h-4" />
                <span>Page {pagination.page} of {pagination.pages}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin mr-2" />
                <span>Loading users...</span>
              </div>
            ) : error ? (
              <div className="text-center py-8 text-red-600">
                <p>{error}</p>
              </div>
            ) : purchases.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No users found</p>
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User ID</TableHead>
                      <TableHead>User Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Join Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredPurchases.map((purchase) => (
                      <TableRow key={purchase.id}>
                        <TableCell>
                          <p className="font-mono text-sm">#{purchase.user_id}</p>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{purchase.user_name}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <p className="text-sm">{purchase.email}</p>
                        </TableCell>
                        <TableCell>
                          <Badge variant={purchase.purchase_type === 'premium' ? 'default' : 'secondary'}>
                            {purchase.purchase_type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <p className="text-sm">{new Date(purchase.purchase_date).toLocaleDateString()}</p>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              purchase.status === 'completed' ? 'default' :
                              purchase.status === 'pending' ? 'secondary' :
                              'destructive'
                            }
                            className="gap-1"
                          >
                            {getStatusIcon(purchase.status)}
                            {purchase.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm">
                              View
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="text-sm text-muted-foreground">
                    Page {pagination.page} of {pagination.pages} ({pagination.total} total users)
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === pagination.pages}
                    >
                      Next
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>


      </div>
    </div>
  );
}
