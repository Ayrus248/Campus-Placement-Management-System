from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, StudentProfile, Branch, Company, 
    JobPosting, JobApplication, PlacementDrive
)


# ==================== CUSTOM USER ADMIN ====================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model with role-based filtering and display
    """
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'email', 'first_name', 'last_name')}),
    )


# ==================== STUDENT PROFILE ADMIN ====================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for Student Profiles with detailed information display
    """
    list_display = (
        'enrollment_number', 
        'get_student_name', 
        'branch', 
        'year', 
        'cgpa', 
        'backlogs',
        'has_resume',
        'placement_status'
    )
    list_filter = ('branch', 'year', 'is_placed', 'gender')
    search_fields = ('enrollment_number', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('-cgpa', 'backlogs')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('enrollment_number', 'date_of_birth', 'gender')
        }),
        ('Academic Information', {
            'fields': ('branch', 'year', 'cgpa', 'backlogs', 'tenth_percentage', 'twelfth_percentage')
        }),
        ('Skills & Experience', {
            'fields': ('skills', 'certifications', 'projects')
        }),
        ('Resume', {
            'fields': ('resume', 'resume_uploaded_at')
        }),
        ('Placement Status', {
            'fields': ('is_placed', 'placement_company', 'placement_package')
        }),
    )
    
    readonly_fields = ('resume_uploaded_at',)
    
    def get_student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_student_name.short_description = 'Student Name'
    
    def has_resume(self, obj):
        if obj.resume:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_resume.short_description = 'Resume'
    
    def placement_status(self, obj):
        if obj.is_placed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Placed</span>'
            )
        return format_html('<span style="color: orange;">Not Placed</span>')
    placement_status.short_description = 'Status'


# ==================== BRANCH ADMIN ====================
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """
    Admin interface for managing academic branches
    """
    list_display = ('code', 'name', 'total_students', 'created_at')
    search_fields = ('code', 'name')
    ordering = ('code',)
    
    def total_students(self, obj):
        count = StudentProfile.objects.filter(branch=obj.code).count()
        return count
    total_students.short_description = 'Total Students'


# ==================== COMPANY ADMIN ====================
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin interface for managing companies
    """
    list_display = (
        'name', 
        'industry', 
        'location', 
        'get_recruiter_name',
        'is_approved',
        'total_jobs',
        'active_jobs_count',
        'created_at'
    )
    list_filter = ('is_approved', 'industry', 'created_at')
    search_fields = ('name', 'industry', 'location', 'recruiter__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Company Information', {
            'fields': ('recruiter', 'name', 'description', 'industry', 'logo')
        }),
        ('Contact Details', {
            'fields': ('website', 'location', 'contact_person', 'contact_email', 'contact_phone')
        }),
        ('Approval Status', {
            'fields': ('is_approved',)
        }),
    )
    
    def get_recruiter_name(self, obj):
        return obj.recruiter.get_full_name() or obj.recruiter.username
    get_recruiter_name.short_description = 'Recruiter'
    
    def total_jobs(self, obj):
        return obj.total_jobs_posted()
    total_jobs.short_description = 'Total Jobs'
    
    def active_jobs_count(self, obj):
        count = obj.active_jobs()
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return count
    active_jobs_count.short_description = 'Active Jobs'


# ==================== JOB POSTING ADMIN ====================
class JobApplicationInline(admin.TabularInline):
    """
    Inline display of job applications within job posting
    """
    model = JobApplication
    extra = 0
    readonly_fields = ('student', 'status', 'applied_at')
    can_delete = False
    
    fields = ('student', 'status', 'applied_at')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    """
    Admin interface for managing job postings
    """
    list_display = (
        'title',
        'company',
        'job_type',
        'get_package_display',
        'minimum_cgpa',
        'maximum_backlogs',
        'deadline',
        'is_active',
        'application_count'
    )
    list_filter = ('job_type', 'is_active', 'created_at', 'company')
    search_fields = ('title', 'company__name', 'description')
    ordering = ('-created_at',)
    filter_horizontal = ('allowed_branches',)
    
    inlines = [JobApplicationInline]
    
    fieldsets = (
        ('Job Details', {
            'fields': ('company', 'title', 'description', 'job_type', 'location')
        }),
        ('Compensation', {
            'fields': ('package_min', 'package_max')
        }),
        ('Eligibility Criteria', {
            'fields': ('minimum_cgpa', 'maximum_backlogs', 'allowed_branches', 'allowed_years', 'required_skills')
        }),
        ('Application Details', {
            'fields': ('deadline', 'vacancies', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('bond_details', 'selection_process'),
            'classes': ('collapse',)
        }),
    )
    
    def get_package_display(self, obj):
        return f"₹{obj.package_min} - ₹{obj.package_max} LPA"
    get_package_display.short_description = 'Package Range'
    
    def application_count(self, obj):
        count = obj.total_applications()
        if count > 0:
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        return count
    application_count.short_description = 'Applications'


# ==================== JOB APPLICATION ADMIN ====================
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing job applications
    """
    list_display = (
        'get_student_name',
        'get_enrollment',
        'get_job_title',
        'get_company',
        'status',
        'applied_at'
    )
    list_filter = ('status', 'applied_at', 'job__company')
    search_fields = (
        'student__user__first_name',
        'student__user__last_name',
        'student__enrollment_number',
        'job__title',
        'job__company__name'
    )
    ordering = ('-applied_at',)
    
    fieldsets = (
        ('Application Details', {
            'fields': ('student', 'job', 'status')
        }),
        ('Cover Letter', {
            'fields': ('cover_letter',)
        }),
        ('Recruiter Feedback', {
            'fields': ('recruiter_notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('applied_at',)
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = 'Student'
    
    def get_enrollment(self, obj):
        return obj.student.enrollment_number
    get_enrollment.short_description = 'Enrollment No.'
    
    def get_job_title(self, obj):
        return obj.job.title
    get_job_title.short_description = 'Job Title'
    
    def get_company(self, obj):
        return obj.job.company.name
    get_company.short_description = 'Company'


# ==================== PLACEMENT DRIVE ADMIN ====================
@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    """
    Admin interface for managing placement drives
    """
    list_display = (
        'title',
        'start_date',
        'end_date',
        'is_active',
        'company_count',
        'created_at'
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    ordering = ('-start_date',)
    filter_horizontal = ('companies',)
    
    fieldsets = (
        ('Drive Information', {
            'fields': ('title', 'description')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Participating Companies', {
            'fields': ('companies',)
        }),
        ('Created By', {
            'fields': ('created_by',)
        }),
    )
    
    def company_count(self, obj):
        count = obj.total_companies()
        return format_html('<span style="color: blue;">{} companies</span>', count)
    company_count.short_description = 'Companies'


# ==================== ADMIN SITE CUSTOMIZATION ====================
admin.site.site_header = "Campus Placement Management System"
admin.site.site_title = "CPMS Admin"
admin.site.index_title = "Welcome to CPMS Administration"