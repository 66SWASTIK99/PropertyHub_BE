from django.urls import path
from .import views

urlpatterns = [
    path('signup/', views.user_signup_view, name='signupapi'),
    path('login/', views.user_login_view,name='loginapi'),
    path('forgetpw/',views.ForgetpwAPI.as_view(),name='forgetpwapi')
]