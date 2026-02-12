
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone


# ==================== CUSTOM USER MODEL ====================
class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based access control for different user types.
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin/Placement Officer'),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text="User role in the system"
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_student(self):
        return self.role == 'student'
    
    def is_recruiter(self):
        return self.role == 'recruiter'
    
    def is_placement_admin(self):
        return self.role == 'admin'


# ==================== STUDENT PROFILE ====================
class StudentProfile(models.Model):
    """
    Detailed profile for students including academic information,
    skills, resume, and eligibility criteria.
    """
    BRANCH_CHOICES = (
        ('CSE', 'Computer Science Engineering'),
        ('IT', 'Information Technology'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('CHEM', 'Chemical Engineering'),
        ('OTHER', 'Other'),
    )
    
    YEAR_CHOICES = (
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="Link to user account"
    )
    
    # Personal Information
    enrollment_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="University enrollment/registration number"
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Student's date of birth"
    )
    
    gender = models.CharField(
        max_length=10,
        choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')),
        default='M'
    )
    
    # Academic Information
    branch = models.CharField(
        max_length=10,
        choices=BRANCH_CHOICES,
        help_text="Branch/Department"
    )
    
    year = models.CharField(
        max_length=1,
        choices=YEAR_CHOICES,
        help_text="Current year of study"
    )
    
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Cumulative Grade Point Average (0-10 scale)"
    )
    
    backlogs = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of active backlogs/arrears"
    )
    
    tenth_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="10th standard percentage"
    )
    
    twelfth_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="12th standard percentage"
    )
    
    # Skills and Experience
    skills = models.TextField(
        help_text="Comma-separated list of skills (e.g., Python, Java, SQL)"
    )
    
    certifications = models.TextField(
        blank=True,
        null=True,
        help_text="List of certifications and courses completed"
    )
    
    projects = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of projects completed"
    )
    
    # Resume Management
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Upload resume in PDF format only"
    )
    
    resume_uploaded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when resume was uploaded"
    )
    
    # Status
    is_placed = models.BooleanField(
        default=False,
        help_text="Whether student has been placed"
    )
    
    placement_company = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Company where student got placed"
    )
    
    placement_package = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Annual package in lakhs"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ['-cgpa', 'backlogs']   
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.enrollment_number}"
    
    def get_eligibility_status(self, job):
        """Check if student is eligible for a specific job"""
        if self.cgpa < job.minimum_cgpa:
            return False, f"CGPA requirement not met (Required: {job.minimum_cgpa})"
        
        if self.backlogs > job.maximum_backlogs:
            return False, f"Too many backlogs (Maximum allowed: {job.maximum_backlogs})"
        
        if job.allowed_branches.exists() and self.branch not in job.allowed_branches.values_list('code', flat=True):
            return False, "Branch not eligible"
        
        return True, "Eligible"
    
    def save(self, *args, **kwargs):
        if self.resume and not self.resume_uploaded_at:
            self.resume_uploaded_at = timezone.now()
        super().save(*args, **kwargs)


# ==================== BRANCH MODEL ====================
class Branch(models.Model):
    """
    Academic branches/departments in the institution.
    Used for filtering jobs by branch eligibility.
    """
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short code for branch (e.g., CSE, ECE)"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Full name of the branch"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of the branch"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================== COMPANY MODEL ====================
class Company(models.Model):
    """
    Companies/Organizations that recruit from campus.
    Linked to recruiter users.
    """
    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='companies',
        limit_choices_to={'role': 'recruiter'},
        help_text="Recruiter who manages this company"
    )
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Company name"
    )
    
    description = models.TextField(
        help_text="Brief description of the company"
    )
    
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Company website URL"
    )
    
    industry = models.CharField(
        max_length=100,
        help_text="Industry sector (e.g., IT, Finance, Manufacturing)"
    )
    
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        help_text="Company logo"
    )
    
    location = models.CharField(
        max_length=200,
        help_text="Headquarters or primary location"
    )
    
    contact_person = models.CharField(
        max_length=100,
        help_text="Name of HR/recruitment contact person"
    )
    
    contact_email = models.EmailField(
        help_text="Contact email for recruitment queries"
    )
    
    contact_phone = models.CharField(
        max_length=15,
        help_text="Contact phone number"
    )
    
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether company is approved by admin"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def total_jobs_posted(self):
        return self.jobs.count()
    
    def active_jobs(self):
        return self.jobs.filter(is_active=True, deadline__gte=timezone.now()).count()


