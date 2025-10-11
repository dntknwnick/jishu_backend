import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Target, BookOpen, BarChart3, Users, MessageSquare, Menu, Settings, LogOut, User, Shield } from 'lucide-react';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import ThemeToggle from './ThemeToggle';

interface HeaderProps {
  user: any;
}

export default function Header({ user }: HeaderProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = user?.is_admin === true;

  // Debug: Log admin status
  console.log('Header - User:', user);
  console.log('Header - Is Admin:', isAdmin);
  console.log('Header - user.is_admin:', user?.is_admin);

  const userNavItems = [
    { path: '/courses', label: 'Courses', icon: <BookOpen className="w-4 h-4" /> },
    { path: '/results', label: 'Results', icon: <BarChart3 className="w-4 h-4" /> },
    { path: '/community', label: 'Community', icon: <Users className="w-4 h-4" /> },
    { path: '/chatbot', label: 'AI Chatbot', icon: <MessageSquare className="w-4 h-4" /> },
  ];

  const adminNavItems = [
    { path: '/admin', label: 'Dashboard', icon: <BarChart3 className="w-4 h-4" /> },
    { path: '/admin/courses', label: 'Courses', icon: <BookOpen className="w-4 h-4" /> },
    { path: '/admin/posts', label: 'Posts', icon: <Users className="w-4 h-4" /> },
    { path: '/admin/users', label: 'Users', icon: <User className="w-4 h-4" /> },
    { path: '/admin/payments', label: 'Payments', icon: <Settings className="w-4 h-4" /> },
  ];

  const navItems = isAdmin ? adminNavItems : userNavItems;

  return (
    <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to={isAdmin ? '/admin' : '/courses'} className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Target className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent hidden sm:inline">
            Jishu App
          </span>
          {isAdmin && (
            <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-md flex items-center gap-1">
              <Shield className="w-3 h-3" />
              Admin
            </span>
          )}
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => (
            <Button
              key={item.path}
              variant={location.pathname === item.path ? 'default' : 'ghost'}
              size="sm"
              className="gap-2"
              onClick={() => navigate(item.path)}
            >
              {item.icon}
              {item.label}
            </Button>
          ))}
        </nav>

        {/* User Menu */}
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="sm">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64">
              <div className="flex flex-col gap-4 mt-8">
                {navItems.map((item) => (
                  <Button
                    key={item.path}
                    variant={location.pathname === item.path ? 'default' : 'ghost'}
                    className="w-full justify-start gap-2"
                    onClick={() => navigate(item.path)}
                  >
                    {item.icon}
                    {item.label}
                  </Button>
                ))}
              </div>
            </SheetContent>
          </Sheet>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar>
                  <AvatarImage src={user?.avatar} alt={user?.name} />
                  <AvatarFallback>{user?.name?.charAt(0) || 'U'}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <div className="flex items-center gap-2">
                    <p>{user?.name}</p>
                    {isAdmin && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        <Shield className="w-3 h-3 mr-1" />
                        Admin
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{user?.email_id}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {!isAdmin && (
                <>
                  <DropdownMenuItem className="cursor-pointer" onClick={() => navigate('/profile')}>
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer" onClick={() => navigate('/account')}>
                    <Settings className="mr-2 h-4 w-4" />
                    Account Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem className="cursor-pointer text-red-600" onClick={() => navigate('/logout')}>
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
