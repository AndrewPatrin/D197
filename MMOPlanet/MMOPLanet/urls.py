from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('main.urls'), name='posts'),
    path('summernote/', include('django_summernote.urls')),
    path('', include('signup.urls')),
    path('accounts/', include('allauth.urls')),
    path('', RedirectView.as_view(url='/posts/')),
    path('subscribe/', views.subscribe, name='subscribe'),
]
