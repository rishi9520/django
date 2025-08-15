import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, message } from 'antd';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import TeacherManagement from './pages/TeacherManagement';
import AttendanceManagement from './pages/AttendanceManagement';
import ArrangementManagement from './pages/ArrangementManagement';
import ScheduleManagement from './pages/ScheduleManagement';
import Reports from './pages/Reports';
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
            <Route path="/" element={<Dashboard user={user} />} />
            <Route path="/dashboard" element={<Dashboard user={user} />} />
            <Route path="/teachers" element={<TeacherManagement user={user} />} />
            <Route path="/attendance" element={<AttendanceManagement user={user} />} />
            <Route path="/arrangements" element={<ArrangementManagement user={user} />} />
            <Route path="/schedules" element={<ScheduleManagement user={user} />} />
            <Route path="/reports" element={<Reports user={user} />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;