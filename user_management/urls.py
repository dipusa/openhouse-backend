from django.conf.urls import url
from user_management import views as views


urlpatterns = [
    url(r'^api/login/$', views.LoginView.as_view()),
]