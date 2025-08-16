import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, message } from 'antd';
import LoginPage from './pages/LoginPage';
import ProfessionalDashboard from './pages/ProfessionalDashboard';
import TeacherManagement from './pages/TeacherManagement';
import AttendanceManagement from './pages/AttendanceManagement';
import ArrangementManagementPro from './pages/ArrangementManagementPro';
import ReportsManagement from './pages/ReportsManagement';
import BillingManagement from './pages/BillingManagement';
import AdminControls from './pages/AdminControls';
import { apiService } from './services/apiService';
import AppHeader from './components/AppHeader';
import AppSidebar from './components/AppSidebar';

const { Content } = Layout;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    // Check for saved user session
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    message.success('Login successful!');
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
      setUser(null);
      localStorage.removeItem('user');
      message.success('Logout successful!');
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if API call fails
      setUser(null);
      localStorage.removeItem('user');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppSidebar 
        collapsed={sidebarCollapsed}
        onCollapse={setSidebarCollapsed}
        user={user}
      />
      <Layout>
        <AppHeader 
          user={user}
          onLogout={handleLogout}
          onMenuClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        <Content className="mobile-responsive">
          <Routes>
            <Route path="/" element={<ProfessionalDashboard />} />
            <Route path="/dashboard" element={<ProfessionalDashboard />} />
            <Route path="/teachers" element={<TeacherManagement />} />
            <Route path="/attendance" element={<AttendanceManagement />} />
            <Route path="/arrangements" element={<ArrangementManagementPro />} />
            <Route path="/reports" element={<ReportsManagement />} />
            <Route path="/billing" element={<BillingManagement />} />
            <Route path="/admin" element={<AdminControls />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;