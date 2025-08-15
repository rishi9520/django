import React from 'react';
import { Card, Typography, Alert } from 'antd';

const { Title } = Typography;

const AttendanceManagement = ({ user }) => {
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={3}>Attendance Management</Title>
        <Alert
          message="Under Development"
          description="This feature will integrate with the preserved attendance logic from the original system."
          type="info"
          showIcon
        />
      </Card>
    </div>
  );
};

export default AttendanceManagement;