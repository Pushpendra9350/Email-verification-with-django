from django.urls import path
from .views import * 
urlpatterns = [
    path('', home, name='home'),
    path('login', login_user, name='login'),
    path('register', register, name='register'),
    path('tokensent', send_token, name='send_token'),
    path('success', success, name='success'),
    path('verify/<auth_token>', verify, name='verify'),
    path('error', error_page, name='error'),
    path('logout', logout_user, name='logout')
]