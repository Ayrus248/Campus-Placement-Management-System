# Campus Placement Management System

A comprehensive web-based platform designed to streamline campus placement activities, enabling students, recruiters, and placement officers to interact effectively.

## Features

### For Students
- Profile creation with academic details (CGPA, backlogs, skills)
- Resume upload and download
- Browse and apply for job postings
- View application status
- Filter jobs based on eligibility (CGPA, backlogs)

### For Recruiters
- Company profile management
- Post job openings with eligibility criteria
- View student applications
- Access student profiles and resumes
- Track recruitment drives

### For Placement Officers/Admin
- Manage students, recruiters, and companies
- View placement statistics and analytics
- Generate reports
- Manage job postings and applications
- Track placement drives and results

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite3
- **Authentication**: Django's built-in authentication with role-based access control

## Installation & Setup

### Step 1: Prerequisites
Make sure you have Python 3.8+ installed on your system.

```bash
python --version
```

### Step 2: Clone or Download the Project
Download the project files to your local machine.

### Step 3: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Create Django Project Structure
```bash
# This creates the main project configuration
django-admin startproject placement_project .

# Create the main application
python manage.py startapp placement
```

### Step 6: Database Setup
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow the prompts to create admin credentials
```

### Step 8: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
campus_placement_system/
│
├── placement_project/          # Main project configuration
│   ├── __init__.py
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── placement/                  # Main application
│   ├── migrations/            # Database migrations
│   ├── static/                # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/             # HTML templates
│   │   └── placement/
│   ├── __init__.py
│   ├── admin.py               # Admin panel configuration
│   ├── apps.py                # App configuration
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # App URL patterns
│   └── forms.py               # Form definitions
│
├── media/                      # User uploaded files (resumes)
│   └── resumes/
│
├── manage.py                   # Django management script
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

## User Roles

1. **Student**: Can create profile, upload resume, apply for jobs
2. **Recruiter**: Can post jobs, view applications, access student data
3. **Admin/Placement Officer**: Full access to all features, statistics, and management

## Key Features Explained

### Role-Based Access Control
- Custom user model with role field (Student, Recruiter, Admin)
- Decorators to restrict views based on user roles
- Different dashboards for each role

### Student Profile Management
- Academic details (CGPA, backlogs, branch, year)
- Skills and certifications
- Resume upload with PDF validation
- Resume download functionality

### Job Posting System
- Companies can post jobs with eligibility criteria
- CGPA cutoff and backlog restrictions
- Automatic filtering based on student eligibility
- Application deadline management

### Smart Job Filtering
- Jobs sorted based on eligibility (CGPA, backlogs)
- Students only see jobs they're eligible for
- Search and filter functionality

### Statistics Dashboard
- Total students, companies, jobs
- Placement percentage
- Company-wise placement stats
- Branch-wise placement analysis
- Visual charts and graphs

### Resume Management
- Secure file upload
- PDF format validation
- Download functionality for authorized users
- File size restrictions

## Security Features

- Password hashing using Django's authentication system
- CSRF protection on all forms
- Login required decorators
- Role-based access control
- Secure file uploads

## Future Enhancements

- Email notifications for new job postings
- Interview scheduling system
- Multiple rounds tracking
- Bulk student data upload (CSV/Excel)
- Advanced analytics with charts
- Export reports to PDF/Excel
- Online assessment integration

## Troubleshooting

### Database Issues
If you encounter database errors, delete `db.sqlite3` and all migration files (except `__init__.py` in migrations folder), then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
Run:
```bash
python manage.py collectstatic
```

### Port Already in Use
Use a different port:
```bash
python manage.py runserver 8080
```

## Support

For issues and queries, refer to the Django documentation at https://docs.djangoproject.com/

## License

This project is for educational purposes.
