import streamlit as st
import datetime
import json
import random
from streamlit.components.v1 import html
import streamlit.components.v1 as components


st.markdown(
    """
    <style>
        /* Base Styles and Animations */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        .terms-premium-container {
            font-family: 'Poppins', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            animation: fadeIn 0.8s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes slideRight {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.03); }
            100% { transform: scale(1); }
        }

        /* Premium Headers */
        .premium-header {
            text-align: center;
            margin-bottom: 40px;
            position: relative;
        }

        .premium-title {
            font-size: 3rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 15px;
            text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
        }

        .premium-title::after {
            content: '';
            display: block;
            width: 100px;
            height: 5px;
            background: linear-gradient(90deg, #3B82F6, #1E40AF);
            margin: 15px auto 0;
            border-radius: 10px;
        }

        .premium-subtitle {
            font-size: 1.2rem;
            color: #64748B;
            margin-bottom: 20px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        /* Premium Section Cards */
        .premium-section {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            padding: 30px;
            margin-bottom: 30px;
            border-left: 5px solid #3B82F6;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .premium-section:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(59, 130, 246, 0.15);
        }

        .premium-section::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 150px;
            height: 150px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0));
            border-radius: 0 0 0 100%;
            z-index: 0;
        }

        .premium-section-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
        }

        .premium-section-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            background: linear-gradient(135deg, #3B82F6, #1E40AF);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
            font-size: 24px;
        }

        .premium-section-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1E3A8A;
            margin: 0;
        }

        .premium-section-content {
            position: relative;
            z-index: 1;
            color: #334155;
            font-size: 1.05rem;
            line-height: 1.7;
        }

        .premium-section-content ul {
            padding-left: 20px;
        }

        .premium-section-content li {
            margin-bottom: 12px;
            position: relative;
            padding-left: 10px;
        }

        .premium-section-content li strong {
            color: #1E3A8A;
            font-weight: 600;
        }

        /* Premium Call-to-Action */
        .premium-cta {
            background: linear-gradient(135deg, #1E3A8A, #3B82F6);
            border-radius: 16px;
            padding: 40px;
            color: white;
            text-align: center;
            margin: 50px 0;
            box-shadow: 0 15px 35px rgba(30, 58, 138, 0.3);
            position: relative;
            overflow: hidden;
        }

        .premium-cta::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 70%);
            animation: rotateGradient 10s linear infinite;
            z-index: 0;
        }

        @keyframes rotateGradient {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .premium-cta-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }

        .premium-cta-text {
            font-size: 1.1rem;
            margin-bottom: 30px;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            position: relative;
            z-index: 1;
        }

        .premium-cta-button {
            background: white;
            color: #1E3A8A;
            font-weight: 700;
            font-size: 1.1rem;
            padding: 15px 30px;
            border-radius: 50px;
            text-decoration: none;
            transition: all 0.3s ease;
            display: inline-block;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 1;
        }

        .premium-cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        /* Premium Footer */
        .premium-footer {
            text-align: center;
            margin-top: 70px;
            padding-top: 40px;
            border-top: 1px solid #E2E8F0;
            position: relative;
        }

        .premium-footer-logo {
            margin-bottom: 20px;
        }

        .premium-footer-text {
            color: #64748B;
            margin-bottom: 5px;
            font-size: 0.95rem;
        }

        .premium-copyright {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }

        .premium-copyright-icon {
            margin-right: 10px;
        }

        .premium-social-icons {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            gap: 15px;
        }

        .premium-social-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3B82F6, #1E40AF);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
        }

        .premium-social-icon:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 6px 10px rgba(59, 130, 246, 0.4);
        }

        /* Additional Premium Elements */
        .animated-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E3A8A;
            display: inline-block;
            margin-right: 5px;
        }

        .premium-badge {
            display: inline-block;
            padding: 5px 12px;
            background: linear-gradient(135deg, #3B82F6, #1E40AF);
            color: white;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 10px;
            box-shadow: 0 2px 5px rgba(59, 130, 246, 0.3);
        }

        .premium-list-item {
            display: flex;
            margin-bottom: 15px;
        }

        .premium-list-icon {
            min-width: 22px;
            margin-right: 10px;
            color: #3B82F6;
        }

        .protection-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .protection-item {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            border-left: 3px solid #3B82F6;
        }

        .protection-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
        }

        .protection-icon {
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: #3B82F6;
        }

        .protection-title {
            font-weight: 600;
            color: #1E3A8A;
            margin-bottom: 8px;
            font-size: 1.1rem;
        }

        .protection-text {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .last-updated {
            display: inline-block;
            padding: 8px 15px;
            background: #F1F5F9;
            border-radius: 20px;
            font-size: 0.9rem;
            color: #64748B;
            margin-top: 10px;
        }

        .highlight-text {
            font-weight: 500;
            color: #1E3A8A;
        }

        /* Responsive Adjustments */
        @media (max-width: 768px) {
            .premium-title {
                font-size: 2.2rem;
            }

            .premium-section {
                padding: 25px;
            }

            .premium-section-title {
                font-size: 1.4rem;
            }

            .premium-cta {
                padding: 30px;
            }

            .premium-cta-title {
                font-size: 1.8rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_terms_and_conditions(school_id, data_manager):
    """Render the Terms & Conditions page with professional styling"""

    # Page Title
    # st.title("Terms & Conditions")

    # # Introduction
    # st.info(
    #     "Please read these Terms & Conditions carefully. By accessing or using the "
    #     "**Teacher Attendance System**, you agree to be bound by these terms."
    # )
    st.markdown(
        """
    <div style="margin-right: 5px;color:#1e3a8a;" class="terms-premium-container">
        <div class="premium-header">
            <h1 class="premium-title">Terms & Conditions</h1>
            
    """,
        unsafe_allow_html=True,
    )

    sections = [
        {
            "title": "Ownership & Intellectual Property",
            "icon": "💼",
            "content": """
            This software and its entire contents including but not limited to its:
            
            * **Source code & binary forms** - All programming code, compiled applications and associated files
            * **User interface design** - All visual elements, layouts, and design patterns
            * **Documentation** - All manuals, guides, and supporting materials
            * **Branding elements** - Logos, icons, color schemes and other visual identifiers
            
            are the **exclusive intellectual property** of RK Coders. The software is protected by Indian copyright laws and international treaty provisions.
            
            Any reproduction, modification, or distribution of this software without express written consent from RK Coders is **strictly prohibited** and constitutes a violation of copyright law.
            """,
        },
        {
            "title": "License & Usage Restrictions",
            "icon": "🔐",
            "content": """
            This software is **licensed, not sold**. The license granted herein is:
            
            * **Non-exclusive** - RK Coders may license the software to others
            * **Non-transferable** - You may not transfer or sublicense to others
            * **Limited** - For internal administrative use only
            * **Revocable** - Can be terminated upon violation of these terms
            
            You are **expressly prohibited** from:
            
            * Reverse engineering, decompiling, or disassembling the software
            * Removing or altering any copyright notices or proprietary markings
            * Using the software to develop competing products
            * Distributing, leasing, renting, or sublicensing the software
            * Using the software in any manner that violates applicable laws
            
            Violation of these restrictions will result in automatic license termination and may lead to legal action.
            """,
        },
        {
            "title": "Data Privacy & Security",
            "icon": "🔒",
            "content": """
            RK Coders is committed to protecting your data with industry-standard security measures.

            * **Data Ownership** - All data entered into the system remains your property
            * **Confidentiality** - We treat your data with the highest level of confidentiality
            * **No Data Sharing** - We do not share, sell, or distribute user data to third parties without consent
            * **Data Security** - We implement technical and organizational measures to protect your data

            While we take extensive measures to protect your data, RK Coders shall not be liable for data loss, cyber-attacks, or unauthorized access resulting from user negligence, third-party vulnerabilities, or forces beyond our reasonable control.
            """,
        },
        {
            "title": "Service Availability & Maintenance",
            "icon": "⚙️",
            "content": """
            RK Coders strives to provide maximum uptime and performance, but cannot guarantee 100% service availability.

            * **Scheduled Maintenance** - System may be periodically unavailable for updates and improvements
            * **Notification** - We will provide advance notice for scheduled maintenance whenever possible
            * **Emergency Maintenance** - May be performed without notice to address critical issues
            * **External Factors** - Service availability may be impacted by factors beyond our control

            RK Coders reserves the right to modify, suspend, or discontinue any aspect of the software with or without notice.
            """,
        },
        {
            "title": "Subscription & Payment Terms",
            "icon": "💰",
            "content": """
            Continued access to the Teacher Attendance System requires an active subscription.

            * **Payment Terms** - Subscription fees are due in advance on a monthly/annual basis
            * **Late Payment** - Failure to pay on time may result in account suspension or termination
            * **No Refunds** - All payments are non-refundable, including in cases of early termination
            * **Price Changes** - RK Coders reserves the right to modify pricing with 30 days prior notice

            You are responsible for all taxes and fees associated with your subscription unless explicitly stated otherwise.
            """,
        },
        {
            "title": "Liability Disclaimer",
            "icon": "⚠️",
            "content": """
            To the maximum extent permitted by applicable law:

            * The software is provided "as is" without warranties of any kind, either express or implied
            * RK Coders disclaims all warranties including but not limited to merchantability, fitness for a particular purpose, and non-infringement
            * RK Coders is not responsible for any direct, indirect, incidental, special, consequential, or exemplary damages
            * Users are solely responsible for ensuring data accuracy and compliance with educational regulations

            In no event shall RK Coders' total liability exceed the amount paid by you for the software in the 12 months preceding any claim.
            """,
        },
        {
            "title": "Termination of Access",
            "icon": "🚫",
            "content": """
            RK Coders reserves the right to suspend or terminate your access to the software if:

            * You breach any provision of these Terms & Conditions
            * You fail to make timely payment of subscription fees
            * You engage in fraudulent, illegal, or unauthorized activities
            * You misuse system resources or attempt to gain unauthorized access

            Upon termination, you must cease all use of the software and destroy all copies in your possession.
            """,
        },
        {
            "title": "Updates & Modifications",
            "icon": "🔄",
            "content": """
            RK Coders may release updates, bug fixes, or feature improvements at any time.

            * **Automatic Updates** - Software may automatically download and install updates
            * **Version Support** - Only the latest version of the software is fully supported
            * **Terms Updates** - These Terms & Conditions may be updated periodically
            * **Notification** - We will make reasonable efforts to notify you of significant changes

            Continued use of the software after an update implies acceptance of any new terms.
            """,
        },
        {
            "title": "Governing Law & Jurisdiction",
            "icon": "⚖️",
            "content": """
            These Terms & Conditions shall be governed by the laws of India, without regard to its conflict of law principles.

            * Any legal disputes arising from the use of this software will be resolved exclusively in the courts of Sadabad (Hathras), Uttar Pradesh, India
            * You consent to the personal jurisdiction of such courts
            * If any provision of these terms is found to be unenforceable, the remaining provisions will remain in full force and effect

            These Terms & Conditions constitute the entire agreement between you and RK Coders regarding your use of the software.
            """,
        },
        {
            "title": "Acceptance of Terms",
            "icon": "✅",
            "content": """
            By using this software, you acknowledge that:

            * You have read and understood these Terms & Conditions
            * You agree to be bound by these terms in their entirety
            * You have the authority to accept these terms on behalf of your organization
            * If you do not agree with any of these terms, you must discontinue use of the software immediately

            Your continued use of the Teacher Attendance System constitutes your ongoing acceptance of these terms.
            """,
        },
    ]

    # Render each section with professional styling
    for i, section in enumerate(sections):
        # Create a section with header
        st.subheader(f"{i+1}. {section['icon']} {section['title']}")

        # Section content
        st.markdown(section["content"])
        st.divider()

    # Additional protection measures
    st.subheader("🛡️ Additional Protection Measures")
    st.write(
        "In addition to these Terms & Conditions, RK Coders implements the following measures to protect our intellectual property:"
    )

    protection_measures = [
        "**End-User License Agreement (EULA)** - A comprehensive agreement that specifically defines the permitted uses and restrictions of our software.",
        "**Copyright Registration** - Our software is officially registered with the Indian Copyright Office to ensure maximum legal protection.",
        "**License Key System** - Sophisticated authentication mechanisms ensure only authorized users can access our software.",
        "**Code Obfuscation & Encryption** - Advanced techniques to prevent unauthorized access to source code and protect our intellectual property.",
        "**Data Encryption** - Industry-standard encryption to protect all sensitive school and user data.",
    ]

    for measure in protection_measures:
        st.success(measure)

    # Document footer with last updated date and copyright notice
    current_year = datetime.datetime.now().year

    st.divider()
    st.caption(f"This document was last updated on April 01, {current_year}")
    st.caption(f"© {current_year} RK Coders. All Rights Reserved.")
    st.caption(
        "Teacher Attendance System by Rishi Agrawal, son of Late Devendra Agrawal"
    )


def render_contact_page(school_id, data_manager):
    """Render the Contact page with social media icons and modern design"""
    st.markdown(
        """
<style>
    /* Base Styles and Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #4F46E5, #7C3AED);
        --secondary-gradient: linear-gradient(135deg, #3B82F6, #2563EB);
        --accent-gradient: linear-gradient(135deg, #F59E0B, #D97706);
        --success-gradient: linear-gradient(135deg, #10B981, #059669);
        --error-gradient: linear-gradient(135deg, #EF4444, #DC2626);
        --primary-color: #4F46E5;
        --text-primary: #1E293B;
        --text-secondary: #475569;
        --text-light: #94A3B8;
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        --card-hover-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    .ultra-contact-container {
        font-family: 'Montserrat', sans-serif;
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Advanced Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes zoomIn {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2); }
        50% { transform: scale(1.05); box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3); }
        100% { transform: scale(1); box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2); }
    }
    
    @keyframes glowing {
        0% { box-shadow: 0 0 5px rgba(79, 70, 229, 0.5); }
        50% { box-shadow: 0 0 20px rgba(79, 70, 229, 0.8); }
        100% { box-shadow: 0 0 5px rgba(79, 70, 229, 0.5); }
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Ultra-premium Hero Section */
    .contact-hero {
        position: relative;
        padding: 120px 0 140px;
        text-align: center;
        overflow: hidden;
        border-radius: 0 0 30px 30px;
        background: var(--primary-gradient);
        margin-bottom: 80px;
    }
    
    .contact-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url('https://cdn.pixabay.com/photo/2018/03/24/08/56/background-3257024_1280.jpg');
        background-size: cover;
        background-position: center;
        mix-blend-mode: overlay;
        opacity: 0.1;
    }
    
    .hero-shapes {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: 0;
    }
    
    .hero-shape {
        position: absolute;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
    }
    
    .hero-shape-1 {
        width: 150px;
        height: 150px;
        top: 20%;
        left: 10%;
        animation: float 8s ease-in-out infinite;
    }
    
    .hero-shape-2 {
        width: 80px;
        height: 80px;
        bottom: 20%;
        right: 10%;
        animation: float 6s ease-in-out infinite;
        animation-delay: 1s;
    }
    
    .hero-shape-3 {
        width: 120px;
        height: 120px;
        top: 60%;
        left: 20%;
        animation: float 7s ease-in-out infinite;
        animation-delay: 2s;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        margin-bottom: 20px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        letter-spacing: -0.5px;
        animation: zoomIn 1s ease-out forwards;
    }
    
    .hero-title span {
        background: linear-gradient(to right, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        display: inline-block;
    }
    
    .hero-title span::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: 5px;
        width: 100%;
        height: 4px;
        background: linear-gradient(to right, #FFD700, #FFA500);
        border-radius: 2px;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 40px;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
        animation: fadeIn 1s ease-out forwards;
        animation-delay: 0.3s;
        opacity: 0;
    }
    
    .hero-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 40px;
        animation: fadeIn 1s ease-out forwards;
        animation-delay: 0.6s;
        opacity: 0;
    }
    
    .hero-button {
        padding: 16px 32px;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        text-decoration: none;
    }
    
    .hero-button-primary {
        background: white;
        color: var(--primary-color);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .hero-button-primary:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    .hero-button-secondary {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .hero-button-secondary:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-5px);
    }
    
    .hero-wave {
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 100%;
        height: 80px;
    }
    """,
        unsafe_allow_html=True,
    )
    # Page Title with decorative elements
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 10px;">
        <h1 style="color: #1E3A8A; font-size: 2.8rem; font-weight: 700;">Contact Us</h1>
        <div style="width: 80px; height: 4px; background: linear-gradient(90deg, #3B82F6, #1E40AF); margin: 5px auto 30px;"></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Hero section with gradient background
    st.markdown(
        """
