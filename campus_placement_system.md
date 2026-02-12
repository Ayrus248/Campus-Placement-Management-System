campus\_placement\_system/

│

├── venv/                      # Virtual environment (don't modify)

│

├── placement\_project/         # Project configuration

│   ├── \_\_init\_\_.py

│   ├── settings.py           # ⚙️ Configuration hub

│   ├── urls.py               # 🔗 Main URL routing

│   ├── wsgi.py               # 🚀 Deployment file

│   └── asgi.py               # 🚀 Async deployment

│

├── placement/                 # Main application

│   ├── migrations/           # 📊 Database version control

│   ├── \_\_init\_\_.py

│   ├── admin.py              # 👨‍💼 Admin panel config

│   ├── apps.py               # 📱 App configuration

│   ├── models.py             # 🗄️ Database structure

│   ├── views.py              # 🎯 Business logic

│   └── tests.py              # 🧪 Unit tests

│

├── db.sqlite3                 # 💾 Database file

├── manage.py                  # 🛠️ Management script

└── requirements.txt           # 📦 Dependencies list







**MODELS**



1\. User (Custom User Model)

   ├── 2. StudentProfile (One-to-One with User)

   ├── 3. Company (Many-to-One with User)

 

4\. Branch (Academic Departments)



5\. JobPosting

   ├── Related to Company (Many-to-One)

   ├── Related to Branch (Many-to-Many)

 

6\. JobApplication

   ├── Related to StudentProfile (Many-to-One)

   ├── Related to JobPosting (Many-to-One)

 

7\. PlacementDrive

   ├── Related to Company (Many-to-Many)

   ├── Related to User/Admin (Many-to-One)







**HTML Templates**



placement/templates/placement/

├── base.html                    # Master template

├── home.html                    # Landing page

├── login.html                   # Login page

├── register.html                # Registration page

│

├── student/

│   ├── dashboard.html          # ✅ Created

│   ├── profile.html            # Student profile view

│   ├── edit\_profile.html       # Edit profile form

│   ├── jobs.html               # Browse jobs

│   ├── job\_detail.html         # Job details

│   ├── apply\_job.html          # Apply for job

│   ├── applications.html       # My applications

│   └── upload\_resume.html      # Resume upload

│

├── recruiter/

│   ├── dashboard.html          # Recruiter dashboard

│   ├── create\_company.html     # Company registration

│   ├── edit\_company.html       # Edit company

│   ├── create\_job.html         # Post job

│   ├── edit\_job.html           # Edit job

│   └── view\_applications.html  # View applications

│

└── admin/

&nbsp;   ├── dashboard.html          # Admin dashboard

&nbsp;   ├── statistics.html         # Detailed statistics

&nbsp;   ├── manage\_students.html    # Student management

&nbsp;   ├── manage\_companies.html   # Company management

&nbsp;   ├── manage\_drives.html      # Placement drives

&nbsp;   └── create\_drive.html       # Create drive

