import React from 'react';
import { Layout, Menu, Avatar, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  TeamOutlined,
  CalendarOutlined,
  SwapOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  BookOutlined
} from '@ant-design/icons';

const { Sider } = Layout;
const { Text } = Typography;

const AppSidebar = ({ collapsed, onCollapse, user }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/teachers',
      icon: <TeamOutlined />,
      label: 'Teacher Management',
    },
    {
      key: '/attendance',
      icon: <ClockCircleOutlined />,
      label: 'Attendance',
    },
    {
      key: '/arrangements',
      icon: <SwapOutlined />,
      label: 'Arrangements',
    },
    {
      key: '/schedules',
      icon: <CalendarOutlined />,
      label: 'Schedules',
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: 'Reports',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={onCollapse}
      style={{
        background: '#fff',
        boxShadow: '2px 0 6px rgba(0,21,41,.35)',
      }}
      breakpoint="lg"
      collapsedWidth="80"
    >
      {/* School Logo and Name */}
      <div
        style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          padding: collapsed ? '0' : '0 16px',
          borderBottom: '1px solid #f0f0f0',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        {user?.school_logo ? (
          <Avatar
            src={user.school_logo}
            size={collapsed ? 32 : 40}
            style={{ marginRight: collapsed ? 0 : 12 }}
          />
        ) : (
          <Avatar
            icon={<BookOutlined />}
            size={collapsed ? 32 : 40}
            style={{ 
              backgroundColor: '#40a9ff',
              marginRight: collapsed ? 0 : 12 
            }}
          />
        )}
        {!collapsed && (
          <div>
            <Text 
              style={{ 
                color: 'white', 
                fontWeight: '600',
                fontSize: '16px',
                display: 'block',
                lineHeight: '1.2'
              }}
            >
              SMS
            </Text>
            <Text 
              style={{ 
                color: 'rgba(255,255,255,0.8)', 
                fontSize: '12px',
                display: 'block'
              }}
            >
              Management
            </Text>
          </div>
        )}
      </div>

      {/* Navigation Menu */}
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          borderRight: 0,
          height: 'calc(100vh - 64px)',
          overflow: 'auto',
        }}
      />
    </Sider>
  );
};

export default AppSidebar;