# ==================== JOB POSTING MODEL ====================
class JobPosting(models.Model):
    """
    Job opportunities posted by companies.
    Includes eligibility criteria and application deadline.
    """
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('internship', 'Internship'),
        ('part_time', 'Part Time'),
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Company posting this job"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Job title/position"
    )
    
    description = models.TextField(
        help_text="Detailed job description"
    )
    
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default='full_time',
        help_text="Type of employment"
    )
    
    location = models.CharField(
        max_length=200,
        help_text="Job location(s)"
    )
    
    # Compensation
    package_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Minimum package/stipend in lakhs per annum"
    )
    
    package_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Maximum package/stipend in lakhs per annum"
    )
    
    # Eligibility Criteria
    minimum_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Minimum CGPA required"
    )
    
    maximum_backlogs = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Maximum number of backlogs allowed"
    )
    
    allowed_branches = models.ManyToManyField(
        Branch,
        blank=True,
        related_name='jobs',
        help_text="Branches eligible for this job (leave empty for all branches)"
    )
    
    allowed_years = models.CharField(
        max_length=20,
        default='4',
        help_text="Comma-separated years eligible (e.g., '3,4' for third and fourth year)"
    )
    
    # Skills Required
    required_skills = models.TextField(
        help_text="Skills required for this position"
    )
    
    # Application Details
    deadline = models.DateTimeField(
        help_text="Application deadline"
    )
    
    vacancies = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of positions available"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether job is currently accepting applications"
    )
    
    # Additional Information
    bond_details = models.TextField(
        blank=True,
        null=True,
        help_text="Bond or service agreement details"
    )
    
    selection_process = models.TextField(
        blank=True,
        null=True,
        help_text="Details about selection rounds (written test, interview, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Job Posting"
        verbose_name_plural = "Job Postings"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    def is_deadline_passed(self):
        return timezone.now() > self.deadline
    
    def total_applications(self):
        return self.applications.count()
    
    def pending_applications(self):
        return self.applications.filter(status='pending').count()
    
    def accepted_applications(self):
        return self.applications.filter(status='accepted').count()
    
    def get_package_range(self):
        return f"₹{self.package_min} - ₹{self.package_max} LPA"


# ==================== JOB APPLICATION MODEL ====================
class JobApplication(models.Model):
    """
    Student applications for job postings.
    Tracks application status and timestamps.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted/Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn by Student'),
    )
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="Student who applied"
    )
    
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="Job applied for"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current application status"
    )
    
    cover_letter = models.TextField(
        blank=True,
        null=True,
        help_text="Optional cover letter or message to recruiter"
    )
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Feedback from recruiter
    recruiter_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes from recruiter (visible to admin only)"
    )
    
    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_at']
        unique_together = ('student', 'job')  # Prevent duplicate applications
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.job.title}"
    
    def can_withdraw(self):
        """Check if student can withdraw application"""
        return self.status == 'pending' and not self.job.is_deadline_passed()


# ==================== PLACEMENT DRIVE MODEL ====================
class PlacementDrive(models.Model):
    """
    Organized placement drives/events.
    Groups multiple job postings under one drive.
    """
    title = models.CharField(
        max_length=200,
        help_text="Drive title (e.g., 'Winter Placements 2024')"
    )
    
    description = models.TextField(
        help_text="Description and details of the drive"
    )
    
    start_date = models.DateField(
        help_text="Drive start date"
    )
    
    end_date = models.DateField(
        help_text="Drive end date"
    )
    
    companies = models.ManyToManyField(
        Company,
        blank=True,
        related_name='drives',
        help_text="Companies participating in this drive"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether drive is currently active"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'admin'},
        help_text="Admin who created this drive"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Placement Drive"
        verbose_name_plural = "Placement Drives"
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def total_companies(self):
        return self.companies.count()
    
    def total_jobs(self):
        return JobPosting.objects.filter(company__in=self.companies.all()).count()
