import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Card, 
  Typography, 
  Space, 
  Input, 
  Tag,
  Modal,
  Form,
  message,
  Spin
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  SearchOutlined,
  UserOutlined 
} from '@ant-design/icons';
import { apiService } from '../services/apiService';
import '../styles/TeacherManagement.css';

const { Title } = Typography;
const { Search } = Input;

const TeacherManagement = () => {
  const user = JSON.parse(localStorage.getItem('user'));
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);
  const [form] = Form.useForm();
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    fetchTeachers();
  }, [user]);

  const fetchTeachers = async () => {
    try {
      setLoading(true);
      const response = await apiService.getTeachers(user.school_id);
      setTeachers(response.teachers || []);
    } catch (error) {
      console.error('Error fetching teachers:', error);
      message.error('Failed to load teachers');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTeacher = () => {
    setEditingTeacher(null);
    form.resetFields();
    form.setFieldsValue({ school: user.school_id });
    setModalVisible(true);
  };

  const handleEditTeacher = (record) => {
    setEditingTeacher(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDeleteTeacher = async (record) => {
    Modal.confirm({
      title: 'Delete Teacher',
      content: `Are you sure you want to delete ${record.name}?`,
      onOk: async () => {
        try {
          await apiService.deleteTeacher(user.school_id, record.teacher_id);
          message.success('Teacher deleted successfully');
          fetchTeachers();
        } catch (error) {
          message.error('Failed to delete teacher');
        }
      },
    });
  };

  const handleSubmit = async (values) => {
    try {
      if (editingTeacher) {
        await apiService.updateTeacher(user.school_id, editingTeacher.teacher_id, values);
        message.success('Teacher updated successfully');
      } else {
        await apiService.addTeacher(user.school_id, values);
        message.success('Teacher added successfully');
      }
      setModalVisible(false);
      fetchTeachers();
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to save teacher';
      message.error(errorMsg);
    }
  };

  const columns = [
    {
      title: 'Teacher ID',
      dataIndex: 'teacher_id',
      key: 'teacher_id',
      width: 120,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      filteredValue: searchText ? [searchText] : null,
      onFilter: (value, record) =>
        record.name.toLowerCase().includes(value.toLowerCase()) ||
        record.teacher_id.toLowerCase().includes(value.toLowerCase()),
    },
    {
      title: 'Phone',
      dataIndex: 'phone',
      key: 'phone',
      width: 130,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => (
        <Tag color={category === 'Principal' ? 'red' : category === 'Vice Principal' ? 'orange' : 'blue'}>
          {category}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditTeacher(record)}
          >
            Edit
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteTeacher(record)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>
            Teacher Management
          </Title>
          <Space>
            <Search
              placeholder="Search teachers..."
              allowClear
              style={{ width: 250 }}
              onChange={(e) => setSearchText(e.target.value)}
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddTeacher}
            >
              Add Teacher
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={teachers}
          rowKey="teacher_id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `Total ${total} teachers`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* Add/Edit Teacher Modal */}
      <Modal
        title={editingTeacher ? 'Edit Teacher' : 'Add Teacher'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="school" hidden>
            <Input />
          </Form.Item>

          <Form.Item
            name="teacher_id"
            label="Teacher ID"
            rules={[{ required: true, message: 'Please enter teacher ID' }]}
          >
            <Input placeholder="Enter teacher ID" />
          </Form.Item>

          <Form.Item
            name="name"
            label="Name"
            rules={[{ required: true, message: 'Please enter teacher name' }]}
          >
            <Input placeholder="Enter teacher name" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="Phone"
            rules={[{ required: true, message: 'Please enter phone number' }]}
          >
            <Input placeholder="Enter phone number" />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true, message: 'Please enter category' }]}
          >
            <Input placeholder="e.g., Teacher, Principal, Vice Principal" />
          </Form.Item>

          <Form.Item
            name="biometric_code"
            label="Biometric Code"
          >
            <Input placeholder="Enter biometric code (optional)" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {editingTeacher ? 'Update' : 'Add'} Teacher
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TeacherManagement;