<div class="ultra-contact-container">
    <div class="contact-hero">
        <div class="hero-shapes">
            <div class="hero-shape hero-shape-1"></div>
            <div class="hero-shape hero-shape-2"></div>
            <div class="hero-shape hero-shape-3"></div>
        </div>
        <div class="hero-content">
            <h1 class="hero-title">Get in Touch <span>With Us</span></h1>
            <p style="margin-left:110px;"class="hero-subtitle">
                We're here to help! Reach out for support, inquiries, or to explore how our 
                Teacher Attendance System can transform your school's operations.
            </p>
            <div class="hero-buttons">
                <a href="#contact-form" class="hero-button hero-button-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                        <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                    </svg>
                    Send Message
                </a>
                <a href="#social-connect" class="hero-button hero-button-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1h-3zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5zm1.886 6.914L15 7.151V12.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V7.15l6.614 1.764a1.5 1.5 0 0 0 .772 0zM1.5 4h13a.5.5 0 0 1 .5.5v1.616L8.129 7.948a.5.5 0 0 1-.258 0L1 6.116V4.5a.5.5 0 0 1 .5-.5z"/>
                    </svg>
                    Connect with Us
                </a>
            </div>
        </div>
        <div class="hero-wave">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 100" fill="#ffffff">
                <path d="M0,96L48,85.3C96,75,192,53,288,42.7C384,32,480,32,576,42.7C672,53,768,75,864,74.7C960,75,1056,53,1152,48C1248,43,1344,53,1392,58.7L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
            </svg>
        </div>
    </div>
