from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1.0.0/',include('app.v1_0_0.urls')),
    path('api/v2.0.0/',include('app.v2_0_0.urls')),
]
