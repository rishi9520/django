import React from 'react';
import { Layout, Avatar, Dropdown, Button, Typography } from 'antd';
import { 
  UserOutlined, 
  LogoutOutlined, 
  SettingOutlined,
  MenuOutlined 
} from '@ant-design/icons';

const { Header } = Layout;
const { Text } = Typography;

const AppHeader = ({ user, onLogout, onMenuClick }) => {
  const menuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: onLogout,
    },
  ];

  return (
    <Header 
      className="professional-header"
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 20px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={onMenuClick}
          style={{ 
            color: 'white',
            marginRight: '16px',
            display: 'block'
          }}
          className="mobile-menu-btn"
        />
        <div>
          <Text style={{ color: 'white', fontSize: '18px', fontWeight: '600' }}>
            {user?.school_name || 'School Management System'}
          </Text>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Text style={{ color: 'white' }}>
          Welcome, {user?.name}
        </Text>
        <Dropdown 
          menu={{ items: menuItems }}
          placement="bottomRight"
          trigger={['click']}
        >
          <Avatar 
            icon={<UserOutlined />}
            style={{ 
              backgroundColor: '#40a9ff',
              cursor: 'pointer'
            }}
          />
        </Dropdown>
      </div>
    </Header>
  );
};

export default AppHeader;