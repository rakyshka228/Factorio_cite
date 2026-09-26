from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from factorio_app.views import (
    blueprint_detail,
    create_blueprint,
    home,
    profile,
    register,
    toggle_like,
    user_blueprint_detail,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('blueprint/<slug:slug>/', blueprint_detail, name='blueprint_detail'),
    path('community/blueprint/<int:pk>/', user_blueprint_detail, name='user_blueprint_detail'),
    path('community/blueprint/<int:pk>/like/', toggle_like, name='toggle_like'),
    path('publish/', create_blueprint, name='create_blueprint'),
    path('profile/<str:username>/', profile, name='profile'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
