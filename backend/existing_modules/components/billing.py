import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import data_manager
import time

def load_billing_css():
    """Load professional billing-specific CSS styling"""
    st.markdown("""
    <style>
    /* Billing Page Specific Styles */
    .billing-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #475569;
    }
    
    .plan-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    
    .plan-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid #475569;
        border-radius: 20px;
        padding: 2.5rem;
        max-width: 400px;
        min-width: 350px;
        position: relative;
        transition: all 0.4s ease;
        overflow: hidden;
    }
    
    .plan-card:hover {
        transform: translateY(-10px);
        border-color: #3b82f6;
        box-shadow: 0 25px 50px rgba(59, 130, 246, 0.2);
    }
    
    .plan-card.enterprise {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        position: relative;
    }
    
    .plan-card.enterprise::before {
        content: "POPULAR";
        position: absolute;
        top: 15px;
        right: -35px;
        background: #ef4444;
        color: white;
        padding: 8px 40px;
        transform: rotate(45deg);
        font-size: 0.8rem;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
    }
    
    .plan-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .plan-price {
        font-size: 3.5rem;
        font-weight: 800;
        color: #3b82f6;
        text-align: center;
        margin: 1.5rem 0;
        text-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    
    .plan-duration {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 1.5rem 0;
    }
    
    .feature-list li {
        padding: 0.7rem 0;
        color: #e2e8f0;
        position: relative;
        padding-left: 2rem;
    }
    
    .feature-list li::before {
        content: "✓";
        color: #10b981;
        font-weight: bold;
        font-size: 1.2rem;
        position: absolute;
        left: 0;
        top: 0.7rem;
    }
    
    .premium-btn {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        text-align: center;
        margin-top: 1rem;
    }
    
    .premium-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    }
    
    /* Payment Methods */
    .payment-container {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #4b5563;
    }
    
    .payment-method {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        border: 2px solid #6b7280;
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .payment-method:hover {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
    }
    
    .payment-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
    }
    
    .payment-details {
        color: #d1d5db;
        line-height: 1.6;
    }
    
    .payment-details strong {
        color: #3b82f6;
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .error-message {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    /* Current Subscription Status */
    .subscription-status {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 2px solid #10b981;
    }
    
    .subscription-status h4 {
        color: white;
        font-size: 1.4rem;
        margin-bottom: 1rem;
    }
    
    .subscription-status p {
        color: #f0fdf4;
        margin: 0.5rem 0;
    }
    
    /* Icons */
    .icon {
        color: #3b82f6;
        margin-right: 0.5rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .plan-container {
            flex-direction: column;
            align-items: center;
        }
        
        .plan-card {
            min-width: 280px;
            max-width: 100%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_billing_plans():
    """Get available billing plans for schools"""
    return [
        {
            'id': 1,
            'name': 'Smart School',
            'price_monthly': 2000,
            'price_annual': 22000,
            'price_usd_monthly': 24,
            'price_usd_annual': 264,
            'duration': 12,
            'features': [
                'Complete teacher management system',
                'Automated substitute arrangements',
                'WhatsApp notifications for all staff',
                'Student attendance tracking',
                'Basic analytics and reports',
                'Email support during business hours',
                'Secure data backup',
                'Mobile-responsive design',
                'Basic school customization'
            ],
            'popular': False
        },
        {
            'id': 2,
            'name': 'Premium School',
            'price_monthly': 2500,
            'price_annual': 27000,
            'price_usd_monthly': 30,
            'price_usd_annual': 324,
            'duration': 12,
            'features': [
                'All Smart School features included',
                'Advanced analytics dashboard',
                'Priority 24/7 phone & WhatsApp support',
                'Multi-campus management',
                'Parent notification system',
                'API access for school software',
                'Advanced reporting & insights',
                'Custom school branding',
                'Dedicated account manager',
                'Priority feature requests'
            ],
            'popular': True
        }
    ]

def get_subscription_status(school_id):
    """Get current subscription status for a school"""
    try:
        # Try to get from database first
        connection = data_manager.get_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM subscriptions 
                WHERE school_id = %s AND status = 'active' 
                ORDER BY created_at DESC LIMIT 1
            """, (school_id,))
            subscription = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if subscription:
                return subscription
    except Exception as e:
        # Fallback for demo purposes
        pass
    
    # # Demo subscription for S001
    # if school_id == 'S001':
    #     return {
    #         'school_id': 'S001',
    #         'plan_name': 'Professional',
    #         'price': 2000.00,
    #         'start_date': datetime.now().date(),
    #         'end_date': datetime.now().date() + timedelta(days=365),
    #         'status': 'active',
    #         'payment_method': 'Bank Transfer'
    #     }
    
    return None

