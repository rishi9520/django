import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  DatePicker,
  Space,
  Typography,
  Tag,
  Select,
  Row,
  Col,
  Statistic,
  Modal,
  Form,
  Input,
  TimePicker,
  message,
  Alert,
  Progress,
  Spin
} from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  CalendarOutlined,
  DownloadOutlined,
  EditOutlined,
  UserOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { apiService } from '../services/apiService';
import '../styles/AttendanceManagement.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const AttendanceManagement = () => {
  const [loading, setLoading] = useState(false);
  const [dailyAttendance, setDailyAttendance] = useState([]);
  const [attendanceReport, setAttendanceReport] = useState([]);
  const [selectedDate, setSelectedDate] = useState(moment());
  const [dateRange, setDateRange] = useState([moment().subtract(7, 'days'), moment()]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form] = Form.useForm();
  const [stats, setStats] = useState({
    total: 0,
    present: 0,
    absent: 0,
    rate: 0
  });

  const user = JSON.parse(localStorage.getItem('user'));
  const schoolId = user?.school_id;

  useEffect(() => {
    if (schoolId) {
      fetchDailyAttendance();
    }
  }, [schoolId, selectedDate]);

  useEffect(() => {
    if (schoolId && dateRange[0] && dateRange[1]) {
      fetchAttendanceReport();
    }
  }, [schoolId, dateRange]);

  const fetchDailyAttendance = async () => {
    setLoading(true);
    try {
      const dateStr = selectedDate.format('YYYY-MM-DD');
      const response = await apiService.getDailyAttendance(schoolId, dateStr);
      const attendance = response.daily_attendance || [];
      
      setDailyAttendance(attendance);
      
      // Calculate statistics
      const total = attendance.length;
      const present = attendance.filter(a => a.status === 'present').length;
      const absent = attendance.filter(a => a.status === 'absent').length;
      const rate = total > 0 ? Math.round((present / total) * 100) : 0;
      
      setStats({ total, present, absent, rate });
    } catch (error) {
      console.error('Error fetching daily attendance:', error);
      message.error('Failed to fetch attendance data');
    } finally {
      setLoading(false);
    }
  };

  const fetchAttendanceReport = async () => {
    try {
      const startDate = dateRange[0].format('YYYY-MM-DD');
      const endDate = dateRange[1].format('YYYY-MM-DD');
      const response = await apiService.getAttendanceReport(schoolId, startDate, endDate);
      setAttendanceReport(response.attendance || []);
    } catch (error) {
      console.error('Error fetching attendance report:', error);
      message.error('Failed to fetch attendance report');
    }
  };

  const handleMarkAttendance = async (values) => {
    try {
      await apiService.markAttendance(schoolId, {
        teacher_id: editingRecord.teacher_id,
        date: selectedDate.format('YYYY-MM-DD'),
        status: values.status,
        check_in_time: values.check_in_time ? values.check_in_time.format('HH:mm') : null,
        check_out_time: values.check_out_time ? values.check_out_time.format('HH:mm') : null
      });
      
      message.success('Attendance marked successfully');
      setModalVisible(false);
      form.resetFields();
      fetchDailyAttendance();
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to mark attendance';
      message.error(errorMsg);
    }
  };

  const openAttendanceModal = (record) => {
    setEditingRecord(record);
    form.setFieldsValue({
      status: record.status !== 'not_marked' ? record.status : 'present',
      check_in_time: record.check_in_time ? moment(record.check_in_time, 'HH:mm') : null,
      check_out_time: record.check_out_time ? moment(record.check_out_time, 'HH:mm') : null
    });
    setModalVisible(true);
  };

  const exportAttendanceReport = () => {
    if (attendanceReport.length === 0) {
      message.warning('No data to export');
      return;
    }

    const csvContent = [
      ['Date', 'Teacher ID', 'Teacher Name', 'Status', 'Check In', 'Check Out'],
      ...attendanceReport.map(record => [
        record.date,
        record.teacher_id,
        record.teacher_name,
        record.status,
        record.check_in_time || '',
        record.check_out_time || ''
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_report_${schoolId}_${dateRange[0].format('YYYY-MM-DD')}_to_${dateRange[1].format('YYYY-MM-DD')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const dailyColumns = [
    {
      title: 'Teacher ID',
      dataIndex: 'teacher_id',
      key: 'teacher_id',
      width: 120
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name) => (
        <Space>
          <UserOutlined />
          <span>{name}</span>
        </Space>
      )
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (category) => {
        const colors = { TGT: 'blue', PGT: 'green', PRT: 'orange' };
        return <Tag color={colors[category] || 'default'}>{category}</Tag>;
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const configs = {
          present: { color: '#52c41a', icon: <CheckCircleOutlined />, text: 'Present' },
          absent: { color: '#ff4d4f', icon: <ExclamationCircleOutlined />, text: 'Absent' },
          late: { color: '#faad14', icon: <ClockCircleOutlined />, text: 'Late' },
          not_marked: { color: '#d9d9d9', icon: <ClockCircleOutlined />, text: 'Not Marked' }
        };
        const config = configs[status] || configs.not_marked;
        
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: 'Check In',
      dataIndex: 'check_in_time',
      key: 'check_in_time',
      render: (time) => time || <Text type="secondary">-</Text>
    },
    {
      title: 'Check Out',
      dataIndex: 'check_out_time',
      key: 'check_out_time',
      render: (time) => time || <Text type="secondary">-</Text>
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EditOutlined />}
          onClick={() => openAttendanceModal(record)}
          size="small"
        >
          Mark
        </Button>
      )
    }
  ];

  const reportColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => moment(a.date).unix() - moment(b.date).unix()
    },
    {
      title: 'Teacher ID',
      dataIndex: 'teacher_id',
      key: 'teacher_id'
    },
    {
      title: 'Teacher Name',
      dataIndex: 'teacher_name',
      key: 'teacher_name'
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const configs = {
          present: { color: '#52c41a', icon: <CheckCircleOutlined />, text: 'Present' },
          absent: { color: '#ff4d4f', icon: <ExclamationCircleOutlined />, text: 'Absent' },
          late: { color: '#faad14', icon: <ClockCircleOutlined />, text: 'Late' }
        };
        const config = configs[status] || configs.present;
        
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: 'Check In',
      dataIndex: 'check_in_time',
      key: 'check_in_time'
    },
    {
      title: 'Check Out',
      dataIndex: 'check_out_time',
      key: 'check_out_time'
    }
  ];

  return (
    <div className="attendance-management">
      <Card className="header-card">
        <div className="header-content">
          <div>
            <Title level={2} className="page-title">
              <CheckCircleOutlined style={{ marginRight: 12 }} />
              Attendance Management
            </Title>
            <Text type="secondary">Track and manage teacher attendance</Text>
          </div>
          <Space>
            <DatePicker
              value={selectedDate}
              onChange={setSelectedDate}
              format="YYYY-MM-DD"
              placeholder="Select date"
            />
            <Button 
              icon={<CalendarOutlined />} 
              onClick={fetchDailyAttendance}
              loading={loading}
            >
              Refresh
            </Button>
          </Space>
        </div>
      </Card>

      {/* Statistics Cards */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <Statistic
              title="Total Teachers"
              value={stats.total}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <Statistic
              title="Present"
              value={stats.present}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <Statistic
              title="Absent"
              value={stats.absent}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card className="stat-card">
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={stats.rate}
                size={80}
                format={percent => `${percent}%`}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <Text strong style={{ display: 'block', marginTop: 8 }}>
                Attendance Rate
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Daily Attendance */}
      <Card 
        title={
          <Space>
            <CalendarOutlined />
            <span>Daily Attendance - {selectedDate.format('MMMM DD, YYYY')}</span>
          </Space>
        }
        className="content-card"
        style={{ marginBottom: 24 }}
      >
        {stats.absent > 0 && (
          <Alert
            message={`${stats.absent} teacher(s) are absent today. Arrangements may be needed.`}
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
            action={
              <Button size="small" onClick={() => window.location.href = '/arrangements'}>
                View Arrangements
              </Button>
            }
          />
        )}
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" />
          </div>
        ) : (
          <Table
            columns={dailyColumns}
            dataSource={dailyAttendance}
            rowKey="teacher_id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => 
                `${range[0]}-${range[1]} of ${total} teachers`
            }}
            scroll={{ x: 800 }}
            className="attendance-table"
          />
        )}
      </Card>

      {/* Attendance Report */}
      <Card 
        title={
          <Space>
            <DownloadOutlined />
            <span>Attendance Report</span>
          </Space>
        }
        extra={
          <Space>
            <RangePicker
              value={dateRange}
              onChange={setDateRange}
              format="YYYY-MM-DD"
            />
            <Button
              icon={<DownloadOutlined />}
              onClick={exportAttendanceReport}
              disabled={attendanceReport.length === 0}
            >
              Export CSV
            </Button>
          </Space>
        }
        className="content-card"
      >
        <Table
          columns={reportColumns}
          dataSource={attendanceReport}
          rowKey={(record) => `${record.teacher_id}-${record.date}`}
          pagination={{
            pageSize: 15,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} of ${total} records`
          }}
          scroll={{ x: 800 }}
          className="attendance-table"
        />
      </Card>

      {/* Mark Attendance Modal */}
      <Modal
        title={`Mark Attendance - ${editingRecord?.name}`}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleMarkAttendance}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            name="status"
            label="Attendance Status"
            rules={[{ required: true, message: 'Please select status' }]}
          >
            <Select placeholder="Select attendance status">
              <Option value="present">Present</Option>
              <Option value="absent">Absent</Option>
              <Option value="late">Late</Option>
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="check_in_time"
                label="Check In Time"
              >
                <TimePicker
                  format="HH:mm"
                  placeholder="Select check in time"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="check_out_time"
                label="Check Out Time"
              >
                <TimePicker
                  format="HH:mm"
                  placeholder="Select check out time"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                Mark Attendance
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AttendanceManagement;