import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Import pages
import Login from './pages/Login';
import Register from './pages/Register';
import Courses from './pages/Courses';
import BookingFlow from './pages/BookingFlow';

// Placeholder components for routes we haven't built yet
const HomePage = () => {
  const { currentUser } = useAuth();
  
  if (!currentUser) {
    return <Navigate to="/courses" />;
  }

  // Redirect based on role
  if (currentUser.role === 'customer') {
    return <Navigate to="/courses" />;
  } else if (currentUser.role === 'instructor') {
    return <Navigate to="/instructor/schedule" />;
  } else {
    return <Navigate to="/admin/dashboard" />;
  }
};

const BookingsPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">My Bookings</h1>
    <p className="text-gray-600">Bookings management coming soon!</p>
  </div>
);

const ProfilePage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Profile</h1>
    <p className="text-gray-600">Profile management coming soon!</p>
  </div>
);

const InstructorSchedulePage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">My Schedule</h1>
    <p className="text-gray-600">Instructor schedule coming soon!</p>
  </div>
);

const InstructorStudentsPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">My Students</h1>
    <p className="text-gray-600">Student management coming soon!</p>
  </div>
);

const AdminDashboardPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Admin Dashboard</h1>
    <p className="text-gray-600">Admin dashboard coming soon!</p>
  </div>
);

const AdminBookingsPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Manage Bookings</h1>
    <p className="text-gray-600">Booking management coming soon!</p>
  </div>
);

const AdminInstructorsPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Manage Instructors</h1>
    <p className="text-gray-600">Instructor management coming soon!</p>
  </div>
);

const AdminCoursesPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Manage Courses</h1>
    <p className="text-gray-600">Course management coming soon!</p>
  </div>
);

const AdminSettingsPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Settings</h1>
    <p className="text-gray-600">Settings coming soon!</p>
  </div>
);

const UnauthorizedPage = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Unauthorized</h1>
    <p className="text-gray-600">You don't have permission to access this page.</p>
  </div>
);

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected Routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <HomePage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/courses" element={
        <ProtectedRoute>
          <Layout>
            <Courses />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/courses/:courseId/book" element={
        <ProtectedRoute requiredRole={['customer']}>
          <Layout>
            <BookingFlow />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/bookings" element={
        <ProtectedRoute requiredRole={['customer']}>
          <Layout>
            <BookingsPage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/profile" element={
        <ProtectedRoute>
          <Layout>
            <ProfilePage />
          </Layout>
        </ProtectedRoute>
      } />

      {/* Instructor Routes */}
      <Route path="/instructor/schedule" element={
        <ProtectedRoute requiredRole={['instructor']}>
          <Layout>
            <InstructorSchedulePage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/instructor/students" element={
        <ProtectedRoute requiredRole={['instructor']}>
          <Layout>
            <InstructorStudentsPage />
          </Layout>
        </ProtectedRoute>
      } />

      {/* Admin Routes */}
      <Route path="/admin/dashboard" element={
        <ProtectedRoute requiredRole={['admin', 'owner']}>
          <Layout>
            <AdminDashboardPage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin/bookings" element={
        <ProtectedRoute requiredRole={['admin', 'owner']}>
          <Layout>
            <AdminBookingsPage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin/instructors" element={
        <ProtectedRoute requiredRole={['admin', 'owner']}>
          <Layout>
            <AdminInstructorsPage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin/courses" element={
        <ProtectedRoute requiredRole={['admin', 'owner']}>
          <Layout>
            <AdminCoursesPage />
          </Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin/settings" element={
        <ProtectedRoute requiredRole={['admin', 'owner']}>
          <Layout>
            <AdminSettingsPage />
          </Layout>
        </ProtectedRoute>
      } />

      {/* Error Pages */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      
      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
