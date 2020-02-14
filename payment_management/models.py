from django.db import models
from user_management.models import CustomUser
import uuid


class Course(models.Model):
    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_name = models.CharField(max_length=252)
    course_description = models.CharField(max_length=252, blank=True)


class CourseProvidedByTeacher(models.Model):
    course_teacher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teaching_fee = models.IntegerField(default=1500), # Per Enrolment Per Month


class StudentEnrolledToCourse(models.Model):
    enrollment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course_teacher = models.ForeignKey(CourseProvidedByTeacher, on_delete=models.CASCADE)
    month_enroled_form = models.DateField(auto_now=True) # Starting Month Of the course
    enrolled_till = models.DateField(blank=True, null=True)
    # To confirm Student is still taking the course
    is_active = models.BooleanField(default=True)
    # To store the feedback/Reason at the time of delisting th course
    feedback = models.TextField(blank=True)


class PaymentHistory(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course_teacher = models.ForeignKey(CourseProvidedByTeacher, on_delete=models.CASCADE)
    paid_for_start_date = models.DateField()
    paid_for_end_date = models.DateField()
    success = models.BooleanField()
    # Below two fields are for calculating fee for this course (in future)
    total_amount_paid_during_transaction = models.IntegerField()
    total_number_of_courses_paid_for = models.IntegerField()
