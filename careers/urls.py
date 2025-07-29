from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('apply/<int:job_id>/', views.apply, name='apply'),
    path('success/', views.success, name='success'), 
    path('chatbot/', views.chatbot, name='chatbot'),
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('track-status/', views.track_status, name='track_status'),
    path('hr-review/<int:application_id>/', views.hr_review, name='hr_review'),
    path('voice-apply/', views.voice_apply, name='voice_apply'),

]
