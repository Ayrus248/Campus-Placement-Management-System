from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from functools import wraps
import mimetypes

from .models import (
    User, StudentProfile, Branch, Company, 
    JobPosting, JobApplication, PlacementDrive
)
from .forms import (
    UserRegistrationForm, LoginForm, StudentProfileForm,
    CompanyForm, JobPostingForm, ResumeUploadForm
)


# ==================== DECORATORS FOR ROLE-BASED ACCESS ====================
def student_required(view_func):
    """Decorator to restrict access to students only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('placement:login')
        if request.user.role != 'student':
            messages.error(request, "Access denied. Students only.")
            return redirect('placement:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def recruiter_required(view_func):
    """Decorator to restrict access to recruiters only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('placement:login')
        if request.user.role != 'recruiter':
            messages.error(request, "Access denied. Recruiters only.")
            return redirect('placement:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to restrict access to admins only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('placement:login')
        if request.user.role != 'admin':
            messages.error(request, "Access denied. Admins only.")
            return redirect('placement:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== HOME & AUTHENTICATION VIEWS ====================
def home(request):
    """
    Home page - redirects to appropriate dashboard based on user role
    """
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('placement:student_dashboard')
        elif request.user.role == 'recruiter':
            return redirect('placement:recruiter_dashboard')
        elif request.user.role == 'admin':
            return redirect('placement:admin_dashboard')
    
    context = {
        'total_students': StudentProfile.objects.count(),
        'total_companies': Company.objects.filter(is_approved=True).count(),
        'total_jobs': JobPosting.objects.filter(is_active=True).count(),
        'placed_students': StudentProfile.objects.filter(is_placed=True).count(),
    }
    return render(request, 'placement/home.html', context)


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('placement:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect('placement:home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    
    return render(request, 'placement/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('placement:home')


def register(request):
    """Handle new user registration"""
    if request.user.is_authenticated:
        return redirect('placement:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Please complete your profile.")
            
            if user.role == 'student':
                return redirect('placement:edit_student_profile')
            elif user.role == 'recruiter':
                return redirect('placement:create_company')
            
            return redirect('placement:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'placement/register.html', {'form': form})


# ==================== STUDENT VIEWS ====================
@student_required
def student_dashboard(request):
    """Student dashboard showing overview and quick stats"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect('placement:edit_student_profile')
    
    # Get eligible jobs
    eligible_jobs = []
    all_jobs = JobPosting.objects.filter(
        is_active=True,
        deadline__gte=timezone.now()
    )
    
    for job in all_jobs:
        is_eligible, message = profile.get_eligibility_status(job)
        if is_eligible:
            eligible_jobs.append(job)
    
    # Get recent applications
    recent_applications = JobApplication.objects.filter(
        student=profile
    ).order_by('-applied_at')[:5]
    
    context = {
        'profile': profile,
        'eligible_jobs_count': len(eligible_jobs),
        'total_applications': JobApplication.objects.filter(student=profile).count(),
        'pending_applications': JobApplication.objects.filter(student=profile, status='pending').count(),
        'recent_applications': recent_applications,
        'eligible_jobs': eligible_jobs[:5],  # Show top 5
    }
    return render(request, 'placement/student/dashboard.html', context)


@student_required
def student_profile(request):
    """View student profile"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, "Please create your profile first.")
        return redirect('placement:edit_student_profile')
    
    return render(request, 'placement/student/profile.html', {'profile': profile})


@student_required
def edit_student_profile(request):
    """Create or edit student profile"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('placement:student_profile')
    else:
        form = StudentProfileForm(instance=profile)
    
    return render(request, 'placement/student/edit_profile.html', {'form': form})


@student_required
def student_jobs(request):
    """List all jobs with eligibility filtering"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect('placement:edit_student_profile')
    
    # Get all active jobs
    jobs = JobPosting.objects.filter(
        is_active=True,
        deadline__gte=timezone.now()
    ).select_related('company')
    
    # Filter by search query
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by company
    company_filter = request.GET.get('company', '')
    if company_filter:
        jobs = jobs.filter(company__id=company_filter)
    
    # Add eligibility status to each job
    jobs_with_eligibility = []
    for job in jobs:
        is_eligible, message = profile.get_eligibility_status(job)
        # Check if already applied
        has_applied = JobApplication.objects.filter(student=profile, job=job).exists()
        
        jobs_with_eligibility.append({
            'job': job,
            'is_eligible': is_eligible,
            'eligibility_message': message,
            'has_applied': has_applied,
        })
    
    # Sort: eligible jobs first
    jobs_with_eligibility.sort(key=lambda x: (not x['is_eligible'], x['job'].deadline))
    
    companies = Company.objects.filter(is_approved=True)
    
    context = {
        'jobs_with_eligibility': jobs_with_eligibility,
        'companies': companies,
        'search_query': search_query,
    }
    return render(request, 'placement/student/jobs.html', context)


@student_required
def job_detail(request, job_id):
    """View detailed information about a specific job"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    try:
        profile = request.user.student_profile
        is_eligible, eligibility_message = profile.get_eligibility_status(job)
        has_applied = JobApplication.objects.filter(student=profile, job=job).exists()
    except StudentProfile.DoesNotExist:
        is_eligible = False
        eligibility_message = "Please complete your profile first."
        has_applied = False
    
    context = {
        'job': job,
        'is_eligible': is_eligible,
        'eligibility_message': eligibility_message,
        'has_applied': has_applied,
    }
    return render(request, 'placement/student/job_detail.html', context)


@student_required
def apply_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Please complete your profile before applying.")
        return redirect('placement:edit_student_profile')
    
    # Check if already applied
    if JobApplication.objects.filter(student=profile, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('placement:job_detail', job_id=job_id)
    
    # Check eligibility
    is_eligible, eligibility_message = profile.get_eligibility_status(job)
    if not is_eligible:
        messages.error(request, f"You are not eligible: {eligibility_message}")
        return redirect('placement:job_detail', job_id=job_id)
    
    # Check if job is still active
    if not job.is_active or job.is_deadline_passed():
        messages.error(request, "This job is no longer accepting applications.")
        return redirect('placement:job_detail', job_id=job_id)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        
        # Create application
        application = JobApplication.objects.create(
            student=profile,
            job=job,
            cover_letter=cover_letter,
            status='pending'
        )
        
        messages.success(request, f"Successfully applied for {job.title} at {job.company.name}!")
        return redirect('placement:my_applications')
    
    return render(request, 'placement/student/apply_job.html', {'job': job})


@student_required
def my_applications(request):
    """View all applications submitted by the student"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect('placement:edit_student_profile')
    
    applications = JobApplication.objects.filter(
        student=profile
    ).select_related('job__company').order_by('-applied_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'placement/student/applications.html', context)


@student_required
def upload_resume(request):
    """Upload or update resume"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('placement:edit_student_profile')
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume uploaded successfully!")
            return redirect('placement:student_profile')
    else:
        form = ResumeUploadForm(instance=profile)
    
    return render(request, 'placement/student/upload_resume.html', {'form': form, 'profile': profile})


@student_required
def download_resume(request):
    """Download own resume"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('placement:student_dashboard')
    
    if not profile.resume:
        messages.error(request, "No resume uploaded yet.")
        return redirect('placement:student_profile')
    
    try:
        response = FileResponse(profile.resume.open('rb'))
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = f'attachment; filename="{profile.enrollment_number}_resume.pdf"'
        return response
    except Exception as e:
        messages.error(request, "Error downloading resume.")
        return redirect('placement:student_profile')


# ==================== RECRUITER VIEWS ====================
@recruiter_required
def recruiter_dashboard(request):
    """Recruiter dashboard showing their companies and jobs"""
    companies = Company.objects.filter(recruiter=request.user)
    
    total_jobs = JobPosting.objects.filter(company__recruiter=request.user).count()
    active_jobs = JobPosting.objects.filter(
        company__recruiter=request.user,
        is_active=True,
        deadline__gte=timezone.now()
    ).count()
    
    total_applications = JobApplication.objects.filter(
        job__company__recruiter=request.user
    ).count()
    
    pending_applications = JobApplication.objects.filter(
        job__company__recruiter=request.user,
        status='pending'
    ).count()
    
    recent_applications = JobApplication.objects.filter(
        job__company__recruiter=request.user
    ).select_related('student__user', 'job').order_by('-applied_at')[:10]
    
    context = {
        'companies': companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_applications': recent_applications,
    }
    return render(request, 'placement/recruiter/dashboard.html', context)


@recruiter_required
def create_company(request):
    """Create a new company"""
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.recruiter = request.user
            company.save()
            messages.success(request, f"Company '{company.name}' created successfully! Awaiting admin approval.")
            return redirect('placement:recruiter_dashboard')
    else:
        form = CompanyForm()
    
    return render(request, 'placement/recruiter/create_company.html', {'form': form})


@recruiter_required
def edit_company(request, company_id):
    """Edit company details"""
    company = get_object_or_404(Company, id=company_id, recruiter=request.user)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company details updated successfully!")
            return redirect('placement:recruiter_dashboard')
    else:
        form = CompanyForm(instance=company)
    
    return render(request, 'placement/recruiter/edit_company.html', {'form': form, 'company': company})


@recruiter_required
def create_job(request):
    """Create a new job posting"""
    companies = Company.objects.filter(recruiter=request.user, is_approved=True)
    
    if not companies.exists():
        messages.error(request, "You need an approved company before posting jobs.")
        return redirect('placement:create_company')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, recruiter=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Job posted successfully!")
            return redirect('placement:recruiter_dashboard')
    else:
        form = JobPostingForm(recruiter=request.user)
    
    return render(request, 'placement/recruiter/create_job.html', {'form': form})


@recruiter_required
def edit_job(request, job_id):
    """Edit job posting"""
    job = get_object_or_404(JobPosting, id=job_id, company__recruiter=request.user)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job, recruiter=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('placement:recruiter_dashboard')
    else:
        form = JobPostingForm(instance=job, recruiter=request.user)
    
    return render(request, 'placement/recruiter/edit_job.html', {'form': form, 'job': job})


@recruiter_required
def view_applications(request, job_id):
    """View all applications for a specific job"""
    job = get_object_or_404(JobPosting, id=job_id, company__recruiter=request.user)
    
    applications = JobApplication.objects.filter(
        job=job
    ).select_related('student__user').order_by('-applied_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'job': job,
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'placement/recruiter/view_applications.html', context)


@recruiter_required
def update_application_status(request, application_id):
    """Update application status"""
    application = get_object_or_404(
        JobApplication,
        id=application_id,
        job__company__recruiter=request.user
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        recruiter_notes = request.POST.get('recruiter_notes', '')
        
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.recruiter_notes = recruiter_notes
            application.save()
            messages.success(request, f"Application status updated to {application.get_status_display()}.")
        else:
            messages.error(request, "Invalid status.")
    
    return redirect('placement:view_applications', job_id=application.job.id)


# ==================== ADMIN VIEWS ====================
@admin_required
def admin_dashboard(request):
    """Admin dashboard with overview statistics"""
    # Basic counts
    total_students = StudentProfile.objects.count()
    total_companies = Company.objects.count()
    approved_companies = Company.objects.filter(is_approved=True).count()
    total_jobs = JobPosting.objects.count()
    active_jobs = JobPosting.objects.filter(is_active=True, deadline__gte=timezone.now()).count()
    
    # Placement statistics
    placed_students = StudentProfile.objects.filter(is_placed=True).count()
    placement_percentage = (placed_students / total_students * 100) if total_students > 0 else 0
    
    # Application statistics
    total_applications = JobApplication.objects.count()
    pending_applications = JobApplication.objects.filter(status='pending').count()
    
    # Recent activity
    recent_applications = JobApplication.objects.select_related(
        'student__user', 'job__company'
    ).order_by('-applied_at')[:10]
    
    pending_companies = Company.objects.filter(is_approved=False)[:5]
    
    # Branch-wise statistics
    branch_stats = StudentProfile.objects.values('branch').annotate(
        total=Count('id'),
        placed=Count('id', filter=Q(is_placed=True)),
        avg_cgpa=Avg('cgpa')
    ).order_by('branch')
    
    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'approved_companies': approved_companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'placed_students': placed_students,
        'placement_percentage': round(placement_percentage, 2),
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_applications': recent_applications,
        'pending_companies': pending_companies,
        'branch_stats': branch_stats,
    }
    return render(request, 'placement/admin/dashboard.html', context)


@admin_required
def statistics(request):
    """Detailed statistics page"""
    # Overall stats
    total_students = StudentProfile.objects.count()
    placed_students = StudentProfile.objects.filter(is_placed=True).count()
    
    # Branch-wise detailed stats
    branch_stats = StudentProfile.objects.values('branch').annotate(
        total_students=Count('id'),
        placed_students=Count('id', filter=Q(is_placed=True)),
        avg_cgpa=Avg('cgpa'),
        avg_package=Avg('placement_package', filter=Q(is_placed=True))
    ).order_by('branch')
    
    # Company-wise placements
    company_stats = StudentProfile.objects.filter(
        is_placed=True
    ).values('placement_company').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # CGPA distribution
    cgpa_ranges = [
        ('9.0 - 10.0', StudentProfile.objects.filter(cgpa__gte=9.0).count()),
        ('8.0 - 8.9', StudentProfile.objects.filter(cgpa__gte=8.0, cgpa__lt=9.0).count()),
        ('7.0 - 7.9', StudentProfile.objects.filter(cgpa__gte=7.0, cgpa__lt=8.0).count()),
        ('6.0 - 6.9', StudentProfile.objects.filter(cgpa__gte=6.0, cgpa__lt=7.0).count()),
        ('Below 6.0', StudentProfile.objects.filter(cgpa__lt=6.0).count()),
    ]
    
    context = {
        'total_students': total_students,
        'placed_students': placed_students,
        'branch_stats': branch_stats,
        'company_stats': company_stats,
        'cgpa_ranges': cgpa_ranges,
    }
    return render(request, 'placement/admin/statistics.html', context)


@admin_required
def manage_students(request):
    """Manage all students"""
    students = StudentProfile.objects.select_related('user').all()
    
    # Filters
    branch_filter = request.GET.get('branch', '')
    year_filter = request.GET.get('year', '')
    placement_filter = request.GET.get('placement', '')
    search_query = request.GET.get('search', '')
    
    if branch_filter:
        students = students.filter(branch=branch_filter)
    if year_filter:
        students = students.filter(year=year_filter)
    if placement_filter == 'placed':
        students = students.filter(is_placed=True)
    elif placement_filter == 'not_placed':
        students = students.filter(is_placed=False)
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(enrollment_number__icontains=search_query)
        )
    
    context = {
        'students': students,
        'branches': StudentProfile.BRANCH_CHOICES,
        'years': StudentProfile.YEAR_CHOICES,
    }
    return render(request, 'placement/admin/manage_students.html', context)


@admin_required
def manage_companies(request):
    """Manage all companies"""
    companies = Company.objects.select_related('recruiter').all()
    
    approval_filter = request.GET.get('approval', '')
    if approval_filter == 'approved':
        companies = companies.filter(is_approved=True)
    elif approval_filter == 'pending':
        companies = companies.filter(is_approved=False)
    
    context = {
        'companies': companies,
    }
    return render(request, 'placement/admin/manage_companies.html', context)


@admin_required
def approve_company(request, company_id):
    """Approve or reject a company"""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            company.is_approved = True
            company.save()
            messages.success(request, f"Company '{company.name}' has been approved.")
        elif action == 'reject':
            company.is_approved = False
            company.save()
            messages.warning(request, f"Company '{company.name}' approval has been revoked.")
    
    return redirect('placement:manage_companies')


@admin_required
def manage_drives(request):
    """Manage placement drives"""
    drives = PlacementDrive.objects.all().order_by('-start_date')
    
    context = {
        'drives': drives,
    }
    return render(request, 'placement/admin/manage_drives.html', context)


@admin_required
def create_drive(request):
    """Create a new placement drive"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        drive = PlacementDrive.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_by=request.user,
            is_active=True
        )
        
        messages.success(request, f"Placement drive '{title}' created successfully!")
        return redirect('placement:manage_drives')
    
    return render(request, 'placement/admin/create_drive.html')


# ==================== COMMON/SHARED VIEWS ====================
@login_required
def download_student_resume(request, student_id):
    """Download a student's resume (accessible by recruiters and admins)"""
    # Only recruiters and admins can download resumes
    if request.user.role not in ['recruiter', 'admin']:
        messages.error(request, "Access denied.")
        return redirect('placement:home')
    
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if not student.resume:
        messages.error(request, "This student has not uploaded a resume.")
        return redirect(request.META.get('HTTP_REFERER', 'placement:home'))
    
    try:
        response = FileResponse(student.resume.open('rb'))
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = f'attachment; filename="{student.enrollment_number}_resume.pdf"'
        return response
    except Exception as e:
        messages.error(request, "Error downloading resume.")
        return redirect(request.META.get('HTTP_REFERER', 'placement:home'))
