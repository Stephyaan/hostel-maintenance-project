"""
URL configuration for hostel_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.shortcuts import render

def serve_frontend(request, path):
    # If anyone asks for index.html inside a subfolder (usually due to relative logout redirects),
    # serve the main login page from the root.
    if path.endswith('index.html'):
        return render(request, 'index.html')
    
    # Otherwise, try to serve the specifically requested HTML file.
    return render(request, path)

urlpatterns = [
    re_path(r'^(?P<path>.*\.html)$', serve_frontend),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
]
