import React from 'react';
import { Card, Typography, Alert } from 'antd';

const { Title } = Typography;

const Reports = ({ user }) => {
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={3}>Reports & Analytics</Title>
        <Alert
          message="Under Development"
          description="This feature will show various reports and analytics for the school management system."
          type="info"
          showIcon
        />
      </Card>
    </div>
  );
};

export default Reports;