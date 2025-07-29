

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
from django.core.files.storage import default_storage
from .models import Job, Application
from django.http import JsonResponse
from django.http import HttpResponse
from django.db.models import Q



#Job listings page
def job_list(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    context = {
        'jobs': jobs,
        'query': query,
    }
    return render(request, 'job_listings.html', context)
    
        


#Job details page
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_detail.html', {'job': job})


#video upload
def analyze_video_sentiment(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = 0
    brightness = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames += 1
        brightness += np.mean(frame)
    cap.release()
    if frames == 0:
        return "Neutral"
    avg_brightness = brightness / frames
    score = min(100, max(0, (avg_brightness / 2)))  # Scale to 0-100
    if avg_brightness > 120:
        return "Confident" , score
    elif avg_brightness > 80:
        return "Neutral", score
    else:
        return "Low Energy", score



#Apply page
def apply(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        resume = request.FILES.get('resume')
        video_resume = request.FILES.get('video_resume')

        if not name or not email or not resume:
            messages.error(request, "All fields are required.")
            return redirect('apply', job_id=job.id)

        # ✅ Create application instance properly
        application = Application(
            job=job,
            name=name,
            email=email,
            resume=resume,
            video_resume=video_resume
        )

        application = Application.objects.create(
            job=job, name=name, email=email, resume=resume, video_resume=video_resume
        )

        if video_resume:
            video_path = default_storage.save(video_resume.name, video_resume)
            full_path = default_storage.path(video_path)
            sentiment, score = analyze_video_sentiment(full_path)

            application.ai_sentiment = sentiment
            application.ai_score = score
            application.save()


            messages.success(request, f"✅ Video Resume Uploaded - AI Analysis: {sentiment}")

        # ✅ Add success message
        messages.success(request, f"🎉 {name}, your application for '{job.title}' has been submitted successfully!")

        return redirect('success')

    return render(request, 'apply.html', {'job': job})
    

#success page
def success(request):
    return render(request, 'success.html')


#simple chatbot view

def chatbot(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    if 'last_topic' not in request.session:
        request.session['last_topic'] = None

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        chat = request.session['chat_history']
        last_topic = request.session['last_topic']

        bot_response, new_topic = simple_bot_response(user_message, last_topic)

        chat.append({'user': user_message, 'bot': bot_response})
        request.session['chat_history'] = chat
        request.session['last_topic'] = new_topic

    return render(request, 'chatbot.html', {'chat_history': request.session.get('chat_history', [])})


# Context-aware bot response
def simple_bot_response(message, last_topic):
    message = message.lower()

    # Handle "yes" or "no" based on last topic
    if message == "yes" and last_topic == "interview_tips":
        return ("Here are 5 common interview questions:\n"
                "1️⃣ Tell me about yourself.\n"
                "2️⃣ Why should we hire you?\n"
                "3️⃣ Describe a challenge you overcame.\n"
                "4️⃣ What are your strengths and weaknesses?\n"
                "5️⃣ Where do you see yourself in 5 years?", None)

    if message == "yes" and last_topic == "resume_format":
        return ("📄 Resume Format:\n- Name & Contact Info\n- Summary\n- Skills\n- Experience\n- Education\n"
                "Would you like me to generate a sample PDF?", None)

    if message == "yes" and last_topic == "track_status_link":
        return ("🔗 Here’s the link to track your application: /track-status/", None)

    # Greetings
    if any(word in message for word in ["hi", "hello", "hey"]):
        return ("👋 Hi there! I can help with jobs, applications, resumes, and interview tips. What do you need help with?", None)

    # Job openings
    if "job" in message or "openings" in message:
        return ("💼 We have job openings! Do you want me to show categories or all jobs?", None)

    # Resume tips
    if "resume" in message:
        return ("📄 Resume Tip: Keep it short and highlight achievements. Want me to share a sample format?", "resume_format")

    # Status tracking
    if "status" in message or "track" in message:
        return ("📊 You can track your application status. Should I give you the link?", "track_status_link")

    # Interview tips
    if "interview" in message or "prepare" in message:
        return ("🎤 Interview Tip: Research the company and practice answers. Want me to share common interview questions?", "interview_tips")
           

    #landing page
def landing(request):
    return render(request, 'landing.html')    


# ✅ Signup Page
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Auto login after signup
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('job_list')

    return render(request, 'signup.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('job_list')  # Redirect to job listings after login
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


def track_status(request):
    stages = ['applied', 'reviewed', 'interview', 'offered', 'rejected']
    application = None
    current_stage = 0
    email = ""

    if request.method == "POST":
        email = request.POST.get('email')
        if email:
            try:
                application = Application.objects.filter(email=email).latest('applied_at')
                status_value = application.status.lower()
                if status_value in stages:
                    current_stage = stages.index(status_value)
                else:
                    current_stage = 0
            except Application.DoesNotExist:
                return render(request, 'track_status.html', {
                    'error': "No applications found for this email.",
                    'application': None
                })

    return render(request, 'track_status.html', {
        'application': application,
        'stages': stages,
        'current_stage': current_stage,
        'email': email,
    })

#hr review
def hr_review(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'hr_review.html', {'application': application})

#voice implementation
def voice_apply(request):
    job_title = request.GET.get("title", "")
    job = Job.objects.filter(title__icontains=job_title).first()

    if job:
        messages.success(request, f"Redirecting to apply for {job.title}.")
        return redirect('apply', job_id=job.id)
    else:
        messages.error(request, f"No job found matching '{job_title}'. Try again.")
        return redirect('job_list')
