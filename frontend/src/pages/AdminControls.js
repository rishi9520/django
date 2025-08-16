import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  Space,
  Table,
  Modal,
  Form,
  Input,
  Switch,
  message,
  Alert,
  Statistic,
  Tabs,
  List,
  Avatar,
  Tag,
  Select,
  Upload,
  Progress
} from 'antd';
import {
  SettingOutlined,
  UserOutlined,
  SecurityScanOutlined,
  DatabaseOutlined,
  CloudUploadOutlined,
  FileTextOutlined,
  BellOutlined,
  GlobalOutlined,
  TeamOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  UploadOutlined
} from '@ant-design/icons';
import { apiService } from '../services/apiService';
import '../styles/AdminControls.css';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const AdminControls = () => {
  const [loading, setLoading] = useState(false);
  const [systemStats, setSystemStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalData: 0,
    systemHealth: 95
  });
  const [users, setUsers] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState(''); // 'user', 'backup', 'settings'
  const [form] = Form.useForm();
  const [selectedUser, setSelectedUser] = useState(null);

  const user = JSON.parse(localStorage.getItem('user'));
  const schoolId = user?.school_id;

  useEffect(() => {
    if (schoolId) {
      fetchSystemData();
    }
  }, [schoolId]);

  const fetchSystemData = async () => {
    setLoading(true);
    try {
      // Fetch teachers as admin users for demo
      const teachersResponse = await apiService.getTeachers(schoolId);
      const teachers = teachersResponse.teachers || [];
      
      // Mock admin data - in real app, you'd have dedicated admin endpoints
      const mockUsers = teachers.slice(0, 5).map((teacher, index) => ({
        id: teacher.teacher_id,
        name: teacher.name,
        email: `${teacher.teacher_id}@${schoolId}.edu`,
        role: index === 0 ? 'Admin' : 'Teacher',
        status: Math.random() > 0.2 ? 'Active' : 'Inactive',
        lastLogin: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      }));

      setUsers(mockUsers);
      setSystemStats({
        totalUsers: mockUsers.length,
        activeUsers: mockUsers.filter(u => u.status === 'Active').length,
        totalData: teachers.length,
        systemHealth: 95 + Math.random() * 5
      });
    } catch (error) {
      console.error('Error fetching system data:', error);
      message.error('Failed to fetch system data');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = (action, userRecord = null) => {
    setSelectedUser(userRecord);
    setModalType('user');
    
    if (action === 'add') {
      form.resetFields();
    } else if (action === 'edit' && userRecord) {
      form.setFieldsValue(userRecord);
    }
    
    setModalVisible(true);
  };

  const handleUserSubmit = async (values) => {
    try {
      if (selectedUser) {
        // Update user
        message.success('User updated successfully');
      } else {
        // Add new user
        message.success('User added successfully');
      }
      
      setModalVisible(false);
      form.resetFields();
      fetchSystemData();
    } catch (error) {
      message.error('Failed to save user');
    }
  };

  const handleDeleteUser = (userRecord) => {
    Modal.confirm({
      title: 'Delete User',
      content: `Are you sure you want to delete ${userRecord.name}?`,
      okType: 'danger',
      onOk: async () => {
        try {
          // Delete user logic
          message.success('User deleted successfully');
          fetchSystemData();
        } catch (error) {
          message.error('Failed to delete user');
        }
      }
    });
  };

  const handleBackup = () => {
    Modal.confirm({
      title: 'Create Backup',
      content: 'This will create a backup of all school data. Continue?',
      onOk: async () => {
        try {
          // Backup logic
          message.success('Backup created successfully');
        } catch (error) {
          message.error('Failed to create backup');
        }
      }
    });
  };

  const handleDataImport = (info) => {
    if (info.file.status === 'uploading') {
      message.loading('Uploading file...', 0);
    }
    if (info.file.status === 'done') {
      message.destroy();
      message.success('Data imported successfully');
      fetchSystemData();
    }
    if (info.file.status === 'error') {
      message.destroy();
      message.error('Import failed');
    }
  };

  const userColumns = [
    {
      title: 'User',
      key: 'user',
      render: (_, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 'bold' }}>{record.name}</div>
            <div style={{ color: '#666', fontSize: '12px' }}>{record.email}</div>
          </div>
        </Space>
      )
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (role) => {
        const color = role === 'Admin' ? 'red' : 'blue';
        return <Tag color={color}>{role}</Tag>;
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const color = status === 'Active' ? 'green' : 'default';
        return <Tag color={color}>{status}</Tag>;
      }
    },
    {
      title: 'Last Login',
      dataIndex: 'lastLogin',
      key: 'lastLogin'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => message.info(`Viewing ${record.name}`)}
          >
            View
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleUserAction('edit', record)}
          >
            Edit
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDeleteUser(record)}
          >
            Delete
          </Button>
        </Space>
      )
    }
  ];

  const systemLogs = [
    {
      id: 1,
      type: 'info',
      message: 'User login: admin@demo.edu',
      timestamp: '2025-08-16 10:30:00',
      icon: <UserOutlined style={{ color: '#1890ff' }} />
    },
    {
      id: 2,
      type: 'warning',
      message: 'Failed login attempt from unknown IP',
      timestamp: '2025-08-16 10:25:00',
      icon: <SecurityScanOutlined style={{ color: '#faad14' }} />
    },
    {
      id: 3,
      type: 'success',
      message: 'Database backup completed successfully',
      timestamp: '2025-08-16 10:20:00',
      icon: <DatabaseOutlined style={{ color: '#52c41a' }} />
    },
    {
      id: 4,
      type: 'info',
      message: 'System maintenance completed',
      timestamp: '2025-08-16 10:15:00',
      icon: <SettingOutlined style={{ color: '#1890ff' }} />
    }
  ];

  return (
    <div className="admin-controls">
      <Card className="header-card">
        <div className="header-content">
          <div>
            <Title level={2} className="page-title">
              <SettingOutlined style={{ marginRight: 12 }} />
              Admin Controls
            </Title>
            <Text type="secondary">Manage system settings, users, and data</Text>
          </div>
        </div>
      </Card>

      {/* System Statistics */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <Statistic
              title="Total Users"
              value={systemStats.totalUsers}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <Statistic
              title="Active Users"
              value={systemStats.activeUsers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <Statistic
              title="Data Records"
              value={systemStats.totalData}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={Math.round(systemStats.systemHealth)}
                size={80}
                format={percent => `${percent}%`}
                strokeColor={{
                  '0%': '#ff4d4f',
                  '50%': '#faad14',
                  '100%': '#52c41a'
                }}
              />
              <Text strong style={{ display: 'block', marginTop: 8 }}>
                System Health
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* Left Column - Main Controls */}
        <Col xs={24} lg={16}>
          <Card className="content-card">
            <Tabs defaultActiveKey="users" className="admin-tabs">
              <TabPane tab="User Management" key="users">
                <div style={{ marginBottom: 16 }}>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => handleUserAction('add')}
                  >
                    Add New User
                  </Button>
                </div>
                
                <Table
                  columns={userColumns}
                  dataSource={users}
                  rowKey="id"
                  pagination={{ pageSize: 10 }}
                  loading={loading}
                  className="admin-table"
                />
              </TabPane>

              <TabPane tab="Data Management" key="data">
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <Alert
                    message="Data Management"
                    description="Backup, restore, and import/export school data safely."
                    type="info"
                    showIcon
                  />
                  
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12}>
                      <Card>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <DatabaseOutlined style={{ fontSize: 32, color: '#1890ff' }} />
                          <Title level={4}>Database Backup</Title>
                          <Paragraph>Create a complete backup of all school data.</Paragraph>
                          <Button
                            type="primary"
                            block
                            onClick={handleBackup}
                            icon={<CloudUploadOutlined />}
                          >
                            Create Backup
                          </Button>
                        </Space>
                      </Card>
                    </Col>
                    
                    <Col xs={24} sm={12}>
                      <Card>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <FileTextOutlined style={{ fontSize: 32, color: '#52c41a' }} />
                          <Title level={4}>Data Import</Title>
                          <Paragraph>Import teacher and student data from CSV files.</Paragraph>
                          <Upload
                            accept=".csv"
                            showUploadList={false}
                            onChange={handleDataImport}
                            beforeUpload={() => false}
                          >
                            <Button
                              type="default"
                              block
                              icon={<UploadOutlined />}
                            >
                              Import CSV Data
                            </Button>
                          </Upload>
                        </Space>
                      </Card>
                    </Col>
                  </Row>
                </Space>
              </TabPane>

              <TabPane tab="System Settings" key="settings">
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <Card title="School Information">
                    <Row gutter={[16, 16]}>
                      <Col xs={24} sm={12}>
                        <Form.Item label="School Name">
                          <Input defaultValue={user?.school_name || 'Demo School'} />
                        </Form.Item>
                      </Col>
                      <Col xs={24} sm={12}>
                        <Form.Item label="School Code">
                          <Input defaultValue={schoolId} disabled />
                        </Form.Item>
                      </Col>
                    </Row>
                  </Card>

                  <Card title="System Preferences">
                    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                      <Row justify="space-between" align="middle">
                        <Text>Enable Email Notifications</Text>
                        <Switch defaultChecked />
                      </Row>
                      <Row justify="space-between" align="middle">
                        <Text>Auto Backup (Daily)</Text>
                        <Switch defaultChecked />
                      </Row>
                      <Row justify="space-between" align="middle">
                        <Text>Public Registration</Text>
                        <Switch />
                      </Row>
                      <Row justify="space-between" align="middle">
                        <Text>Maintenance Mode</Text>
                        <Switch />
                      </Row>
                    </Space>
                  </Card>

                  <Button type="primary" size="large">
                    Save Settings
                  </Button>
                </Space>
              </TabPane>
            </Tabs>
          </Card>
        </Col>

        {/* Right Column - System Activity */}
        <Col xs={24} lg={8}>
          <Card 
            title={
              <Space>
                <BellOutlined />
                <span>System Activity</span>
              </Space>
            }
            className="content-card"
            style={{ marginBottom: 24 }}
          >
            <List
              dataSource={systemLogs}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={item.icon}
                    title={item.message}
                    description={item.timestamp}
                  />
                </List.Item>
              )}
            />
          </Card>

          <Card 
            title={
              <Space>
                <GlobalOutlined />
                <span>Quick Actions</span>
              </Space>
            }
            className="content-card"
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Button
                block
                icon={<DatabaseOutlined />}
                onClick={() => message.info('Database optimization started')}
              >
                Optimize Database
              </Button>
              <Button
                block
                icon={<SecurityScanOutlined />}
                onClick={() => message.info('Security scan initiated')}
              >
                Security Scan
              </Button>
              <Button
                block
                icon={<CloudUploadOutlined />}
                onClick={() => message.info('Cache cleared successfully')}
              >
                Clear Cache
              </Button>
              <Button
                block
                icon={<SettingOutlined />}
                onClick={() => message.info('System restart scheduled')}
              >
                Restart System
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* User Modal */}
      <Modal
        title={selectedUser ? 'Edit User' : 'Add New User'}
        open={modalVisible && modalType === 'user'}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUserSubmit}
          style={{ marginTop: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="name"
                label="Full Name"
                rules={[{ required: true, message: 'Name is required' }]}
              >
                <Input placeholder="Enter full name" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="email"
                label="Email"
                rules={[
                  { required: true, message: 'Email is required' },
                  { type: 'email', message: 'Invalid email format' }
                ]}
              >
                <Input placeholder="Enter email address" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="role"
                label="Role"
                rules={[{ required: true, message: 'Role is required' }]}
              >
                <Select placeholder="Select role">
                  <Option value="Admin">Admin</Option>
                  <Option value="Teacher">Teacher</Option>
                  <Option value="Staff">Staff</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="status"
                label="Status"
                rules={[{ required: true, message: 'Status is required' }]}
              >
                <Select placeholder="Select status">
                  <Option value="Active">Active</Option>
                  <Option value="Inactive">Inactive</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {selectedUser ? 'Update' : 'Add'} User
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AdminControls;