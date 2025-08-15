# School Management System Migration Project

## Overview

Successfully migrated existing School Management System from Streamlit to Django (Backend) + React (Frontend). The system manages automatic teacher arrangements, absence tracking, and replacements with a professional, mobile-friendly design.

**MIGRATION STATUS: COMPLETED ✓**
- Django backend with 5 apps (authentication, teachers, arrangements, attendance, schedules)
- React frontend with Ant Design components and professional UI
- Railway MySQL database connection established
- All existing Python business logic preserved in backend/existing_modules/
- Professional login page with school selection dropdown
- Multi-school support implemented with school_id based access control

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React with component-based architecture
- **UI Framework**: Ant Design with professional components and theming
- **UI Components**: Modern components including dashboard, teacher management, arrangements, attendance, and reports
- **Styling**: Professional CSS with Poppins font family, responsive mobile-friendly design with gradients
- **State Management**: React hooks and localStorage for user authentication and data persistence
- **Routing**: React Router for navigation between pages
- **API Integration**: Axios for Django backend communication

### Backend Architecture
- **Framework**: Django with Django REST Framework
- **Apps Structure**: 5 Django apps (authentication, teachers, arrangements, attendance, schedules)
- **Core Logic**: ALL existing Python business logic preserved in `backend/existing_modules/`
- **Data Manager**: Original `data_manager.py` preserved for database operations
- **Authentication**: Django REST API with preserved bcrypt authentication logic
- **Arrangement Logic**: Original `arrangement_logic.py` preserved for teacher replacement algorithms
- **Auto Marking**: Original `auto_marker.py` preserved for automated attendance
- **API Endpoints**: RESTful APIs for all frontend interactions

### Data Storage
- **Database**: MySQL database with Railway hosting
- **Connection**: Environment variable-based configuration with connection pooling
- **Schema**: Comprehensive schema including schools, admins, users, arrangements, attendance, schedules, and coverage tracking tables
- **Data Import**: CSV import functionality for bulk data operations

### Authentication & Authorization
- **User Management**: Multi-role system (admin, teachers) with school-based isolation
- **Security**: Password hashing with bcrypt, API key authentication for external integrations
- **Domain Validation**: Domain-based access control ensuring users can only access from authorized domains
- **Session Management**: Streamlit session-based user state management

### Business Logic Components
- **Arrangement Engine**: Advanced algorithm for teacher replacement with subject expertise matching and workload distribution
- **Attendance System**: Biometric integration with bulk processing capabilities
- **Scheduling**: Daily and weekly schedule management with period-based organization
- **Reporting**: Comprehensive analytics and reporting with date range filtering

## External Dependencies

### Third-Party Services
- **MSG91**: WhatsApp messaging service for notifications and communication
- **Tawk.to**: Customer support chat widget integration

### Database & Hosting
- **Railway**: Cloud hosting platform with MySQL database
- **MySQL Connector**: Database connectivity with connection pooling and error handling

### Python Libraries
- **Streamlit**: Web application framework for UI components
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualization and charts
- **PyTZ**: Timezone handling for IST (Asia/Kolkata)
- **BCrypt**: Password hashing and security
- **Flask**: API server for external integrations
- **Schedule**: Task scheduling for automated operations

### Frontend Dependencies
- **Google Fonts**: Poppins font family for consistent typography
- **Streamlit Lottie**: Animation components for enhanced UI
- **Custom CSS**: Professional styling with gradients and responsive design

### Development Tools
- **dotenv**: Environment variable management for development
- **Certifi**: SSL certificate verification
- **Watchdog**: File system monitoring for development