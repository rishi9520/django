import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  DatePicker,
  Select,
  Typography,
  Space,
  Table,
  Statistic,
  Progress,
  Alert,
  Empty,
  Spin,
  message,
  Modal
} from 'antd';
import {
  BarChartOutlined,
  DownloadOutlined,
  CalendarOutlined,
  UserOutlined,
  SwapOutlined,
  FileTextOutlined,
  TrophyOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { apiService } from '../services/apiService';
import '../styles/ReportsManagement.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const ReportsManagement = () => {
  const [loading, setLoading] = useState(false);
  const [reportType, setReportType] = useState('attendance');
  const [dateRange, setDateRange] = useState([moment().subtract(30, 'days'), moment()]);
  const [reportData, setReportData] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [teachers, setTeachers] = useState([]);

  const user = JSON.parse(localStorage.getItem('user'));
  const schoolId = user?.school_id;

  useEffect(() => {
    if (schoolId) {
      fetchTeachers();
      generateReport();
    }
  }, [schoolId]);

  useEffect(() => {
    if (schoolId) {
      generateReport();
    }
  }, [reportType, dateRange]);

  const fetchTeachers = async () => {
    try {
      const response = await apiService.getTeachers(schoolId);
      setTeachers(response.teachers || []);
    } catch (error) {
      console.error('Error fetching teachers:', error);
    }
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const startDate = dateRange[0].format('YYYY-MM-DD');
      const endDate = dateRange[1].format('YYYY-MM-DD');

      switch (reportType) {
        case 'attendance':
          await generateAttendanceReport(startDate, endDate);
          break;
        case 'arrangements':
          await generateArrangementsReport(startDate, endDate);
          break;
        case 'teacher_performance':
          await generateTeacherPerformanceReport(startDate, endDate);
          break;
        default:
          await generateAttendanceReport(startDate, endDate);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      message.error('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const generateAttendanceReport = async (startDate, endDate) => {
    const response = await apiService.getAttendanceReport(schoolId, startDate, endDate);
    const attendance = response.attendance || [];
    
    // Calculate statistics
    const totalRecords = attendance.length;
    const presentCount = attendance.filter(a => a.status === 'present').length;
    const absentCount = attendance.filter(a => a.status === 'absent').length;
    const lateCount = attendance.filter(a => a.status === 'late').length;
    
    // Group by teacher
    const teacherStats = attendance.reduce((acc, record) => {
      if (!acc[record.teacher_id]) {
        acc[record.teacher_id] = {
          teacher_id: record.teacher_id,
          teacher_name: record.teacher_name,
          total: 0,
          present: 0,
          absent: 0,
          late: 0,
          rate: 0
        };
      }
      
      acc[record.teacher_id].total++;
      acc[record.teacher_id][record.status]++;
      acc[record.teacher_id].rate = Math.round(
        (acc[record.teacher_id].present / acc[record.teacher_id].total) * 100
      );
      
      return acc;
    }, {});

    setReportData(Object.values(teacherStats));
    setStatistics({
      totalRecords,
      presentCount,
      absentCount,
      lateCount,
      overallRate: totalRecords > 0 ? Math.round((presentCount / totalRecords) * 100) : 0
    });
  };

  const generateArrangementsReport = async (startDate, endDate) => {
    // Mock arrangements report - in real app, you'd fetch from arrangements endpoint
    const mockData = [
      {
        date: '2025-08-15',
        total_arrangements: 5,
        ideal_matches: 3,
        acceptable_matches: 2,
        fallback_matches: 0,
        coverage_rate: 100
      },
      {
        date: '2025-08-14',
        total_arrangements: 3,
        ideal_matches: 2,
        acceptable_matches: 1,
        fallback_matches: 0,
        coverage_rate: 100
      }
    ];

    setReportData(mockData);
    setStatistics({
      totalArrangements: mockData.reduce((sum, day) => sum + day.total_arrangements, 0),
      averageCoverage: Math.round(
        mockData.reduce((sum, day) => sum + day.coverage_rate, 0) / mockData.length
      ),
      idealMatches: mockData.reduce((sum, day) => sum + day.ideal_matches, 0),
      acceptableMatches: mockData.reduce((sum, day) => sum + day.acceptable_matches, 0)
    });
  };

  const generateTeacherPerformanceReport = async (startDate, endDate) => {
    const attendanceResponse = await apiService.getAttendanceReport(schoolId, startDate, endDate);
    const attendance = attendanceResponse.attendance || [];
    
    // Calculate performance metrics per teacher
    const teacherPerformance = teachers.map(teacher => {
      const teacherRecords = attendance.filter(a => a.teacher_id === teacher.teacher_id);
      const totalDays = teacherRecords.length;
      const presentDays = teacherRecords.filter(a => a.status === 'present').length;
      const lateDays = teacherRecords.filter(a => a.status === 'late').length;
      const absentDays = teacherRecords.filter(a => a.status === 'absent').length;
      
      const attendanceRate = totalDays > 0 ? Math.round((presentDays / totalDays) * 100) : 0;
      const punctualityRate = totalDays > 0 ? Math.round(((presentDays - lateDays) / totalDays) * 100) : 0;
      
      let performanceGrade = 'A';
      if (attendanceRate < 95) performanceGrade = 'B';
      if (attendanceRate < 85) performanceGrade = 'C';
      if (attendanceRate < 75) performanceGrade = 'D';
      
      return {
        teacher_id: teacher.teacher_id,
        name: teacher.name,
        category: teacher.category,
        totalDays,
        presentDays,
        absentDays,
        lateDays,
        attendanceRate,
        punctualityRate,
        performanceGrade
      };
    });

    setReportData(teacherPerformance);
    setStatistics({
      totalTeachers: teachers.length,
      averageAttendance: Math.round(
        teacherPerformance.reduce((sum, t) => sum + t.attendanceRate, 0) / teachers.length
      ),
      topPerformers: teacherPerformance.filter(t => t.performanceGrade === 'A').length,
      needsImprovement: teacherPerformance.filter(t => t.performanceGrade === 'D').length
    });
  };

  const exportReport = () => {
    if (reportData.length === 0) {
      message.warning('No data to export');
      return;
    }

    let csvContent = '';
    let filename = '';

    switch (reportType) {
      case 'attendance':
        csvContent = [
          ['Teacher ID', 'Teacher Name', 'Total Days', 'Present', 'Absent', 'Late', 'Attendance Rate'],
          ...reportData.map(item => [
            item.teacher_id,
            item.teacher_name,
            item.total,
            item.present,
            item.absent,
            item.late,
            `${item.rate}%`
          ])
        ].map(row => row.join(',')).join('\n');
        filename = `attendance_report_${schoolId}_${dateRange[0].format('YYYY-MM-DD')}_to_${dateRange[1].format('YYYY-MM-DD')}.csv`;
        break;
        
      case 'arrangements':
        csvContent = [
          ['Date', 'Total Arrangements', 'Ideal Matches', 'Acceptable Matches', 'Fallback Matches', 'Coverage Rate'],
          ...reportData.map(item => [
            item.date,
            item.total_arrangements,
            item.ideal_matches,
            item.acceptable_matches,
            item.fallback_matches,
            `${item.coverage_rate}%`
          ])
        ].map(row => row.join(',')).join('\n');
        filename = `arrangements_report_${schoolId}_${dateRange[0].format('YYYY-MM-DD')}_to_${dateRange[1].format('YYYY-MM-DD')}.csv`;
        break;
        
      case 'teacher_performance':
        csvContent = [
          ['Teacher ID', 'Name', 'Category', 'Total Days', 'Present', 'Absent', 'Late', 'Attendance Rate', 'Punctuality Rate', 'Grade'],
          ...reportData.map(item => [
            item.teacher_id,
            item.name,
            item.category,
            item.totalDays,
            item.presentDays,
            item.absentDays,
            item.lateDays,
            `${item.attendanceRate}%`,
            `${item.punctualityRate}%`,
            item.performanceGrade
          ])
        ].map(row => row.join(',')).join('\n');
        filename = `teacher_performance_report_${schoolId}_${dateRange[0].format('YYYY-MM-DD')}_to_${dateRange[1].format('YYYY-MM-DD')}.csv`;
        break;
    }

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getColumns = () => {
    switch (reportType) {
      case 'attendance':
        return [
          { title: 'Teacher ID', dataIndex: 'teacher_id', key: 'teacher_id' },
          { title: 'Teacher Name', dataIndex: 'teacher_name', key: 'teacher_name' },
          { title: 'Total Days', dataIndex: 'total', key: 'total' },
          { title: 'Present', dataIndex: 'present', key: 'present' },
          { title: 'Absent', dataIndex: 'absent', key: 'absent' },
          { title: 'Late', dataIndex: 'late', key: 'late' },
          { 
            title: 'Attendance Rate', 
            dataIndex: 'rate', 
            key: 'rate',
            render: (rate) => (
              <Progress 
                percent={rate} 
                size="small" 
                format={percent => `${percent}%`}
                strokeColor={rate >= 95 ? '#52c41a' : rate >= 85 ? '#faad14' : '#ff4d4f'}
              />
            )
          }
        ];
        
      case 'arrangements':
        return [
          { title: 'Date', dataIndex: 'date', key: 'date' },
          { title: 'Total Arrangements', dataIndex: 'total_arrangements', key: 'total_arrangements' },
          { title: 'Ideal Matches', dataIndex: 'ideal_matches', key: 'ideal_matches' },
          { title: 'Acceptable Matches', dataIndex: 'acceptable_matches', key: 'acceptable_matches' },
          { title: 'Fallback Matches', dataIndex: 'fallback_matches', key: 'fallback_matches' },
          { 
            title: 'Coverage Rate', 
            dataIndex: 'coverage_rate', 
            key: 'coverage_rate',
            render: (rate) => `${rate}%`
          }
        ];
        
      case 'teacher_performance':
        return [
          { title: 'Teacher ID', dataIndex: 'teacher_id', key: 'teacher_id' },
          { title: 'Name', dataIndex: 'name', key: 'name' },
          { title: 'Category', dataIndex: 'category', key: 'category' },
          { title: 'Total Days', dataIndex: 'totalDays', key: 'totalDays' },
          { title: 'Present', dataIndex: 'presentDays', key: 'presentDays' },
          { title: 'Absent', dataIndex: 'absentDays', key: 'absentDays' },
          { 
            title: 'Attendance Rate', 
            dataIndex: 'attendanceRate', 
            key: 'attendanceRate',
            render: (rate) => `${rate}%`
          },
          { 
            title: 'Grade', 
            dataIndex: 'performanceGrade', 
            key: 'performanceGrade',
            render: (grade) => {
              const colors = { A: 'green', B: 'blue', C: 'orange', D: 'red' };
              return <span style={{ color: colors[grade], fontWeight: 'bold' }}>{grade}</span>;
            }
          }
        ];
        
      default:
        return [];
    }
  };

  const renderStatistics = () => {
    switch (reportType) {
      case 'attendance':
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Total Records" value={statistics.totalRecords} prefix={<FileTextOutlined />} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Present" value={statistics.presentCount} prefix={<UserOutlined />} valueStyle={{ color: '#52c41a' }} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Absent" value={statistics.absentCount} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#ff4d4f' }} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Overall Rate" value={statistics.overallRate} suffix="%" prefix={<TrophyOutlined />} valueStyle={{ color: '#1890ff' }} />
            </Col>
          </Row>
        );
        
      case 'arrangements':
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Total Arrangements" value={statistics.totalArrangements} prefix={<SwapOutlined />} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Average Coverage" value={statistics.averageCoverage} suffix="%" prefix={<TrophyOutlined />} valueStyle={{ color: '#52c41a' }} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Ideal Matches" value={statistics.idealMatches} prefix={<TrophyOutlined />} valueStyle={{ color: '#52c41a' }} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Acceptable Matches" value={statistics.acceptableMatches} prefix={<CalendarOutlined />} valueStyle={{ color: '#faad14' }} />
            </Col>
          </Row>
        );
        
      case 'teacher_performance':
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Total Teachers" value={statistics.totalTeachers} prefix={<UserOutlined />} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Average Attendance" value={statistics.averageAttendance} suffix="%" prefix={<BarChartOutlined />} valueStyle={{ color: '#1890ff' }} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Top Performers" value={statistics.topPerformers} prefix={<TrophyOutlined />} valueStyle={{ color: '#52c41a' }} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="Need Improvement" value={statistics.needsImprovement} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#ff4d4f' }} />
            </Col>
          </Row>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="reports-management">
      <Card className="header-card">
        <div className="header-content">
          <div>
            <Title level={2} className="page-title">
              <BarChartOutlined style={{ marginRight: 12 }} />
              Reports & Analytics
            </Title>
            <Text type="secondary">Generate comprehensive reports and insights</Text>
          </div>
          <Space>
            <Select
              value={reportType}
              onChange={setReportType}
              style={{ width: 200 }}
              placeholder="Select report type"
            >
              <Option value="attendance">Attendance Report</Option>
              <Option value="arrangements">Arrangements Report</Option>
              <Option value="teacher_performance">Teacher Performance</Option>
            </Select>
            <RangePicker
              value={dateRange}
              onChange={setDateRange}
              format="YYYY-MM-DD"
            />
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={exportReport}
              disabled={reportData.length === 0}
            >
              Export
            </Button>
          </Space>
        </div>
      </Card>

      {/* Statistics */}
      <Card className="statistics-card" style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 24 }}>Summary Statistics</Title>
        {renderStatistics()}
      </Card>

      {/* Report Table */}
      <Card className="content-card">
        <div style={{ marginBottom: 16 }}>
          <Title level={4}>
            {reportType === 'attendance' && 'Teacher Attendance Summary'}
            {reportType === 'arrangements' && 'Daily Arrangements Summary'}
            {reportType === 'teacher_performance' && 'Teacher Performance Analysis'}
          </Title>
          <Text type="secondary">
            Report period: {dateRange[0].format('MMMM DD, YYYY')} to {dateRange[1].format('MMMM DD, YYYY')}
          </Text>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" />
          </div>
        ) : reportData.length === 0 ? (
          <Empty description="No data available for the selected period" />
        ) : (
          <Table
            columns={getColumns()}
            dataSource={reportData}
            rowKey={(record) => record.teacher_id || record.date || Math.random()}
            pagination={{
              pageSize: 15,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} records`
            }}
            scroll={{ x: 1000 }}
            className="reports-table"
          />
        )}
      </Card>
    </div>
  );
};

export default ReportsManagement;