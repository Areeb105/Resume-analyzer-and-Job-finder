from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('core/upload/', views.upload_view, name='upload_api'),
    path('core/jobs/', views.get_jobs_view, name='get_jobs_api'),
    path('core/submit-application/', views.submit_application_view, name='submit_application_api'),
    path('core/save-job/', views.save_job_view, name='save_job_api'),
    path('core/saved-jobs/', views.get_saved_jobs_view, name='get_saved_jobs_api'),
    path('core/translate/', views.translate_job_view, name='translate_job_api'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_page, name='upload_page'),
    path('jobs/', views.jobs, name='jobs'),
    path('saved-jobs/', views.saved_jobs_page, name='saved_jobs'),
    path('profile/', views.profile, name='profile'),
    path('preferences/', views.preferences, name='preferences'),
    path('analysis/', views.analysis, name='analysis'),
    path('application/', views.application_view, name='application'),
]


