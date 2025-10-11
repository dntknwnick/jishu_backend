import { useState } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/alert-dialog';
import { 
  Search, 
  UserCheck,
  UserX,
  Shield,
  Mail,
  MoreVertical,
  Eye,
  Ban,
  CheckCircle2
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { toast } from 'sonner@2.0.3';

interface ManageUsersProps {
  user: any;
}

export default function ManageUsers({ user }: ManageUsersProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  
  const [users, setUsers] = useState([
    {
      id: 1,
      name: 'Priya Sharma',
      email: 'priya@example.com',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Priya',
      role: 'user',
      status: 'active',
      course: 'NEET',
      joinedDate: '2025-01-15',
      lastLogin: '2025-02-09',
      testsCompleted: 47,
      purchaseCount: 3,
      totalSpent: 1497
    },
    {
      id: 2,
      name: 'Rahul Kumar',
      email: 'rahul@example.com',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rahul',
      role: 'user',
      status: 'active',
      course: 'JEE Advanced',
      joinedDate: '2025-01-20',
      lastLogin: '2025-02-09',
      testsCompleted: 38,
      purchaseCount: 2,
      totalSpent: 1198
    },
    {
      id: 3,
      name: 'Ananya Patel',
      email: 'ananya@example.com',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Ananya',
      role: 'user',
      status: 'inactive',
      course: 'NEET',
      joinedDate: '2024-12-10',
      lastLogin: '2025-01-15',
      testsCompleted: 82,
      purchaseCount: 4,
      totalSpent: 1996
    },
    {
      id: 4,
      name: 'Vikram Singh',
      email: 'vikram@example.com',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Vikram',
      role: 'user',
      status: 'suspended',
      course: 'JEE Mains',
      joinedDate: '2025-02-01',
      lastLogin: '2025-02-05',
      testsCompleted: 12,
      purchaseCount: 1,
      totalSpent: 499
    },
    {
      id: 5,
      name: 'Dr. Amit Gupta',
      email: 'amit@jishu.com',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Amit',
      role: 'admin',
      status: 'active',
      course: '-',
      joinedDate: '2024-01-01',
      lastLogin: '2025-02-09',
      testsCompleted: 0,
      purchaseCount: 0,
      totalSpent: 0
    }
  ]);

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    return matchesSearch && matchesStatus && matchesRole;
  });

  const handleToggleStatus = (userId: number) => {
    setUsers(users.map(u =>
      u.id === userId
        ? { ...u, status: u.status === 'active' ? 'inactive' : 'active' }
        : u
    ));
    toast.success('User status updated!');
  };

  const handleSuspendUser = (userId: number) => {
    setUsers(users.map(u =>
      u.id === userId ? { ...u, status: 'suspended' } : u
    ));
    toast.success('User suspended!');
  };

  const handleReactivateUser = (userId: number) => {
    setUsers(users.map(u =>
      u.id === userId ? { ...u, status: 'active' } : u
    ));
    toast.success('User reactivated!');
  };

  const handleDeleteUser = (userId: number) => {
    setUsers(users.filter(u => u.id !== userId));
    toast.success('User deleted permanently!');
  };

  const handlePromoteToAdmin = (userId: number) => {
    setUsers(users.map(u =>
      u.id === userId ? { ...u, role: 'admin' } : u
    ));
    toast.success('User promoted to admin!');
  };

  const stats = [
    {
      label: 'Total Users',
      value: users.length.toString(),
      icon: <UserCheck className="w-6 h-6 text-blue-600" />
    },
    {
      label: 'Active Users',
      value: users.filter(u => u.status === 'active').length.toString(),
      icon: <CheckCircle2 className="w-6 h-6 text-green-600" />
    },
    {
      label: 'Suspended',
      value: users.filter(u => u.status === 'suspended').length.toString(),
      icon: <Ban className="w-6 h-6 text-red-600" />
    },
    {
      label: 'Admins',
      value: users.filter(u => u.role === 'admin').length.toString(),
      icon: <Shield className="w-6 h-6 text-purple-600" />
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Manage Users</h1>
          <p className="text-xl text-gray-600">View and moderate user accounts</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => (
            <Card key={idx}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  {stat.icon}
                </div>
                <p className="text-3xl">{stat.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search users..."
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
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                </SelectContent>
              </Select>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  <SelectItem value="user">Users</SelectItem>
                  <SelectItem value="admin">Admins</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Users ({filteredUsers.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Course</TableHead>
                  <TableHead>Tests</TableHead>
                  <TableHead>Total Spent</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage src={user.avatar} alt={user.name} />
                          <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p>{user.name}</p>
                          <p className="text-xs text-gray-600">{user.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                        {user.role === 'admin' && <Shield className="w-3 h-3 mr-1" />}
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>{user.course}</TableCell>
                    <TableCell>{user.testsCompleted}</TableCell>
                    <TableCell>₹{user.totalSpent.toLocaleString()}</TableCell>
                    <TableCell>{user.joinedDate}</TableCell>
                    <TableCell>{user.lastLogin}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          user.status === 'active' ? 'default' :
                          user.status === 'inactive' ? 'secondary' :
                          'destructive'
                        }
                      >
                        {user.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Mail className="w-4 h-4 mr-2" />
                            Send Email
                          </DropdownMenuItem>
                          {user.role !== 'admin' && (
                            <DropdownMenuItem onClick={() => handlePromoteToAdmin(user.id)}>
                              <Shield className="w-4 h-4 mr-2" />
                              Make Admin
                            </DropdownMenuItem>
                          )}
                          {user.status === 'suspended' ? (
                            <DropdownMenuItem onClick={() => handleReactivateUser(user.id)}>
                              <CheckCircle2 className="w-4 h-4 mr-2" />
                              Reactivate
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem onClick={() => handleSuspendUser(user.id)}>
                              <Ban className="w-4 h-4 mr-2" />
                              Suspend
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem onClick={() => handleToggleStatus(user.id)}>
                            <UserX className="w-4 h-4 mr-2" />
                            {user.status === 'active' ? 'Deactivate' : 'Activate'}
                          </DropdownMenuItem>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                                <UserX className="w-4 h-4 mr-2 text-red-600" />
                                <span className="text-red-600">Delete User</span>
                              </DropdownMenuItem>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete User?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  This will permanently delete {user.name}'s account and all associated data. This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction 
                                  onClick={() => handleDeleteUser(user.id)}
                                  className="bg-red-600 hover:bg-red-700"
                                >
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
