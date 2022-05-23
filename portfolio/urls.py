"""portfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.urls import path

import about.views
from portfolio.settings import FUNCTION_APP_PATH, STATIC_URL, STATIC_ROOT

urlpatterns = [
    path(FUNCTION_APP_PATH + '/', about.views.Profile.as_view(), name='profile'),
    path(FUNCTION_APP_PATH + '/profile/', about.views.Profile.as_view(), name='profile'),
    path(FUNCTION_APP_PATH + '/download_resume/', about.views.DownloadResume.as_view(), name='download_resume')
]

urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
