from django.test import TestCase
from .models import Job, Application

class JobModelTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(title="Test Job", description="Test description", location="Remote")

    def test_job_creation(self):
        self.assertEqual(self.job.title, "Test Job")
        self.assertEqual(str(self.job), "Test Job")

class ApplicationModelTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(title="Developer", description="Dev Job", location="Remote")
        self.application = Application.objects.create(
            job=self.job,
            name="John Doe",
            email="john@example.com",
            resume="resumes/test_resume.pdf"
        )

    def test_application_creation(self):
        self.assertEqual(self.application.name, "John Doe")
        self.assertEqual(str(self.application), "John Doe - Developer")
