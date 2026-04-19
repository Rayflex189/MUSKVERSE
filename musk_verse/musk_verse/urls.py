from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('verify-otp/', TemplateView.as_view(template_name='verify_otp.html'), name='verify_otp'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('profile-setup/', TemplateView.as_view(template_name='profile_setup.html'), name='profile_setup'),
    path('marketplace/', TemplateView.as_view(template_name='marketplace.html'), name='marketplace'),
    path('transactions/', TemplateView.as_view(template_name='transaction_history.html'), name='transactions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