""",
        unsafe_allow_html=True,
    )

    # Main content in two columns for better layout

    # Developer Information Section with cards
    st.markdown(
        """
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
        <h1 style="color: #1E3A8A; font-size: 1.8rem; text-align: center;">
            👨‍💻 Contact Information
        </h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Modern contact cards with icons
    contact_info = [
        {
            "icon": "https://cdn-icons-png.flaticon.com/512/1077/1077114.png",
            "title": "Name",
            "value": "Rishi Agrawal",
            "color": "#4F46E5",
        },
        {
            "icon": "https://cdn-icons-png.flaticon.com/512/455/455705.png",
            "title": "Phone",
            "value": "+91 9520496351",
            "color": "#2563EB",
        },
        {
            "icon": "https://cdn-icons-png.flaticon.com/512/732/732200.png",
            "title": "Email",
            "value": "rishiagrawal45202@gmail.com",
            "color": "#DB2777",
        },
        {
            "icon": "https://cdn-icons-png.flaticon.com/512/220/220236.png",
            "title": "WhatsApp",
            "value": "+91 8954730444",
            "color": "#10B981",
        },
        {
            "icon": "https://cdn-icons-png.flaticon.com/512/927/927667.png",
            "title": "Address",
            "value": "Jawahar Bajar, Sadabad (Hathras), Uttar Pradesh, India - 281306",
            "color": "#F59E0B",
        },
    ]

    # Create 2 columns for contact cards
    cont_col1, cont_col2 = st.columns(2)

    for i, info in enumerate(contact_info):
        # Address card in full width
        if i == 4:  # Address
            st.markdown(
                f"""
                <div style="background: white; padding: 20px; border-radius: 10px; 
                          margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                          border-left: 4px solid {info['color']};">
                    <div style="display: flex; align-items: center;">
                        <img src="{info['icon']}" width="32" style="margin-right: 15px;">
                        <div>
                            <div style="font-size: 14px; color: #64748B;">{info['title']}</div>
                            <div style="font-weight: 600; color: #1E293B; font-size: 16px;">{info['value']}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            with cont_col1 if i % 2 == 0 else cont_col2:
                st.markdown(
                    f"""
                    <div style="background: white; padding: 20px; border-radius: 10px; 
                              margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                              border-left: 4px solid {info['color']};">
                        <div style="display: flex; align-items: center;">
                            <img src="{info['icon']}" width="32" style="margin-right: 15px;">
                            <div>
                                <div style="font-size: 14px; color: #64748B;">{info['title']}</div>
                                <div style="font-weight: 600; color: #1E293B; font-size: 16px;">{info['value']}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Business Hours with elegant design
    business_hours_html = """
    <div style="
        background: white; 
        padding: 25px; 
        border-radius: 10px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #3B82F6;
    ">
        <h3 style="
            color: #1E3A8A; 
            margin-top: 0; 
            display: flex; 
            align-items: center; 
            margin-bottom: 20px;
        ">
            <span style="font-size: 1.5rem; margin-right: 10px;">⏰</span> 
            Business Hours
        </h3>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed #E2E8F0;">
            <div style="font-weight: 500; color: #475569;">Monday - Friday</div>
            <div style="color: #1E293B; font-weight: 600;">9:00 AM - 6:00 PM</div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed #E2E8F0;">
            <div style="font-weight: 500; color: #475569;">Saturday</div>
            <div style="color: #1E293B; font-weight: 600;">10:00 AM - 4:00 PM</div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed #E2E8F0;">
            <div style="font-weight: 500; color: #475569;">Sunday</div>
            <div style="color: #1E293B; font-weight: 600;">Closed</div>
        </div>

        <div style="display: flex; justify-content: space-between;">
            <div style="font-weight: 500; color: #475569;">Response Time</div>
            <div style="color: #10B981; font-weight: 600;">Within 24 hours</div>
        </div>
    </div>
"""

    components.html(business_hours_html, height=300)

    qc_col1, qc_col2 = st.columns(2)

    with qc_col1:
        st.markdown(
            """
            <a href="mailto:rishiagrawal45202@gmail.com" style="text-decoration: none;">
                <div style="background: linear-gradient(135deg, #3B82F6, #1E40AF); 
                          color: white; padding: 15px; margin-top:-30px;
                           margin-left:8px; border-radius: 10px; text-align: center; 
                          font-weight: 600; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);
                          transition: transform 0.3s;">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <img src="https://cdn-icons-png.flaticon.com/512/732/732200.png" width="20" 
                             style="filter: brightness(0) invert(1); margin-right: 10px;">
                        Email Us
                    </div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    with qc_col2:
        st.markdown(
            """
            <a href="tel:+919520496351" style="text-decoration: none;">
                <div style="background: linear-gradient(135deg, #10B981, #047857); 
                          color: white;margin-right:8px; padding: 15px; margin-top:-30px;border-radius: 10px; text-align: center; 
                          font-weight: 600; box-shadow: 0 4px 6px rgba(5, 150, 105, 0.3);
                          transition: transform 0.3s;">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <img src="https://cdn-icons-png.flaticon.com/512/455/455705.png" width="20" 
                             style="filter: brightness(0) invert(1); margin-right: 10px;">
                        Call Us
                    </div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    # Social Media Section with elegant card layout
    st.markdown(
        """
    <div style="text-align: center; margin: 50px 0 30px;">
        <h2 style="color: #1E3A8A;font-size: 1.8rem; font-weight: 700; margin-bottom: 5px;">Connect With Us</h2>
        <p style="color: #475569; margin-bottom: 30px; font-size: 1.1rem;">
            Follow us on social media to stay updated with our latest news and updates
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    social_media = [
        {
            "name": "LinkedIn",
            "icon": "https://cdn-icons-png.flaticon.com/512/3536/3536505.png",
            "url": "https://www.linkedin.com/in/rishi-agrawal-994a42253",
            "color": "#0A66C2",
            "bg": "#E7F0FF",
        },
        {
            "name": "Instagram",
            "icon": "https://cdn-icons-png.flaticon.com/512/3955/3955024.png",
            "url": "https://www.instagram.com/rishiagrawal45202/",
            "color": "#E4405F",
            "bg": "#FFEBEE",
        },
        {
            "name": "Telegram",
            "icon": "https://cdn-icons-png.flaticon.com/512/5968/5968804.png",
            "url": "https://t.me/Rishi_agrawal",
            "color": "#0088CC",
            "bg": "#E3F2FD",
        },
        {
            "name": "YouTube",
            "icon": "https://cdn-icons-png.flaticon.com/512/3670/3670147.png",
            "url": "https://youtube.com/@softcode21?si=jll8Hxsu-dvkN74T",
            "color": "#FF0000",
            "bg": "#FFEBEE",
        },
        {
            "name": "WhatsApp",
            "icon": "https://cdn-icons-png.flaticon.com/512/3670/3670051.png",
            "url": "https://wa.me/8954730444",
            "color": "#25D366",
            "bg": "#E8F5E9",
        },
    ]

    # Display social media in a single st.markdown

    social_cards_html = """
<div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-bottom: 40px;">
"""

    for social in social_media:
        social_cards_html += f"""
    <a href="{social['url']}" target="_blank" style="text-decoration: none;">
        <div style="width: 120px; background: white; padding: 25px 15px; border-radius: 10px; 
                  display: flex; flex-direction: column; align-items: center; justify-content: center; 
                  box-shadow: 0 8px 20px rgba(0,0,0,0.05); transition: all 0.3s ease;
                  border-bottom: 4px solid {social['color']};">
            <div style="width: 60px; height: 60px; border-radius: 50%; background: {social['bg']}; 
                      display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                <img src="{social['icon']}" width="36">
            </div>
            <div style="font-weight: 600; color: {social['color']}; font-size: 16px;">{social['name']}</div>
        </div>
    </a>
    """

    social_cards_html += "</div>"
    components.html(social_cards_html, height=300)
    # ✅ FIX: Adding unsafe_allow_html=True to properly render HTML
    # Map and location
    st.markdown(
        """
    <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-top:-60px ;">
        <h2 style="color: #1E3A8A; font-size: 1.5rem; display: flex; align-items: center; margin-bottom: 20px;">
            <span style="font-size: 1.8rem; margin-right: 10px;">📍</span> Our Location
        </h2>
        <div style="border-radius: 10px; overflow: hidden; margin-bottom: 20px;">
            <iframe width="100%" height="400" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d14057.058795243926!2d78.3839!3d27.39!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x397474e94fffffa1%3A0xd2855f8ebb006bf5!2sSadabad%2C%20Uttar%20Pradesh!5e0!3m2!1sen!2sin!4v1743499257162!5m2!1sen!2sin" 
                    style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
        <p style="color: #475569; font-size: 1rem; margin-bottom: 0;">
            Visit us at our office in Sadabad to discuss your needs in person. We're open during business hours and look forward to meeting you!
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # FAQ Section
    st.markdown(
        """
    <div style="margin: 50px 0;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #1E3A8A; font-size: 1.8rem; font-weight: 700; margin-bottom: 5px;">Frequently Asked Questions</h2>
            <p style="color: #475569; margin-bottom: 0; font-size: 1.1rem;">
                Find quick answers to common questions about our services
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Create expandable FAQs with Streamlit
    with st.expander(
        "How can I get technical support for the Teacher Attendance System?"
    ):
        st.write(
            """
        You can reach our technical support team through multiple channels:
        * Email us at rishiagrawal45202@gmail.com
        * Call our support line at +91 9520496351
        * Connect on WhatsApp at +91 8954730444
        
        Our team aims to respond to all inquiries within 24 hours during business days.
        """
        )

    with st.expander(
        "Do you offer customization services for the Teacher Attendance System?"
    ):
        st.write(
            """
        Yes, we offer customization services to meet the specific needs of your school or educational institution. 
        Our team can add custom features, integrate with your existing systems, or modify the interface to match your requirements.
        
        Contact us with your specific needs for a customized solution and pricing quote.
        """
        )

    with st.expander("What training and support options are available for new users?"):
        st.write(
            """
        We provide comprehensive training and support for all new users:
        * Initial setup and configuration assistance
        * User training sessions (remote or on-site)
        * Detailed documentation and user manuals
        * Video tutorials for key features
        * Ongoing technical support
        
        Our goal is to ensure a smooth transition and successful implementation of the system.
        """
        )

    with st.expander("How secure is the data in the Teacher Attendance System?"):
        st.write(
            """
        Data security is our top priority:
        * All data is encrypted both in transit and at rest
        * Regular security audits and updates
        * Role-based access controls
        * Secure authentication mechanisms
        * Regular automated backups
        
        We comply with industry best practices to ensure your school's data remains secure and confidential.
        """
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Contact form - teaser (since we can't actually process it)
    st.markdown(
        """
    <div style="background: linear-gradient(135deg, #1E3A8A, #3B82F6); 
               padding: 40px; border-radius: 15px; color: white; 
               box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3); margin: 50px 0 30px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: white; font-size: 1.8rem; font-weight: 700; margin-bottom: 5px;">Send Us a Message</h2>
            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0; font-size: 1.1rem;">
                Have a question or need assistance? Fill out the form below and we'll get back to you shortly.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Simple form elements
    form_col1, form_col2 = st.columns(2)

    with form_col1:
        st.text_input("Your Name", placeholder="Enter your full name")

    with form_col2:
        st.text_input("Your Email", placeholder="Enter your email address")

    form_col3, form_col4 = st.columns(2)

    with form_col3:
        st.text_input("Phone Number", placeholder="Enter your phone number")

    with form_col4:
        st.selectbox(
            "Subject",
            [
                "Technical Support",
                "Sales Inquiry",
                "Customization Request",
                "Training",
                "Other",
            ],
        )

    st.text_area("Message", placeholder="Type your message here...", height=150)

    st.button(" Send Message", type="secondary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Copyright Footer with more modern design
    current_year = datetime.datetime.now().year

    st.markdown(
        f"""
    <div style="text-align: center; margin-top: 70px; padding-top: 30px; border-top: 1px solid #E2E8F0;">
        <div style="margin-bottom: 15px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2521/2521826.png" width="24" style="vertical-align: middle; margin-right: 8px;">
            <span style="color: #1E293B; font-weight: 600; font-size: 16px;">© {current_year} RK Coders. All Rights Reserved.</span>
        </div>
        <p style="color: #64748B; margin: 5px 0 0 0; font-size: 14px;">
            Teacher Attendance System by Rishi Agrawal, son of Late Devendra Agrawal
        </p>
        <p style="color: #94A3B8; margin: 20px 0 0 0; font-size: 12px;">
            Designed with ❤️ in Sadabad, Uttar Pradesh, India
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
# test line to trigger git