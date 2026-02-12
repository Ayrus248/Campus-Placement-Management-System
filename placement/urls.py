from django.urls import path
from . import views

app_name = 'placement'

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # ==================== STUDENT URLS ====================
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/profile/edit/', views.edit_student_profile, name='edit_student_profile'),
    path('student/jobs/', views.student_jobs, name='student_jobs'),
    path('student/job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('student/apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('student/applications/', views.my_applications, name='my_applications'),
    path('student/resume/upload/', views.upload_resume, name='upload_resume'),
    path('student/resume/download/', views.download_resume, name='download_resume'),
    
    # ==================== RECRUITER URLS ====================
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/company/create/', views.create_company, name='create_company'),
    path('recruiter/company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('recruiter/job/create/', views.create_job, name='create_job'),
    path('recruiter/job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('recruiter/job/<int:job_id>/applications/', views.view_applications, name='view_applications'),
    path('recruiter/application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    
    # ==================== ADMIN URLS ====================
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/statistics/', views.statistics, name='statistics'),
    path('admin-panel/students/', views.manage_students, name='manage_students'),
    path('admin-panel/companies/', views.manage_companies, name='manage_companies'),
    path('admin-panel/company/<int:company_id>/approve/', views.approve_company, name='approve_company'),
    path('admin-panel/drives/', views.manage_drives, name='manage_drives'),
    path('admin-panel/drive/create/', views.create_drive, name='create_drive'),
    
    # ==================== COMMON/SHARED URLS ====================
    path('download-resume/<int:student_id>/', views.download_student_resume, name='download_student_resume'),
]
