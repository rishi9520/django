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
      // Django API returns {"schools": [...]} format
      if (response.schools && Array.isArray(response.schools)) {
        setSchools(response.schools);
        if (response.schools.length === 0) {
          message.warning('No schools found');
        }
      } else {
        message.error('Invalid response format from server');
      }
    } catch (error) {
      console.error('Error fetching schools:', error);
      message.error('Failed to connect to server. Please check your connection.');
      setSchools([]); // Set empty array on error
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

      // Django API returns {"message": "Login successful", "admin": {...}} format
      if (response.message === 'Login successful' && response.admin) {
        onLogin(response.admin);
        message.success('Login successful!');
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
    <div className="login-container" style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Floating Background Elements */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '10%',
        width: '100px',
        height: '100px',
        background: 'rgba(255,255,255,0.1)',
        borderRadius: '50%',
        animation: 'float 6s ease-in-out infinite'
      }}></div>
      <div style={{
        position: 'absolute',
        top: '70%',
        right: '15%',
        width: '150px',
        height: '150px',
        background: 'rgba(255,255,255,0.08)',
        borderRadius: '50%',
        animation: 'float 8s ease-in-out infinite reverse'
      }}></div>
      <div style={{
        position: 'absolute',
        bottom: '20%',
        left: '20%',
        width: '80px',
        height: '80px',
        background: 'rgba(255,255,255,0.12)',
        borderRadius: '50%',
        animation: 'float 7s ease-in-out infinite'
      }}></div>

      <Card 
        className="login-form"
        style={{
          borderRadius: '25px',
          boxShadow: '0 25px 50px rgba(0,0,0,0.2)',
          backdropFilter: 'blur(10px)',
          background: 'rgba(255,255,255,0.95)',
          border: '1px solid rgba(255,255,255,0.3)',
          width: '100%',
          maxWidth: '500px',
          zIndex: 1,
          position: 'relative'
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          {selectedSchool?.logourl ? (
            <Avatar
              src={selectedSchool.logourl}
              size={80}
              style={{ 
                marginBottom: '20px',
                backgroundColor: 'transparent',
                border: '3px solid #667eea'
              }}
            />
          ) : (
            <Avatar
              icon={<BookOutlined />}
              size={80}
              style={{ 
                backgroundColor: '#667eea',
                marginBottom: '20px',
                border: '3px solid #764ba2'
              }}
            />
          )}
          <Title level={1} style={{ 
            margin: '0 0 12px 0', 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontSize: '2.5rem',
            fontWeight: 'bold'
          }}>
            {selectedSchool?.school_name || 'School Management Pro'}
          </Title>
          <Text style={{ 
            color: '#6B7280', 
            fontSize: '16px',
            display: 'block',
            marginBottom: '8px'
          }}>
            Advanced Teacher Management & Attendance System
          </Text>
          <Text style={{ 
            color: '#9CA3AF', 
            fontSize: '14px',
            fontStyle: 'italic'
          }}>
            Streamline your school operations with intelligent automation
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
              placeholder={schoolsLoading ? "Loading schools..." : schools.length === 0 ? "No schools available" : "Choose your school"}
              loading={schoolsLoading}
              disabled={schoolsLoading || schools.length === 0}
              onChange={handleSchoolChange}
              showSearch
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
              notFoundContent={schoolsLoading ? "Loading..." : "No schools found"}
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
        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <div style={{ marginBottom: '16px' }}>
            <Text style={{ 
              color: '#6B7280', 
              fontSize: '13px',
              display: 'block',
              marginBottom: '8px'
            }}>
              By logging in, you agree to our{' '}
              <a href="#" style={{ color: '#667eea', textDecoration: 'none' }}>
                Terms & Conditions
              </a>{' '}
              and{' '}
              <a href="#" style={{ color: '#667eea', textDecoration: 'none' }}>
                Privacy Policy
              </a>
            </Text>
          </div>
          <div style={{ 
            borderTop: '1px solid #E5E7EB', 
            paddingTop: '16px',
            textAlign: 'center'
          }}>
            <Text style={{ 
              color: '#9CA3AF', 
              fontSize: '12px',
              display: 'block'
            }}>
              © 2025 School Management Pro. All rights reserved.
            </Text>
            <Text style={{ 
              color: '#9CA3AF', 
              fontSize: '11px',
              display: 'block',
              marginTop: '4px'
            }}>
              Powered by Advanced AI Technology | Version 2.0
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;