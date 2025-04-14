# 🧼 DryCleaning - Django-based Dry Cleaning Management System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive role-based management system for dry cleaning businesses. This application supports multiple user roles (clients, operators, managers, accountants, and technologists) with separate access levels and functionality. The system includes order tracking, service catalog management, branch management, dynamic pricing with discounts and surcharges, and financial reporting.

## 🚀 Features

- **Role-based Access Control**:
  - 👨‍💼 **Managers**: Full access to system, staff management, reports, services, and branch management
  - 👩‍💻 **Operators**: Order intake, client management, status updates
  - 💰 **Accountants**: Financial reports, order tracking, revenue analysis
  - 🧪 **Technologists**: Order processing workflow, quality control, technical notes
  - 👤 **Clients**: Order submission, status tracking, account management

- **Order Management**:
  - Order creation with service type selection
  - Complexity and urgency level options affecting pricing
  - Order status tracking through the entire workflow
  - Technical notes and recommendations from technologists
  - Order history and detailed view

- **Dynamic Pricing System**:
  - Base price for each service type
  - Surcharges for complexity (10-20%) and urgency (15-30%)
  - Automatic 3% loyalty discount after 3 orders
  - Flexible price calculation based on service parameters

- **Branch Management**:
  - Support for multiple business locations
  - Branch-specific order tracking
  - Location details and contact information

- **Service Catalog**:
  - Categorized service types (Химчистка, Стирка, Глажка, etc.)
  - Customizable base prices and multipliers
  - Service status management

- **Reporting**:
  - Daily, monthly, and yearly financial reports
  - Branch performance analysis
  - Service popularity and revenue metrics

- **User Interface**:
  - Clean, responsive Bootstrap-based design
  - Role-appropriate dashboards and navigation
  - Mobile-friendly layout

## 📋 Prerequisites

- Python 3.12+
- Django 5.2+
- Other dependencies listed in `requirements.txt`

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dry_cleaning.git
   cd dry_cleaning
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Make and apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Generate test data (optional):
   ```bash
   python manage.py generate_test_data
   ```

7. Run the development server:
   ```bash
   python manage.py runserver 8000
   ```

8. Access the application at http://127.0.0.1:8000/

## 🗂️ Project Structure

```
dry_cleaning/
├── accounts/            # User authentication, roles, and permissions
├── branches/            # Branch management
├── clients/             # Client profiles and management
├── orders/              # Order processing and workflow
│   └── management/
│       └── commands/    # Custom management commands including generate_test_data.py
├── services/            # Service types and pricing
├── templates/           # HTML templates
│   ├── accounts/
│   ├── branches/
│   ├── clients/
│   └── orders/
└── dry_cleaning/        # Main project settings
```

## 🧪 Testing

Run the test suite with:

```bash
python manage.py test
```

## 🔄 Workflow

1. **Client Registration/Login**:
   - Clients register accounts or log in
   - Client profiles are automatically created

2. **Order Submission**:
   - Clients or operators create orders
   - Service type, urgency, and complexity are selected
   - Price is calculated based on parameters

3. **Order Processing**:
   - Technologists update order status through the workflow
   - Technical notes and damage information can be added
   - Quality control is performed before completion

4. **Order Completion**:
   - Orders are marked as completed when ready
   - Clients receive notification
   - Order history is maintained for reporting

5. **Reporting**:
   - Managers and accountants access financial reports
   - Data analysis for business performance

## 💻 Usage Examples

### Creating Test Data

The system includes a data generation command to populate the database with test data:

```bash
# Basic usage with default parameters
python manage.py generate_test_data

# Custom parameters
python manage.py generate_test_data --users 20 --branches 5 --services 25 --orders 100

# Reset database before generating data
python manage.py generate_test_data --reset

# Skip user/client creation
python manage.py generate_test_data --skip-users
```

## 🔒 Security

- Role-based access control prevents unauthorized access to sensitive functions
- Permission checks at view level and template rendering
- Safe database query patterns

## 🚧 Development

### Adding a New Service Type

1. Log in as a manager
2. Navigate to "Управление услугами"
3. Click "Добавить услугу"
4. Enter the details and save

### Modifying User Roles

1. Access the admin panel at /admin
2. Edit the user's profile
3. Change the role field
4. Save changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Django Framework
- Bootstrap for UI components
- Contributors and testers

## 🖥️ Demo

Coming soon!
