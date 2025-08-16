import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Table,
  Tag,
  Button,
  Modal,
  Form,
  Select,
  Input,
  DatePicker,
  Space,
  Typography,
  Alert,
  Empty,
  Spin,
  message,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  SwapOutlined,
  PlusOutlined,
  ReloadOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  UserOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { apiService } from '../services/apiService';
import '../styles/ArrangementManagement.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const ArrangementManagementPro = () => {
  const [loading, setLoading] = useState(false);
  const [arrangements, setArrangements] = useState([]);
  const [absentTeachers, setAbsentTeachers] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [selectedDate, setSelectedDate] = useState(moment());
  const [manualModalVisible, setManualModalVisible] = useState(false);
  const [form] = Form.useForm();

  const user = JSON.parse(localStorage.getItem('user'));
  const schoolId = user?.school_id;

  useEffect(() => {
    if (schoolId) {
      fetchData();
    }
  }, [schoolId, selectedDate]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const dateStr = selectedDate.format('YYYY-MM-DD');
      
      // Fetch all data in parallel
      const [arrangementsRes, absentRes, teachersRes] = await Promise.all([
        apiService.getArrangements(schoolId, dateStr),
        apiService.getAbsentTeachers(schoolId, dateStr),
        apiService.getTeachers(schoolId)
      ]);

      setArrangements(arrangementsRes.arrangements || []);
      setAbsentTeachers(absentRes.absent_teachers || []);
      setTeachers(teachersRes.teachers || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      message.error('Failed to fetch arrangement data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateManualArrangement = async (values) => {
    try {
      await apiService.createManualArrangement(schoolId, {
        ...values,
        date: selectedDate.format('YYYY-MM-DD')
      });
      message.success('Manual arrangement created successfully');
      setManualModalVisible(false);
      form.resetFields();
      fetchData();
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to create arrangement';
      message.error(errorMsg);
    }
  };

  const arrangementsColumns = [
    {
      title: 'Period',
      dataIndex: 'period',
      key: 'period',
      width: 80,
      sorter: (a, b) => a.period - b.period
    },
    {
      title: 'Subject',
      dataIndex: 'subject',
      key: 'subject'
    },
    {
      title: 'Class',
      key: 'class',
      render: (_, record) => `${record.class_name}${record.section ? ` - ${record.section}` : ''}`
    },
    {
      title: 'Absent Teacher',
      dataIndex: 'absent_teacher_name',
      key: 'absent_teacher_name',
      render: (name, record) => (
        <Space>
          <UserOutlined style={{ color: '#faad14' }} />
          <span>{name || record.absent_teacher_id}</span>
        </Space>
      )
    },
    {
      title: 'Replacement Teacher',
      dataIndex: 'replacement_teacher_name',
      key: 'replacement_teacher_name',
      render: (name, record) => (
        <Space>
          <UserOutlined style={{ color: '#52c41a' }} />
          <span>{name || record.replacement_teacher_id}</span>
        </Space>
      )
    },
    {
      title: 'Match Quality',
      dataIndex: 'match_quality',
      key: 'match_quality',
      render: (quality) => {
        const configs = {
          ideal: { color: '#52c41a', icon: <CheckCircleOutlined /> },
          acceptable: { color: '#faad14', icon: <ClockCircleOutlined /> },
          fallback: { color: '#ff4d4f', icon: <ExclamationCircleOutlined /> },
          manual: { color: '#722ed1', icon: <UserOutlined /> }
        };
        const config = configs[quality?.toLowerCase()] || configs.fallback;
        
        return (
          <Tag color={config.color} icon={config.icon}>
            {quality?.toUpperCase() || 'UNKNOWN'}
          </Tag>
        );
      }
    }
  ];

  const absentTeachersColumns = [
    {
      title: 'Teacher ID',
      dataIndex: 'teacher_id',
      key: 'teacher_id'
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name) => (
        <Space>
          <UserOutlined style={{ color: '#faad14' }} />
          <span>{name}</span>
        </Space>
      )
    }
  ];

  return (
    <div className="arrangement-management">
      <Card className="header-card">
        <div className="header-content">
          <div>
            <Title level={2} className="page-title">
              <SwapOutlined style={{ marginRight: 12 }} />
              Teacher Arrangements
            </Title>
            <Text type="secondary">Manage automatic and manual teacher arrangements</Text>
          </div>
          <Space>
            <DatePicker
              value={selectedDate}
              onChange={setSelectedDate}
              format="YYYY-MM-DD"
              placeholder="Select date"
            />
            <Button 
              icon={<ReloadOutlined />} 
              onClick={fetchData}
              loading={loading}
            >
              Refresh
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setManualModalVisible(true)}
            >
              Create Manual Arrangement
            </Button>
          </Space>
        </div>
      </Card>

      {/* Summary Statistics */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="Total Arrangements"
              value={arrangements.length}
              prefix={<SwapOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="Absent Teachers"
              value={absentTeachers.length}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="Coverage Rate"
              value={absentTeachers.length > 0 ? Math.round((arrangements.length / absentTeachers.length) * 100) : 100}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card className="content-card">
        <Tabs defaultActiveKey="arrangements" className="arrangement-tabs">
          <TabPane tab="Today's Arrangements" key="arrangements">
            {loading ? (
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" />
              </div>
            ) : arrangements.length === 0 ? (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  <div>
                    <Title level={4}>No Arrangements Needed</Title>
                    <Text type="secondary">
                      All teachers are present for {selectedDate.format('MMMM DD, YYYY')}
                    </Text>
                  </div>
                }
              />
            ) : (
              <>
                <Alert
                  message={`${arrangements.length} arrangements have been created for ${selectedDate.format('MMMM DD, YYYY')}`}
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  columns={arrangementsColumns}
                  dataSource={arrangements}
                  rowKey="id"
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total, range) => 
                      `${range[0]}-${range[1]} of ${total} arrangements`
                  }}
                  scroll={{ x: 1000 }}
                  className="arrangements-table"
                />
              </>
            )}
          </TabPane>

          <TabPane tab="Absent Teachers" key="absent">
            {loading ? (
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" />
              </div>
            ) : absentTeachers.length === 0 ? (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  <div>
                    <Title level={4}>Perfect Attendance!</Title>
                    <Text type="secondary">
                      All teachers are present for {selectedDate.format('MMMM DD, YYYY')}
                    </Text>
                  </div>
                }
              />
            ) : (
              <>
                <Alert
                  message={`${absentTeachers.length} teacher(s) are absent on ${selectedDate.format('MMMM DD, YYYY')}`}
                  type="warning"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  columns={absentTeachersColumns}
                  dataSource={absentTeachers}
                  rowKey="teacher_id"
                  pagination={false}
                  className="absent-teachers-table"
                />
              </>
            )}
          </TabPane>
        </Tabs>
      </Card>

      {/* Create Manual Arrangement Modal */}
      <Modal
        title="Create Manual Arrangement"
        open={manualModalVisible}
        onCancel={() => {
          setManualModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
        className="manual-arrangement-modal"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateManualArrangement}
          style={{ marginTop: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="absent_teacher_id"
                label="Absent Teacher"
                rules={[{ required: true, message: 'Please select absent teacher' }]}
              >
                <Select
                  placeholder="Select absent teacher"
                  showSearch
                  optionFilterProp="children"
                >
                  {teachers.map(teacher => (
                    <Option key={teacher.teacher_id} value={teacher.teacher_id}>
                      {teacher.name} ({teacher.teacher_id})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="replacement_teacher_id"
                label="Replacement Teacher"
                rules={[{ required: true, message: 'Please select replacement teacher' }]}
              >
                <Select
                  placeholder="Select replacement teacher"
                  showSearch
                  optionFilterProp="children"
                >
                  {teachers.map(teacher => (
                    <Option key={teacher.teacher_id} value={teacher.teacher_id}>
                      {teacher.name} ({teacher.teacher_id})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item
                name="period"
                label="Period"
                rules={[{ required: true, message: 'Please enter period' }]}
              >
                <Input placeholder="Enter period number" type="number" min={1} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item
                name="subject"
                label="Subject"
                rules={[{ required: true, message: 'Please enter subject' }]}
              >
                <Input placeholder="Enter subject name" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item
                name="class_name"
                label="Class"
                rules={[{ required: true, message: 'Please enter class' }]}
              >
                <Input placeholder="Enter class name" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="section"
            label="Section (Optional)"
          >
            <Input placeholder="Enter section (e.g., A, B, C)" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setManualModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                Create Arrangement
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ArrangementManagementPro;