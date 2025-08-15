import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Typography, 
  List, 
  Tag,
  Button,
  Space,
  Alert,
  Spin
} from 'antd';
import {
  TeamOutlined,
  ClockCircleOutlined,
  SwapOutlined,
  CalendarOutlined,
  UserOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { apiService } from '../services/apiService';

const { Title, Text } = Typography;

const Dashboard = ({ user }) => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTeachers: 0,
    presentToday: 0,
    absentToday: 0,
    arrangements: 0
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [todayArrangements, setTodayArrangements] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch teachers data
      const teachersResponse = await apiService.getTeachers(user.school_id);
      
      // For now, using sample data since backend endpoints are not fully implemented
      // In production, you would fetch real data from respective endpoints
      
      setStats({
        totalTeachers: teachersResponse.success ? teachersResponse.teachers.length : 0,
        presentToday: 0, // Will be calculated from attendance data
        absentToday: 0,  // Will be calculated from attendance data
        arrangements: 0  // Will be fetched from arrangements endpoint
      });

      // Sample recent activities
      setRecentActivities([
        {
          id: 1,
          type: 'teacher_added',
          message: 'New teacher John Doe was added to the system',
          time: '2 hours ago',
          icon: <UserOutlined style={{ color: '#52c41a' }} />
        },
        {
          id: 2,
          type: 'arrangement',
          message: 'Teacher arrangement created for Math Class',
          time: '4 hours ago',
          icon: <SwapOutlined style={{ color: '#1890ff' }} />
        },
        {
          id: 3,
          type: 'attendance',
          message: 'Attendance marked for 25 teachers',
          time: '1 day ago',
          icon: <ClockCircleOutlined style={{ color: '#722ed1' }} />
        }
      ]);

      // Sample today's arrangements
      setTodayArrangements([
        {
          id: 1,
          absentTeacher: 'John Smith',
          replacementTeacher: 'Mary Johnson',
          class: 'Class 10A',
          period: 3,
          subject: 'Mathematics',
          status: 'Confirmed'
        }
      ]);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Welcome Header */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          Welcome back, {user.name}! 👋
        </Title>
        <Text type="secondary">
          Here's what's happening at {user.school_name} today.
        </Text>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Teachers"
              value={stats.totalTeachers}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Present Today"
              value={stats.presentToday}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Absent Today"
              value={stats.absentToday}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Arrangements"
              value={stats.arrangements}
              prefix={<SwapOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Today's Arrangements */}
        <Col xs={24} lg={12}>
          <Card 
            title="Today's Arrangements" 
            extra={
              <Button type="link" size="small">
                View All
              </Button>
            }
          >
            {todayArrangements.length > 0 ? (
              <List
                dataSource={todayArrangements}
                renderItem={item => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <Space>
                          <Text strong>{item.absentTeacher}</Text>
                          <SwapOutlined style={{ color: '#1890ff' }} />
                          <Text strong>{item.replacementTeacher}</Text>
                        </Space>
                      }
                      description={
                        <Space>
                          <Text>{item.class}</Text>
                          <Text>•</Text>
                          <Text>Period {item.period}</Text>
                          <Text>•</Text>
                          <Text>{item.subject}</Text>
                          <Tag color="green">{item.status}</Tag>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Alert
                message="No arrangements for today"
                description="All teachers are present today!"
                type="success"
                showIcon
              />
            )}
          </Card>
        </Col>

        {/* Recent Activities */}
        <Col xs={24} lg={12}>
          <Card 
            title="Recent Activities"
            extra={
              <Button type="link" size="small">
                View All
              </Button>
            }
          >
            <List
              dataSource={recentActivities}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={item.icon}
                    title={item.message}
                    description={item.time}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card title="Quick Actions" style={{ marginTop: '24px' }}>
        <Space wrap>
          <Button type="primary" icon={<TeamOutlined />}>
            Add Teacher
          </Button>
          <Button icon={<ClockCircleOutlined />}>
            Mark Attendance
          </Button>
          <Button icon={<SwapOutlined />}>
            Create Arrangement
          </Button>
          <Button icon={<CalendarOutlined />}>
            View Schedule
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default Dashboard;