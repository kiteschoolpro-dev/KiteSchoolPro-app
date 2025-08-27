import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Menu, X, User, Calendar, Settings, LogOut, 
  Wind, Users, BarChart3, Home 
} from 'lucide-react';

export default function Layout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = {
    customer: [
      { name: 'Browse Courses', href: '/courses', icon: Wind },
      { name: 'My Bookings', href: '/bookings', icon: Calendar },
      { name: 'Profile', href: '/profile', icon: User },
    ],
    instructor: [
      { name: 'My Schedule', href: '/instructor/schedule', icon: Calendar },
      { name: 'My Students', href: '/instructor/students', icon: Users },
      { name: 'Profile', href: '/profile', icon: User },
    ],
    admin: [
      { name: 'Dashboard', href: '/admin/dashboard', icon: BarChart3 },
      { name: 'Bookings', href: '/admin/bookings', icon: Calendar },
      { name: 'Instructors', href: '/admin/instructors', icon: Users },
      { name: 'Courses', href: '/admin/courses', icon: Wind },
      { name: 'Settings', href: '/admin/settings', icon: Settings },
    ],
    owner: [
      { name: 'Dashboard', href: '/admin/dashboard', icon: BarChart3 },
      { name: 'Bookings', href: '/admin/bookings', icon: Calendar },
      { name: 'Instructors', href: '/admin/instructors', icon: Users },
      { name: 'Courses', href: '/admin/courses', icon: Wind },
      { name: 'Settings', href: '/admin/settings', icon: Settings },
    ]
  };

  const currentNavigation = navigation[currentUser?.role] || navigation.customer;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Brand */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <Wind className="h-8 w-8 text-blue-600" />
                <span className="font-bold text-xl text-gray-900">KiteSchool Pro</span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              {currentNavigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname === item.href
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {currentUser && (
                <>
                  <span className="hidden md:block text-sm text-gray-700">
                    {currentUser.first_name} {currentUser.last_name}
                  </span>
                  <div className="hidden md:block">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      currentUser.role === 'admin' || currentUser.role === 'owner' 
                        ? 'bg-purple-100 text-purple-800'
                        : currentUser.role === 'instructor'
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {currentUser.role}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-700 hover:text-red-600 transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    <span className="hidden md:block">Logout</span>
                  </button>
                </>
              )}

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                {mobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {currentNavigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium ${
                      location.pathname === item.href
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
              
              {currentUser && (
                <div className="border-t pt-4 mt-4">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-gray-900">
                      {currentUser.first_name} {currentUser.last_name}
                    </p>
                    <p className="text-sm text-gray-500 capitalize">
                      {currentUser.role}
                    </p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 w-full px-3 py-2 text-left text-base font-medium text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="h-5 w-5" />
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}