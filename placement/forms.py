from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, Company, JobPosting, Branch


class UserRegistrationForm(UserCreationForm):
    """Form for new user registration"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude 'admin' from role choices for public registration
        self.fields['role'].choices = [
            ('student', 'Student'),
            ('recruiter', 'Recruiter'),
        ]
        
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(forms.Form):
    """Simple login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class StudentProfileForm(forms.ModelForm):
    """Form for creating/editing student profile"""
    
    class Meta:
        model = StudentProfile
        fields = [
            'enrollment_number', 'date_of_birth', 'gender',
            'branch', 'year', 'cgpa', 'backlogs',
            'tenth_percentage', 'twelfth_percentage',
            'skills', 'certifications', 'projects', 'resume'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., Python, Java, SQL, Django'}),
            'certifications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List your certifications'}),
            'projects': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your projects'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name != 'resume':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control-file'


class CompanyForm(forms.ModelForm):
    """Form for creating/editing company"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'description', 'website', 'industry', 'logo',
            'location', 'contact_person', 'contact_email', 'contact_phone'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name not in ['logo']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control-file'


class JobPostingForm(forms.ModelForm):
    """Form for creating/editing job postings"""
    
    class Meta:
        model = JobPosting
        fields = [
            'company', 'title', 'description', 'job_type', 'location',
            'package_min', 'package_max', 'minimum_cgpa', 'maximum_backlogs',
            'allowed_branches', 'allowed_years', 'required_skills',
            'deadline', 'vacancies', 'is_active',
            'bond_details', 'selection_process'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'required_skills': forms.Textarea(attrs={'rows': 3}),
            'bond_details': forms.Textarea(attrs={'rows': 3}),
            'selection_process': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'allowed_branches': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        recruiter = kwargs.pop('recruiter', None)
        super().__init__(*args, **kwargs)
        
        # Limit company choices to recruiter's approved companies
        if recruiter:
            self.fields['company'].queryset = Company.objects.filter(
                recruiter=recruiter,
                is_approved=True
            )
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name != 'allowed_branches':
                field.widget.attrs['class'] = 'form-control'


class ResumeUploadForm(forms.ModelForm):
    """Form for uploading resume"""
    
    class Meta:
        model = StudentProfile
        fields = ['resume']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].widget.attrs['class'] = 'form-control-file'
        self.fields['resume'].required = True
