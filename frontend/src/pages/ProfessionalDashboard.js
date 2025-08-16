import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Progress,
  Table,
  Tag,
  Button,
  Space,
  Calendar,
  Badge,
  Spin,
  Alert,
  Avatar,
  List
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  BookOutlined,
  BarChartOutlined,
  CalendarOutlined,
  SwapOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { apiService } from '../services/apiService';
import '../styles/ProfessionalDashboard.css';

const { Title, Text, Paragraph } = Typography;

const ProfessionalDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    totalTeachers: 0,
    presentToday: 0,
    absentToday: 0,
    arrangements: 0,
    attendanceRate: 0
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [todayArrangements, setTodayArrangements] = useState([]);
  const [selectedDate, setSelectedDate] = useState(moment());

  const user = JSON.parse(localStorage.getItem('user'));
  const schoolId = user?.school_id;

  useEffect(() => {
    if (schoolId) {
      fetchDashboardData();
    }
  }, [schoolId]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch teachers data
      const teachersResponse = await apiService.getTeachers(schoolId);
      const teachers = teachersResponse.teachers || [];

      // Fetch daily attendance
      const today = moment().format('YYYY-MM-DD');
      const attendanceResponse = await apiService.getDailyAttendance(schoolId, today);
      const attendance = attendanceResponse.daily_attendance || [];

      // Fetch arrangements
      const arrangementsResponse = await apiService.getArrangements(schoolId, today);
      const arrangements = arrangementsResponse.arrangements || [];

      // Calculate statistics
      const presentCount = attendance.filter(a => a.status === 'present').length;
      const absentCount = attendance.filter(a => a.status === 'absent').length;
      const attendanceRate = teachers.length > 0 ? (presentCount / teachers.length) * 100 : 0;

      setDashboardData({
        totalTeachers: teachers.length,
        presentToday: presentCount,
        absentToday: absentCount,
        arrangements: arrangements.length,
        attendanceRate: Math.round(attendanceRate)
      });

      setTodayArrangements(arrangements);

      // Mock recent activities (in real app, this would come from an activity log)
      setRecentActivities([
        {
          id: 1,
          type: 'attendance',
          title: 'Attendance Marked',
          description: `${presentCount} teachers marked present today`,
          time: moment().subtract(1, 'hour').fromNow(),
          icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />
        },
        {
          id: 2,
          type: 'arrangement',
          title: 'Auto Arrangement Created',
          description: `${arrangements.length} arrangements generated automatically`,
          time: moment().subtract(2, 'hours').fromNow(),
          icon: <SwapOutlined style={{ color: '#1890ff' }} />
        },
        {
          id: 3,
          type: 'teacher',
          title: 'New Teacher Added',
          description: 'Teacher profile updated in system',
          time: moment().subtract(4, 'hours').fromNow(),
          icon: <UserOutlined style={{ color: '#722ed1' }} />
        }
      ]);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getListData = (value) => {
    const dateStr = value.format('YYYY-MM-DD');
    // Mock calendar data - in real app, fetch from API
    const events = [];
    
    if (dateStr === moment().format('YYYY-MM-DD')) {
      events.push({
        type: 'success',
        content: `${dashboardData.arrangements} arrangements today`
      });
      if (dashboardData.absentToday > 0) {
        events.push({
          type: 'warning',
          content: `${dashboardData.absentToday} absent teachers`
        });
      }
    }
    
    return events;
  };

  const dateCellRender = (value) => {
    const listData = getListData(value);
    return (
      <ul className="events">
        {listData.map((item, index) => (
          <li key={index}>
            <Badge status={item.type} text={item.content} />
          </li>
        ))}
      </ul>
    );
  };

  const arrangementsColumns = [
    {
      title: 'Period',
      dataIndex: 'period',
      key: 'period',
      width: 80
    },
    {
      title: 'Subject',
      dataIndex: 'subject',
      key: 'subject'
    },
    {
      title: 'Class',
      dataIndex: 'class_name',
      key: 'class_name',
      render: (text, record) => `${text}${record.section ? ` - ${record.section}` : ''}`
    },
    {
      title: 'Absent Teacher',
      dataIndex: 'absent_teacher_name',
      key: 'absent_teacher_name'
    },
    {
      title: 'Replacement',
      dataIndex: 'replacement_teacher_name',
      key: 'replacement_teacher_name'
    },
    {
      title: 'Match Quality',
      dataIndex: 'match_quality',
      key: 'match_quality',
      render: (quality) => {
        const colors = {
          ideal: 'green',
          acceptable: 'orange',
          fallback: 'red'
        };
        return <Tag color={colors[quality?.toLowerCase()] || 'default'}>{quality}</Tag>;
      }
    }
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="professional-dashboard">
      {/* Welcome Header */}
      <Card className="welcome-card">
        <div className="welcome-content">
          <div className="welcome-text">
            <Title level={1} className="welcome-title">
              Welcome to {user?.school_name || 'School Management System'}
            </Title>
            <Paragraph className="welcome-subtitle">
              {moment().format('dddd, MMMM DD, YYYY')} • Good {moment().hour() < 12 ? 'Morning' : moment().hour() < 17 ? 'Afternoon' : 'Evening'}
            </Paragraph>
          </div>
          <div className="school-logo">
            {user?.school_logo ? (
              <img src={user.school_logo} alt="School Logo" className="logo-image" />
            ) : (
              <Avatar size={80} icon={<BookOutlined />} className="logo-avatar" />
            )}
          </div>
        </div>
      </Card>

      {/* Key Metrics */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card metric-primary">
            <Statistic
              title="Total Teachers"
              value={dashboardData.totalTeachers}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card metric-success">
            <Statistic
              title="Present Today"
              value={dashboardData.presentToday}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card metric-warning">
            <Statistic
              title="Absent Today"
              value={dashboardData.absentToday}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="metric-card metric-info">
            <Statistic
              title="Arrangements"
              value={dashboardData.arrangements}
              prefix={<SwapOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* Left Column */}
        <Col xs={24} lg={16}>
          {/* Attendance Overview */}
          <Card 
            title={
              <Space>
                <BarChartOutlined />
                <span>Attendance Overview</span>
              </Space>
            }
            className="section-card"
            style={{ marginBottom: 24 }}
          >
            <Row gutter={[16, 16]} align="middle">
              <Col xs={24} sm={12}>
                <div className="attendance-progress">
                  <Progress
                    type="circle"
                    percent={dashboardData.attendanceRate}
                    format={percent => `${percent}%`}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                    size={120}
                  />
                  <Text strong style={{ marginTop: 12, display: 'block', textAlign: 'center' }}>
                    Today's Attendance Rate
                  </Text>
                </div>
              </Col>
              <Col xs={24} sm={12}>
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div className="stat-item">
                    <Text type="secondary">Present:</Text>
                    <Text strong style={{ color: '#52c41a', marginLeft: 8 }}>
                      {dashboardData.presentToday} teachers
                    </Text>
                  </div>
                  <div className="stat-item">
                    <Text type="secondary">Absent:</Text>
                    <Text strong style={{ color: '#faad14', marginLeft: 8 }}>
                      {dashboardData.absentToday} teachers
                    </Text>
                  </div>
                  <div className="stat-item">
                    <Text type="secondary">Total:</Text>
                    <Text strong style={{ marginLeft: 8 }}>
                      {dashboardData.totalTeachers} teachers
                    </Text>
                  </div>
                </Space>
              </Col>
            </Row>
          </Card>

          {/* Today's Arrangements */}
          <Card 
            title={
              <Space>
                <SwapOutlined />
                <span>Today's Arrangements</span>
              </Space>
            }
            className="section-card"
          >
            {todayArrangements.length > 0 ? (
              <Table
                columns={arrangementsColumns}
                dataSource={todayArrangements}
                rowKey="id"
                pagination={false}
                size="small"
                scroll={{ x: 800 }}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
                <Title level={4}>No Arrangements Needed Today</Title>
                <Text type="secondary">All teachers are present and no substitutions are required.</Text>
              </div>
            )}
          </Card>
        </Col>

        {/* Right Column */}
        <Col xs={24} lg={8}>
          {/* Calendar */}
          <Card 
            title={
              <Space>
                <CalendarOutlined />
                <span>Calendar</span>
              </Space>
            }
            className="section-card"
            style={{ marginBottom: 24 }}
          >
            <Calendar
              fullscreen={false}
              value={selectedDate}
              onSelect={setSelectedDate}
              dateCellRender={dateCellRender}
            />
          </Card>

          {/* Recent Activities */}
          <Card 
            title={
              <Space>
                <TrophyOutlined />
                <span>Recent Activities</span>
              </Space>
            }
            className="section-card"
          >
            <List
              dataSource={recentActivities}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={item.icon}
                    title={item.title}
                    description={
                      <div>
                        <div>{item.description}</div>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {item.time}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card 
        title="Quick Actions"
        className="section-card"
        style={{ marginTop: 24 }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Button 
              type="primary" 
              block 
              size="large"
              icon={<UserOutlined />}
              onClick={() => window.location.href = '/teachers'}
            >
              Manage Teachers
            </Button>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Button 
              block 
              size="large"
              icon={<CheckCircleOutlined />}
              onClick={() => window.location.href = '/attendance'}
            >
              Mark Attendance
            </Button>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Button 
              block 
              size="large"
              icon={<SwapOutlined />}
              onClick={() => window.location.href = '/arrangements'}
            >
              View Arrangements
            </Button>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Button 
              block 
              size="large"
              icon={<BarChartOutlined />}
              onClick={() => window.location.href = '/reports'}
            >
              Generate Reports
            </Button>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default ProfessionalDashboard;