import React from 'react';
import { Layout, Avatar, Dropdown, Button, Typography, Modal, Switch, Divider, message } from 'antd';
import { 
  UserOutlined, 
  LogoutOutlined, 
  SettingOutlined,
  MenuOutlined,
  MoonOutlined,
  SunOutlined,
  CameraOutlined,
  PrinterOutlined,
  VideoCameraOutlined,
  DownloadOutlined,
  BgColorsOutlined
} from '@ant-design/icons';

const { Header } = Layout;
const { Text } = Typography;

const AppHeader = ({ user, onLogout, onMenuClick }) => {
  const [darkMode, setDarkMode] = React.useState(false);
  const [settingsVisible, setSettingsVisible] = React.useState(false);

  const handleMenuItemClick = ({ key }) => {
    if (key === 'profile-settings') {
      // Handle profile settings
      console.log('Profile settings clicked');
    } else if (key === 'edit-image') {
      // Handle edit image
      console.log('Edit image clicked');
    } else if (key === 'settings') {
      setSettingsVisible(true);
    } else if (key === 'logout') {
      onLogout();
    }
  };

  const menuItems = [
    {
      key: 'profile-settings',
      icon: <UserOutlined />,
      label: 'Profile Settings',
    },
    {
      key: 'edit-image',
      icon: <UserOutlined />,
      label: 'Edit Profile Image',
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
      danger: true,
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
          menu={{ items: menuItems, onClick: handleMenuItemClick }}
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

        {/* Settings Modal */}
        <Modal
          title="⚙️ Advanced Settings"
          open={settingsVisible}
          onCancel={() => setSettingsVisible(false)}
          footer={null}
          width={600}
          style={{ top: 20 }}
        >
          <div style={{ padding: '20px 0' }}>
            {/* Theme Settings */}
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                🎨 Theme & Appearance
              </Text>
              <Divider style={{ margin: '12px 0' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  {darkMode ? <MoonOutlined style={{ marginRight: '8px' }} /> : <SunOutlined style={{ marginRight: '8px' }} />}
                  <Text>Dark Mode</Text>
                </div>
                <Switch 
                  checked={darkMode} 
                  onChange={(checked) => {
                    setDarkMode(checked);
                    message.success(checked ? 'Dark mode enabled' : 'Light mode enabled');
                  }}
                  checkedChildren="🌙"
                  unCheckedChildren="☀️"
                />
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <BgColorsOutlined style={{ marginRight: '8px' }} />
                  <Text>Theme Colors</Text>
                </div>
                <Button size="small" onClick={() => message.info('Theme customization coming soon!')}>
                  Customize
                </Button>
              </div>
            </div>

            {/* Screenshot & Recording */}
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                📸 Screenshot & Recording
              </Text>
              <Divider style={{ margin: '12px 0' }} />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <Button 
                  icon={<CameraOutlined />} 
                  onClick={() => {
                    navigator.mediaDevices.getDisplayMedia({ video: true }).then(stream => {
                      const video = document.createElement('video');
                      video.srcObject = stream;
                      video.play();
                      
                      const canvas = document.createElement('canvas');
                      canvas.width = stream.getVideoTracks()[0].getSettings().width;
                      canvas.height = stream.getVideoTracks()[0].getSettings().height;
                      const ctx = canvas.getContext('2d');
                      
                      video.addEventListener('loadedmetadata', () => {
                        ctx.drawImage(video, 0, 0);
                        canvas.toBlob(blob => {
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = 'screenshot.png';
                          a.click();
                        });
                        stream.getTracks().forEach(track => track.stop());
                      });
                    }).catch(() => message.error('Screenshot permission denied'));
                  }}
                >
                  Screenshot
                </Button>
                
                <Button 
                  icon={<VideoCameraOutlined />}
                  onClick={() => {
                    navigator.mediaDevices.getDisplayMedia({ video: true, audio: true }).then(stream => {
                      const mediaRecorder = new MediaRecorder(stream);
                      const chunks = [];
                      
                      mediaRecorder.ondataavailable = (event) => chunks.push(event.data);
                      mediaRecorder.onstop = () => {
                        const blob = new Blob(chunks, { type: 'video/webm' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'recording.webm';
                        a.click();
                      };
                      
                      mediaRecorder.start();
                      message.success('Recording started! Click again to stop.');
                      
                      // Auto stop after 30 seconds
                      setTimeout(() => {
                        if (mediaRecorder.state === 'recording') {
                          mediaRecorder.stop();
                          stream.getTracks().forEach(track => track.stop());
                        }
                      }, 30000);
                    }).catch(() => message.error('Recording permission denied'));
                  }}
                >
                  Record Screen
                </Button>
              </div>
            </div>

            {/* Print Options */}
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                🖨️ Print & Export
              </Text>
              <Divider style={{ margin: '12px 0' }} />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <Button 
                  icon={<PrinterOutlined />}
                  onClick={() => {
                    window.print();
                    message.success('Print dialog opened');
                  }}
                >
                  Print Page
                </Button>
                
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={() => {
                    const data = JSON.stringify({
                      user: user,
                      timestamp: new Date().toISOString(),
                      school: user?.school_name
                    }, null, 2);
                    const blob = new Blob([data], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'school-data-export.json';
                    a.click();
                    message.success('Data exported successfully');
                  }}
                >
                  Export Data
                </Button>
              </div>
            </div>
          </div>
        </Modal>
      </div>
    </Header>
  );
};

export default AppHeader;