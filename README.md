# Clothing Rental Platform

A full-stack web application built with Django that allows users to rent clothes online. The platform features a robust authentication system, shopping cart functionality, secure payment processing with Stripe, and an automated notification system.

## Features

### User Management
- Custom user authentication system
- Email verification for new accounts
- Password reset functionality
- User profile management
- Secure password change mechanism

### Shopping Experience
- Browse available clothing items
- Advanced filtering and search capabilities
- Category-based navigation
- Detailed product views
- Related items suggestions
- Real-time stock tracking

### Cart System
- Add/remove items
- Adjust rental duration
- Real-time price calculations
- Multiple items checkout

### Rental Management
- Active rentals tracking
- Rental extension capability
- Return date monitoring
- Rental history

### Payment Processing
- Secure payment handling with Stripe
- Support for multiple payment methods
- Cart checkout process
- Extension payment handling
- Payment status tracking

### Notification System
- Automated return reminders
- Email notifications
- Custom email templates
- Error handling and logging

## Technology Stack

### Backend
- Django
- Python
- PostgreSQL (recommended)

### Frontend
- HTML5
- CSS3
- JavaScript
- Tailwind CSS
- Custom CSS components

### Payment Processing
- Stripe API

### Email Services
- SMTP email backend
- HTML email templates

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [project-directory]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file in the root directory
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
EMAIL_HOST=your_email_host
EMAIL_PORT=your_email_port
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
project/
├── user/                  # User authentication app
├── shop/                  # Main shopping functionality
├── payment/              # Payment processing
├── notification/         # Email notification system
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
└── requirements.txt      # Project dependencies
```

## Configuration

### Stripe Setup
1. Create a Stripe account
2. Get your API keys from the Stripe dashboard
3. Add keys to your environment variables

### Email Configuration
1. Configure your email backend settings in settings.py
2. Set up email templates in the templates directory
3. Test email functionality

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for complex functions

## Deployment

### Prerequisites
- PostgreSQL database
- Web server (e.g., Nginx)
- WSGI server (e.g., Gunicorn)
- SSL certificate

### Steps
1. Set DEBUG=False in production
2. Configure your web server
3. Set up SSL certificate
4. Configure WSGI server
5. Set up database
6. Collect static files:
```bash
python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security Considerations

- Always use HTTPS in production
- Keep API keys secure
- Regularly update dependencies
- Implement rate limiting
- Use secure password hashing
- Implement CSRF protection

## License

MIT License

## Support

For support, please email [naolmitiku@gmail.com]

## Acknowledgments

- Django documentation
- Stripe API documentation
- Tailwind CSS documentation