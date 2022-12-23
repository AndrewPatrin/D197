from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView


from .views import BaseRegisterView, login_user, logout_user, accountActivate, account

urlpatterns = [
    path('login/',
        login_user,
        name='login'),
    path('logout/',
         logout_user,
         name='logout'),
    path('signup/',
         BaseRegisterView.as_view(template_name='user/signup.html'),
         name='signup'),
    path('activate/',
         accountActivate,
         name='activate'),
    path('account/',
         account,
         name='account'),
]