# Njala University Fees Management System 🎓

A modern, full-stack fee management platform for Njala University students, built with Flask (Python) backend and vanilla HTML/CSS/JavaScript frontend.

## 🌟 Features

### Student Portal
- **Dashboard** - Real-time fee balance, payment progress, and transaction summary
- **Fee Management** - View detailed fee breakdown by category and semester
- **Payment Processing** - Initiate payments via Orange Money, Africell Money, or Bank Transfer
- **Payment History** - Complete transaction history with receipts
- **Profile Management** - Update personal information and account settings
- **Mobile-Responsive** - Works seamlessly on desktop and mobile devices

### Admin Dashboard
- **Financial Overview** - Real-time collection metrics and payment analytics
- **Student Management** - Search and manage student accounts
- **Payment Tracking** - Monitor all transactions and reconciliation
- **Fee Configuration** - Manage fee structures and amounts
- **Reporting** - Generate comprehensive financial reports
- **Bulk Operations** - Send payment reminders via SMS

### Technical Features
- **JWT Authentication** - Secure token-based authentication
- **Responsive Design** - Mobile-first approach with bottle green theme
- **Real-time Updates** - Live payment status verification
- **SMS Notifications** - Integration with Twilio for payment alerts
- **Email Receipts** - Automated receipt generation and delivery
- **Database Auditing** - Complete activity tracking and logging
- **API-Driven** - RESTful API for all operations

## 📋 Tech Stack

### Backend
- **Framework:** Flask 3.0
- **Database:** PostgreSQL 12+
- **Authentication:** Flask-JWT-Extended
- **API:** RESTful with CORS support
- **SMS:** Twilio Integration
- **Email:** Flask-Mail with SMTP

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom design system with CSS variables
- **JavaScript (Vanilla)** - No frameworks for maximum performance
- **Responsive** - Mobile-first design

### Infrastructure
- **Server:** Gunicorn / Flask development server
- **Database:** PostgreSQL
- **Environment:** Docker-ready

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- Git

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/njala/fees-system.git
cd njala-fees-system
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Setup Database**
```bash
# Create PostgreSQL database
createdb njala_fees

# Load schema
psql njala_fees < database/schema.sql

# Load seed data (optional)
psql njala_fees < database/seed.sql
```

5. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Run Application**
```bash
# Backend
python backend/app.py

# Frontend - Open in browser
open frontend/index.html
```

### Default Demo Credentials
```
Student ID: NJU/2021/0042
Password: password123

Admin Username: finance_officer
Password: password123
```

## 📁 Project Structure

```
njala-fees-system/
├── frontend/
│   ├── index.html              # Landing page
│   ├── login.html              # Authentication
│   ├── dashboard.html          # Student dashboard
│   ├── admin.html              # Admin panel
│   ├── css/
│   │   └── styles.css          # Main stylesheet (bottle green theme)
│   └── js/
│       ├── auth.js             # Authentication logic
│       ├── dashboard.js        # Dashboard functionality
│       └── payments.js         # Payment processing
│
├── backend/
│   ├── app.py                  # Flask application entry point
│   ├── config.py               # Configuration settings
│   │
│   ├── models/
│   │   ├── user.py             # User and Admin models
│   │   └── payment.py          # Fee and Payment models
│   │
│   ├── routes/
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── fees_routes.py      # Fee management endpoints
│   │   ├── payment_routes.py   # Payment processing endpoints
│   │   └── admin_routes.py     # Admin management endpoints
│   │
│   ├── utils/
│   │   ├── db.py               # Database utilities
│   │   ├── sms.py              # SMS (Twilio) integration
│   │   ├── email.py            # Email notification service
│   │   └── mobile_money.py     # Payment gateway integration
│   │
│   └── requirements.txt        # Python dependencies
│
├── database/
│   ├── schema.sql              # PostgreSQL schema
│   └── seed.sql                # Demo data
│
├── .env                        # Environment variables
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - Student login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/verify-token` - Verify JWT token
- `POST /api/auth/refresh-token` - Refresh access token

### Fees
- `GET /api/fees/balance` - Get fee balance
- `GET /api/fees/list` - List all fees
- `GET /api/fees/breakdown` - Fee breakdown by category
- `GET /api/fees/payment-schedule` - Upcoming payments
- `GET /api/fees/summary` - Complete summary

