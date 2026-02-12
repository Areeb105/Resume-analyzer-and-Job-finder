
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from .utils import extract_text_from_pdf, extract_skills, aggregate_jobs, calculate_ats_score
import os

@csrf_exempt
def upload_view(request):
    if request.method == 'POST':
        if 'resume' not in request.FILES:
            return JsonResponse({'error': 'No resume file provided'}, status=400)
        
        resume_file = request.FILES['resume']
        
        # Simple file saving for now
        file_path = default_storage.save(f'resumes/{resume_file.name}', resume_file)
        # Fix path for windows if needed, though default_storage handles it usually.
        # However, extract_text_from_pdf might need absolute path.
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # 1. Extract Text
        try:
            text = extract_text_from_pdf(full_path)
        except Exception as e:
             return JsonResponse({'error': f"Failed to extract text: {str(e)}"}, status=500)

        # 2. Extract Skills
        skills = extract_skills(text)
        
        # 3. Calculate ATS Score (now includes missing keywords and summary)
        ats_score, ats_breakdown = calculate_ats_score(text, skills)

        # 4. Save to UserProfile (if authenticated)
        if request.user.is_authenticated:
            try:
                from .models import UserProfile
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.resume = file_path # Save relative path
                profile.skills = skills
                profile.ats_score = ats_score
                profile.ats_breakdown = ats_breakdown
                profile.save()
            except Exception as e:
                print(f"Error saving profile: {e}")

        return JsonResponse({
            'success': True,
            'skills': skills,
            'ats_score': ats_score,
            'ats_breakdown': ats_breakdown,
            'missing_keywords': ats_breakdown.get('missing_keywords', []),
            'professional_summary': ats_breakdown.get('professional_summary', '')
            # Jobs are now fetched asynchronously via /api/jobs/
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_jobs_view(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            skills = data.get('skills', [])
            
            jobs = []
            try:
                # Use aggregate_jobs to fetch from multiple APIs
                jobs = aggregate_jobs(skills)
            except Exception as e:
                print(f"Job API Error: {e}")
                
            return JsonResponse({'success': True, 'jobs': jobs})
        except Exception as e:
             return JsonResponse({'error': str(e)}, status=400)
             
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)
            
            if username.isdigit():
                return JsonResponse({'error': 'Username cannot be only numbers'}, status=400)
            
            if len(username) < 4:
                return JsonResponse({'error': 'Username must be at least 4 characters long'}, status=400)
            
            if len(password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters long'}, status=400)
            
            if password.isdigit():
                return JsonResponse({'error': 'Password cannot be only numbers'}, status=400)
                
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already taken'}, status=400)
                
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'core/register.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'core/logout.html')

@login_required(login_url='/login/')
def onboarding_view(request):
    return render(request, 'core/onboarding.html')

def index(request):
    if request.user.is_authenticated:
        return render(request, 'core/dashboard.html')
    return render(request, 'core/index.html')

@login_required(login_url='/login/')
def dashboard(request):
    context = {}
    try:
        from .models import UserProfile
        profile = UserProfile.objects.get(user=request.user)
        
        # Prepare data for frontend hydration
        context['user_profile_data'] = json.dumps({
            'resumeName': os.path.basename(profile.resume.name) if profile.resume else None,
            'skills': profile.skills,
            'atsScore': profile.ats_score,
            'atsBreakdown': profile.ats_breakdown,
            'uploadedAt': profile.uploaded_at.isoformat() if profile.uploaded_at else None
        })
    except UserProfile.DoesNotExist:
        context['user_profile_data'] = 'null'
        
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/login/')
@csrf_exempt
def upload_page(request): # Renamed to avoid conflict with upload_view
    return render(request, 'core/upload.html')

@login_required(login_url='/login/')
def jobs(request):
    return render(request, 'core/jobs.html')

@login_required(login_url='/login/')
def profile(request):
    return render(request, 'core/profile.html')

@login_required(login_url='/login/')
def preferences(request):
    return render(request, 'core/preferences.html')

@login_required(login_url='/login/')
def analysis(request):
    context = {}
    try:
        from .models import UserProfile
        profile = UserProfile.objects.get(user=request.user)
        # Prepare data for frontend hydration
        context['user_profile_data'] = json.dumps({
            'resumeName': os.path.basename(profile.resume.name) if profile.resume else None,
            'skills': profile.skills,
            'atsScore': profile.ats_score,
            'atsBreakdown': profile.ats_breakdown,
            'uploadedAt': profile.uploaded_at.isoformat() if profile.uploaded_at else None
        })
    except UserProfile.DoesNotExist:
        context['user_profile_data'] = 'null'
    return render(request, 'core/analysis.html', context)

@login_required(login_url='/login/')
def application_view(request):
    return render(request, 'core/application.html')

@login_required(login_url='/login/')
@csrf_exempt
def submit_application_view(request):
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            cover_letter = request.POST.get('cover_letter')
            linkedin = request.POST.get('linkedin', '')
            portfolio = request.POST.get('portfolio', '')
            job_id = request.POST.get('job_id')
            job_title = request.POST.get('job_title')
            job_company = request.POST.get('job_company')
            
            # Handle resume file upload
            resume_file = request.FILES.get('resume')
            
            if not all([full_name, email, phone, cover_letter, resume_file]):
                return JsonResponse({'error': 'All required fields must be filled'}, status=400)
            
            # Save resume file
            file_path = default_storage.save(f'applications/{resume_file.name}', resume_file)
            
            # In a real application, you would save this to a database
            # For now, we'll just log it and return success
            print(f"Application received:")
            print(f"  Job: {job_title} at {job_company}")
            print(f"  Applicant: {full_name} ({email})")
            print(f"  Resume: {file_path}")
            print(f"  Cover Letter: {cover_letter[:100]}...")
            
            return JsonResponse({
                'success': True,
                'message': 'Application submitted successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from .models import SavedJob
from .utils import translate_text

@login_required(login_url='/login/')
@csrf_exempt
def save_job_view(request):
    """API endpoint to save or unsave a job"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_id = data.get('job_id')
            action = data.get('action')  # 'save' or 'unsave'
            
            if not job_id:
                return JsonResponse({'error': 'Job ID is required'}, status=400)
            
            if action == 'save':
                # Get job details from request
                job_title = data.get('job_title', '')
                company = data.get('company', '')
                location = data.get('location', '')
                description = data.get('description', '')
                redirect_url = data.get('redirect_url', '')
                salary = data.get('salary', '')
                posted_date = data.get('posted_date', '')
                
                # Create or get saved job
                saved_job, created = SavedJob.objects.get_or_create(
                    user=request.user,
                    job_id=job_id,
                    defaults={
                        'job_title': job_title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'redirect_url': redirect_url,
                        'salary': salary,
                        'posted_date': posted_date
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Job saved successfully',
                    'saved': True
                })
            
            elif action == 'unsave':
                # Delete saved job
                SavedJob.objects.filter(user=request.user, job_id=job_id).delete()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Job removed from saved list',
                    'saved': False
                })
            
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required(login_url='/login/')
def get_saved_jobs_view(request):
    """API endpoint to get all saved jobs for the current user"""
    try:
        saved_jobs = SavedJob.objects.filter(user=request.user)
        
        jobs_data = []
        for saved_job in saved_jobs:
            jobs_data.append({
                'id': saved_job.job_id,
                'title': saved_job.job_title,
                'company': saved_job.company,
                'location': saved_job.location,
                'description': saved_job.description,
                'redirect_url': saved_job.redirect_url,
                'salary': saved_job.salary,
                'postedDate': saved_job.posted_date,
                'saved_at': saved_job.saved_at.isoformat(),
                'saved': True
            })
        
        return JsonResponse({
            'success': True,
            'jobs': jobs_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url='/login/')
def saved_jobs_page(request):
    """Render saved jobs page"""
    return render(request, 'core/saved_jobs.html')

@csrf_exempt
def translate_job_view(request):
    """API endpoint to translate job description"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            target_language = data.get('target_language', 'hi')  # Default to Hindi
            
            if not text:
                return JsonResponse({'error': 'Text is required'}, status=400)
            
            translated_text = translate_text(text, target_language)
            
            return JsonResponse({
                'success': True,
                'translated_text': translated_text,
                'target_language': target_language
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