def create_payment_record(school_id, plan_id, plan_name, amount, payment_method):
    """Create payment record and subscription"""
    try:
        connection = data_manager.get_connection()
        if connection:
            cursor = connection.cursor()
            
            transaction_id = f"TXN{int(time.time())}"
            
            # Create subscription record
            cursor.execute("""
                INSERT INTO subscriptions 
                (school_id, plan_id, plan_name, amount, start_date, end_date, status, payment_method, transaction_id)
                VALUES (%s, %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 12 MONTH), 'active', %s, %s)
                ON DUPLICATE KEY UPDATE
                plan_id = VALUES(plan_id),
                plan_name = VALUES(plan_name),
                amount = VALUES(amount),
                end_date = DATE_ADD(CURDATE(), INTERVAL 12 MONTH),
                status = 'active',
                payment_method = VALUES(payment_method),
                transaction_id = VALUES(transaction_id)
            """, (school_id, plan_id, plan_name, amount, payment_method, transaction_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            return transaction_id
    except Exception as e:
        st.error(f"Database error: {e}")
    
    # Return demo transaction ID
    return f"DEMO_TXN_{int(time.time())}"

def render_billing_page():
    """Render the professional billing and subscription page"""
    
    load_billing_css()
    
    # Header
    st.markdown("""
    <div class="billing-header">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">
            <i class="fas fa-graduation-cap icon"></i>
            Choose Your School Plan
        </h1>
        <p style="color: #94a3b8; font-size: 1.2rem; margin: 1rem 0 0 0;">
            Select the perfect solution for your educational institution
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check current subscription
    school_id = st.session_state.get('current_school', 'S001')
    current_subscription = get_subscription_status(school_id)
    
    if current_subscription:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                    padding: 2.5rem; border-radius: 20px; margin: 2rem 0; border: 2px solid #10b981;
                    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.15);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="color: white; margin: 0; font-size: 1.6rem; font-weight: 700;">
                    <i class="fas fa-crown" style="color: #fbbf24; margin-right: 0.5rem;"></i>
                    Active Plan: {current_subscription['plan_name']}
                </h3>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 8px;">
                    <span style="color: white; font-weight: 600; font-size: 0.9rem;">ACTIVE</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                <div style="background: rgba(255,255,255,0.1); padding: 1.2rem; border-radius: 12px;">
                    <p style="color: #f0fdf4; margin: 0; font-size: 0.9rem; margin-bottom: 0.3rem;">Valid Until</p>
                    <p style="color: white; margin: 0; font-size: 1.1rem; font-weight: 600;">{current_subscription['end_date']}</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1.2rem; border-radius: 12px;">
                    <p style="color: #f0fdf4; margin: 0; font-size: 0.9rem; margin-bottom: 0.3rem;">Annual Amount</p>
                    <p style="color: white; margin: 0; font-size: 1.1rem; font-weight: 600;">₹{current_subscription['price']}</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1.2rem; border-radius: 12px;">
                    <p style="color: #f0fdf4; margin: 0; font-size: 0.9rem; margin-bottom: 0.3rem;">Payment Method</p>
                    <p style="color: white; margin: 0; font-size: 1.1rem; font-weight: 600;">{current_subscription.get('payment_method', 'Bank Transfer')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display plans
    plans = get_billing_plans()
    
    st.markdown("<div class='plan-container'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    for i, plan in enumerate(plans):
        with col1 if i == 0 else col2:
            popular_class = "enterprise" if plan['popular'] else ""
            features_html = "".join([f"<li>{feature}</li>" for feature in plan['features']])
            
            st.markdown(f"""
            <div class="plan-card {popular_class}">
                <div class="plan-title">
                    <i class="fas fa-school"></i>
                    {plan['name']}
                </div>
                <div class="plan-price">₹{plan['price_monthly']}</div>
                <div class="plan-duration">per month</div>
                <div style="text-align: center; color: #94a3b8; margin-bottom: 1rem;">
                    Annual: ₹{plan['price_annual']} / ${plan['price_usd_annual']}
                </div>
                <ul class="feature-list">
                    {features_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Choose {plan['name']} Plan", key=f"plan_{plan['id']}", use_container_width=True):
                st.session_state['selected_plan'] = plan
                st.session_state['show_payment'] = True
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Payment section
    if st.session_state.get('show_payment'):
        render_payment_section()

def render_payment_section():
    """Render payment options section"""
    
    if 'selected_plan' not in st.session_state:
        return
    
    plan = st.session_state['selected_plan']
    price_to_display = plan.get('price_annual', plan.get('price_monthly', 0))
    
    st.markdown(f"""
<div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
            padding: 2rem; border-radius: 16px; margin-bottom: 2rem; text-align: center;">
    <h3 style="color: white;">Order Summary</h3>
    <p style="color: #94a3b8;"><strong>Plan:</strong> {plan['name']}</p>
    <p style="color: #94a3b8;"><strong>Duration:</strong> {plan['duration']} months</p>
    <p style="color: white; font-size: 2rem; font-weight: bold;">
        Total: <span style="color: #3b82f6;">₹{price_to_display}</span>
    </p>
</div>
""", unsafe_allow_html=True)
    
    st.markdown("### Select Payment Method")
    
    # UPI Payment Options
    with st.expander("💳 UPI Payment (Recommended)", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="payment-method">
                <div class="payment-title">
                    <i class="fas fa-mobile-alt icon"></i>PhonePe / Google Pay
                </div>
                <div class="payment-details">
                    <strong>UPI ID:</strong> 9520496351@ptaxis<br>
                    <strong>Merchant:</strong> RK Coders<br>
                    <strong>Amount:</strong> $""" + str(plan['price']) + """
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Pay with PhonePe/GPay", key="upi_ptaxis", use_container_width=True):
                process_payment(plan, 'UPI - PhonePe/GPay')
        
        with col2:
            st.markdown("""
            <div class="payment-method">
                <div class="payment-title">
                    <i class="fas fa-university icon"></i>UPI (IBL Bank)
                </div>
                <div class="payment-details">
                    <strong>UPI ID:</strong> 9520496351@ibl<br>
                    <strong>Merchant:</strong> RK Coders<br>
                    <strong>Amount:</strong> $""" + str(plan['price']) + """
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Pay with UPI (IBL)", key="upi_ibl", use_container_width=True):
                process_payment(plan, 'UPI - IBL Bank')
    
    # Bank Transfer
    with st.expander("🏦 Direct Bank Transfer"):
        st.markdown("""
        <div class="payment-method">
            <div class="payment-title">
                <i class="fas fa-university icon"></i>Bank of Baroda Transfer
            </div>
            <div class="payment-details">
                <strong>Account Number:</strong> 33880100003230<br>
                <strong>Account Holder:</strong> Banti Birla<br>
                <strong>Bank:</strong> Bank of Baroda<br>
                <strong>Company:</strong> RK Coders<br>
                <strong>Amount to Transfer:</strong> $""" + str(plan['price']) + """<br>
                <br>
                <em>Please include your school ID (""" + st.session_state.get('current_school', 'S001') + """) in the transfer reference.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Confirm Bank Transfer Payment", key="bank_transfer", use_container_width=True):
            process_payment(plan, 'Bank Transfer')
    
    # Card Payment (Display Only)
    with st.expander("💳 Debit/Credit Card"):
        st.markdown("""
        <div class="payment-method">
            <div class="payment-title">
                <i class="fas fa-credit-card icon"></i>Card Payment Details
            </div>
            <div class="payment-details">
                <strong>Card Number:</strong> 6522 9445 1254 1686<br>
                <strong>Card Holder:</strong> Krishna Birla<br>
                <strong>Company:</strong> RK Coders<br>
                <br>
                <em style="color: #ef4444;">Note: For security, actual card payments would be processed through a secure payment gateway in production.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Process Card Payment", key="card_payment", use_container_width=True):
            process_payment(plan, 'Debit Card')
    
    # Back button
    if st.button("← Back to Plans", use_container_width=True):
        st.session_state.pop('selected_plan', None)
        st.session_state.pop('show_payment', None)
        st.experimental_rerun()

def process_payment(plan, payment_method):
    """Process the payment and create subscription"""
    
    school_id = st.session_state.get('current_school', 'S001')
    
    # Create payment record
    transaction_id = create_payment_record(
        school_id, 
        plan['id'], 
        plan['name'], 
        plan['price'], 
        payment_method
    )
    
    if transaction_id:
        st.markdown(f"""
        <div class="success-message">
            <h3><i class="fas fa-check-circle"></i> Payment Successful!</h3>
            <p><strong>Transaction ID:</strong> {transaction_id}</p>
            <p><strong>Plan:</strong> {plan['name']}</p>
            <p><strong>Amount:</strong> ${plan['price']}</p>
            <p><strong>Valid for:</strong> 12 months from today</p>
            <p>Your subscription has been activated successfully!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()
        
        # Clear session state
        time.sleep(2)
        st.session_state.pop('selected_plan', None)
        st.session_state.pop('show_payment', None)
        st.experimental_rerun()
    else:
        st.markdown("""
        <div class="error-message">
            <h3><i class="fas fa-exclamation-triangle"></i> Payment Failed</h3>
            <p>There was an issue processing your payment. Please try again or contact support.</p>
        </div>
        """, unsafe_allow_html=True)

def render_subscription_analytics():
    """Render subscription analytics for admin"""
    
    st.subheader("📊 Subscription Analytics")
    
    # Sample data for demonstration
    subscription_data = {
        'Plan': ['Professional', 'Enterprise'],
        'Active Subscriptions': [45, 23],
        'Monthly Revenue': [90000, 57500]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=subscription_data['Active Subscriptions'], 
            names=subscription_data['Plan'],
            title="Subscription Distribution",
            color_discrete_sequence=['#3b82f6', '#8b5cf6']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=subscription_data['Plan'],
            y=subscription_data['Monthly Revenue'],
            title="Revenue by Plan",
            color=subscription_data['Plan'],
            color_discrete_sequence=['#3b82f6', '#8b5cf6']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)