### Payments
- `POST /api/payments/initiate` - Initiate payment
- `GET /api/payments/verify/<transaction_id>` - Verify payment
- `GET /api/payments/history` - Payment history
- `GET /api/payments/receipt/<transaction_id>` - Download receipt
- `POST /api/payments/send-reminder` - Send payment reminder

### Admin
- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/students` - List students
- `GET /api/admin/payments` - List all payments
- `GET /api/admin/reports/collection` - Collection report
- `GET /api/admin/reports/outstanding` - Outstanding fees report
- `POST /api/admin/send-reminder` - Bulk SMS reminder

## 🎨 Design System

The system uses a custom bottle green color scheme representing Njala University:

```css
--green-900: #0a2412
--green-800: #0f3319
--green-700: #1a4d27
--green-600: #1e5c2e   /* Primary bottle green */
--gold: #c9a84c        /* Accent color */
```

## 🔐 Security Features

- **Password Hashing** - PBKDF2-SHA256 encryption
- **JWT Tokens** - Secure stateless authentication
- **CORS Protection** - Cross-origin request validation
- **SQL Injection Prevention** - Parameterized queries
- **HTTPS Ready** - Secure cookie configuration
- **Session Management** - Automatic token expiration
- **Rate Limiting** - Ready for implementation
- **Audit Logging** - Complete activity tracking

## 📱 Mobile Money Integration

### Supported Providers
- **Orange Money** - USSD: *114*1#
- **Africell Money** - USSD: *185#
- **Bank Transfer** - Sierra Leone Commercial Bank

### Payment Flow
1. Student selects amount and payment method
2. System generates reference number
3. Student initiates payment on their phone
4. System receives callback confirmation
5. Automatic receipt and SMS sent

## 📧 Notification System

### SMS Notifications
- Payment confirmation
- Fee payment reminders
- Payment failure alerts
- Exam clearance notices

### Email Notifications
- Registration confirmation
- Payment receipts
- Fee reminders
- Password reset links

## 📊 Reporting & Analytics

### Available Reports
- Fee collection by faculty
- Payment trends (monthly/yearly)
- Outstanding balances
- Student payment statistics
- Transaction reconciliation

### Export Formats
- PDF reports
- CSV data export
- Excel spreadsheets

## 🔧 Configuration

### Environment Variables
See `.env` file for all configuration options:
- Database connection
- JWT secret
- Twilio credentials
- Email SMTP settings
- Orange Money / Africell API keys

### Database Configuration
PostgreSQL connection can be customized in config.py or via DATABASE_URL

## 🚀 Deployment

### Production Setup

1. **Install Production Server**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend/app:create_app()
```

3. **Environment**
- Set `FLASK_ENV=production`
- Update JWT_SECRET_KEY
- Enable HTTPS/SSL certificates
- Set secure CORS origins
- Update database credentials

4. **Docker (Optional)**
```bash
docker build -t njala-fees .
docker run -p 5000:5000 --env-file .env njala-fees
```

## 📝 Development

### Code Standards
- PEP 8 for Python
- Vanilla JS with comments
- CSS with component organization

### Testing
```bash
pytest tests/
```

### Logging
- Application logs: `logs/app.log`
- Database queries logged in development
- Request/response logging for debugging

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

**SMS Not Sending**
- Verify Twilio credentials
- Check phone number format
- Review Twilio account balance

**Payment Gateway Error**
- Confirm API keys are correct
- Check payment provider status
- Verify phone number format

**CORS Error**
- Add origin to CORS_ORIGINS in config
- Verify frontend URL matches config
- Check Access-Control headers

## 📚 Documentation

- **API Docs** - See routes files for endpoint documentation
- **Database Schema** - See database/schema.sql for table structure
- **Frontend Code** - Inline comments in js/ and css/ files

## 🤝 Contributing

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Authors

- **Development Team** - Njala University ICT Department
- **Design** - Custom bottle green theme

## 📞 Support

For issues or questions:
- Email: ict@njala.edu.sl
- Phone: +232 22 000 000
- Portal: https://njala-fees.edu.sl

## 🙏 Acknowledgments

Built specifically for Njala University's unique requirements with emphasis on:
- Simplicity for students
- Comprehensive for admins
- Mobile money integration
- Sierra Leone context

---

**Version:** 1.0.0  
**Last Updated:** 2026  
**Status:** Production Ready
#   N j a l a - U n i v e r s i t y - F e e s - R e g i s t r a t i o n - s y s t e m -  
 