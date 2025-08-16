import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  Space,
  Badge,
  Divider,
  Modal,
  message
} from 'antd';
import {
  CrownOutlined,
  CheckOutlined,
  StarOutlined,
  RocketOutlined
} from '@ant-design/icons';
import '../styles/BillingManagement.css';

const { Title, Text, Paragraph } = Typography;

const BillingManagement = () => {
  const [upgradeModalVisible, setUpgradeModalVisible] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const plans = [
    {
      id: 'basic',
      name: 'Basic Plan',
      price: '₹999',
      duration: 'per month',
      popular: false,
      features: [
        'Up to 50 Teachers',
        'Basic Attendance Tracking',
        'Simple Reports',
        'Email Support',
        'Basic Arrangement System'
      ],
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      id: 'professional',
      name: 'Professional',
      price: '₹2,499',
      duration: 'per month',
      popular: true,
      features: [
        'Up to 200 Teachers',
        'Advanced Attendance Analytics',
        'Comprehensive Reports',
        'Priority Support',
        'Auto Arrangement System',
        'WhatsApp Integration',
        'Biometric Integration',
        'Custom Branding'
      ],
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '₹4,999',
      duration: 'per month',
      popular: false,
      features: [
        'Unlimited Teachers',
        'AI-Powered Analytics',
        'Advanced Reporting Suite',
        '24/7 Phone Support',
        'Smart Arrangement Engine',
        'Multi-School Management',
        'API Access',
        'Custom Integrations',
        'Dedicated Account Manager'
      ],
      color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    }
  ];

  const handleUpgrade = (plan) => {
    setSelectedPlan(plan);
    setUpgradeModalVisible(true);
  };

  const handlePurchase = () => {
    message.success(`Thank you for choosing ${selectedPlan.name}! Our team will contact you shortly.`);
    setUpgradeModalVisible(false);
  };

  return (
    <div className="billing-management">
      <Card className="billing-header">
        <div className="billing-header-content">
          <div className="billing-title-section">
            <Title level={1} className="billing-title">
              <CrownOutlined style={{ marginRight: 12 }} />
              School Management Plans
            </Title>
            <Paragraph className="billing-subtitle">
              Choose the perfect plan for your school's needs. Upgrade anytime with no hidden fees.
            </Paragraph>
          </div>
        </div>
      </Card>

      <div className="plans-container">
        <Row gutter={[24, 24]} justify="center">
          {plans.map((plan) => (
            <Col xs={24} md={8} key={plan.id}>
              <Card className={`plan-card ${plan.popular ? 'popular-plan' : ''}`}>
                {plan.popular && (
                  <div className="popular-badge">
                    <StarOutlined /> MOST POPULAR
                  </div>
                )}
                
                <div className="plan-header">
                  <Title level={3} className="plan-name">
                    {plan.name}
                  </Title>
                  <div className="plan-pricing">
                    <span className="plan-price">{plan.price}</span>
                    <span className="plan-duration">/{plan.duration}</span>
                  </div>
                </div>

                <Divider />

                <div className="plan-features">
                  <ul className="feature-list">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="feature-item">
                        <CheckOutlined className="feature-check" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="plan-action">
                  <Button
                    type={plan.popular ? "primary" : "default"}
                    size="large"
                    block
                    className="plan-button"
                    onClick={() => handleUpgrade(plan)}
                    icon={plan.id === 'enterprise' ? <RocketOutlined /> : undefined}
                  >
                    {plan.id === 'basic' ? 'Get Started' : 'Upgrade Now'}
                  </Button>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </div>

      <Card className="features-showcase">
        <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
          Why Choose Our School Management System?
        </Title>
        
        <Row gutter={[32, 32]}>
          <Col xs={24} md={8}>
            <div className="showcase-item">
              <div className="showcase-icon">
                <CheckOutlined />
              </div>
              <Title level={4}>Smart Automation</Title>
              <Text>Automatic teacher arrangements and attendance tracking save hours of manual work.</Text>
            </div>
          </Col>
          <Col xs={24} md={8}>
            <div className="showcase-item">
              <div className="showcase-icon">
                <StarOutlined />
              </div>
              <Title level={4}>Professional Reports</Title>
              <Text>Generate comprehensive reports with beautiful charts and analytics.</Text>
            </div>
          </Col>
          <Col xs={24} md={8}>
            <div className="showcase-item">
              <div className="showcase-icon">
                <RocketOutlined />
              </div>
              <Title level={4}>24/7 Support</Title>
              <Text>Get help whenever you need it with our dedicated support team.</Text>
            </div>
          </Col>
        </Row>
      </Card>

      <Modal
        title={`Upgrade to ${selectedPlan?.name}`}
        open={upgradeModalVisible}
        onCancel={() => setUpgradeModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setUpgradeModalVisible(false)}>
            Cancel
          </Button>,
          <Button key="purchase" type="primary" onClick={handlePurchase}>
            Proceed with Purchase
          </Button>
        ]}
        width={600}
      >
        {selectedPlan && (
          <div style={{ padding: '20px 0' }}>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Title level={3}>{selectedPlan.name}</Title>
              <Text style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1890ff' }}>
                {selectedPlan.price}
              </Text>
              <Text style={{ fontSize: '1rem', color: '#666', marginLeft: 8 }}>
                /{selectedPlan.duration}
              </Text>
            </div>
            
            <Divider />
            
            <Title level={4}>What's included:</Title>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {selectedPlan.features.map((feature, index) => (
                <li key={index} style={{ padding: '8px 0', display: 'flex', alignItems: 'center' }}>
                  <CheckOutlined style={{ color: '#52c41a', marginRight: 12 }} />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            
            <div style={{ background: '#f6ffed', padding: 16, borderRadius: 8, marginTop: 24, border: '1px solid #b7eb8f' }}>
              <Text strong style={{ color: '#389e0d' }}>
                🎉 Special Offer: Get 1 month free with annual billing!
              </Text>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BillingManagement;