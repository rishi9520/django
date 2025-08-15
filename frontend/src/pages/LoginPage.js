import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Select, 
  Typography, 
  message, 
  Card,
  Avatar,
  Spin 
} from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  BookOutlined 
} from '@ant-design/icons';
import { apiService } from '../services/apiService';

const { Title, Text } = Typography;
const { Option } = Select;

const LoginPage = ({ onLogin }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [schools, setSchools] = useState([]);
  const [schoolsLoading, setSchoolsLoading] = useState(true);
  const [selectedSchool, setSelectedSchool] = useState(null);

  useEffect(() => {
    fetchSchools();
  }, []);

  const fetchSchools = async () => {
    try {
      setSchoolsLoading(true);
      const response = await apiService.getSchools();
      if (response.success) {
        setSchools(response.schools);
      } else {
        message.error('Failed to load schools');
      }
    } catch (error) {
      console.error('Error fetching schools:', error);
      message.error('Failed to connect to server');
    } finally {
      setSchoolsLoading(false);
    }
  };

  const handleSchoolChange = (schoolId) => {
    const school = schools.find(s => s.school_id === schoolId);
    setSelectedSchool(school);
  };

  const handleSubmit = async (values) => {
    try {
      setLoading(true);
      const response = await apiService.login({
        school_id: values.school_id,
        username: values.username,
        password: values.password,
      });

      if (response.success) {
        onLogin(response.user);
      } else {
        message.error(response.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      message.error(
        error.response?.data?.error || 
        'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Card 
        className="login-form"
        style={{
          borderRadius: '15px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          {selectedSchool?.logourl ? (
            <Avatar
              src={selectedSchool.logourl}
              size={64}
              style={{ marginBottom: '16px' }}
            />
          ) : (
            <Avatar
              icon={<BookOutlined />}
              size={64}
              style={{ 
                backgroundColor: '#40a9ff',
                marginBottom: '16px'
              }}
            />
          )}
          <Title level={2} style={{ margin: '0 0 8px 0', color: '#1890ff' }}>
            {selectedSchool?.school_name || 'School Management System'}
          </Title>
          <Text type="secondary">
            Teacher Arrangement & Attendance System
          </Text>
        </div>

        {/* Login Form */}
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="school_id"
            label="Select School"
            rules={[
              { required: true, message: 'Please select your school!' }
            ]}
          >
            <Select
              placeholder="Choose your school"
              loading={schoolsLoading}
              onChange={handleSchoolChange}
              showSearch
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
            >
              {schools.map(school => (
                <Option key={school.school_id} value={school.school_id}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    {school.logourl ? (
                      <Avatar
                        src={school.logourl}
                        size={24}
                        style={{ marginRight: '8px' }}
                      />
                    ) : (
                      <Avatar
                        icon={<BookOutlined />}
                        size={24}
                        style={{ 
                          backgroundColor: '#40a9ff',
                          marginRight: '8px'
                        }}
                      />
                    )}
                    {school.school_name}
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="username"
            label="Username"
            rules={[
              { required: true, message: 'Please enter your username!' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Enter your username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: true, message: 'Please enter your password!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Enter your password"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{
                height: '45px',
                fontSize: '16px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
              }}
            >
              {loading ? <Spin size="small" /> : 'Login'}
            </Button>
          </Form.Item>
        </Form>

        {/* Footer */}
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Powered by School Management System
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;