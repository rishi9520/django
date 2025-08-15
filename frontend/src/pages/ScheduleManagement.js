import React from 'react';
import { Card, Typography, Alert } from 'antd';

const { Title } = Typography;

const ScheduleManagement = ({ user }) => {
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={3}>Schedule Management</Title>
        <Alert
          message="Under Development"
          description="This feature will show teacher schedules and allow schedule management."
          type="info"
          showIcon
        />
      </Card>
    </div>
  );
};

export default ScheduleManagement;