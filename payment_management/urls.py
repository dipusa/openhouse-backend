from django.conf.urls import url
from payment_management import views as views


urlpatterns = [
    url(r'^api/courses_not_enrolled/$', views.CoursesNotEnrolledTillNow.as_view()),
    url(r'^api/enroll_courses/$', views.EnrollCourse.as_view()),
]