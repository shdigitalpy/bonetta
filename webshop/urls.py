from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

def custom_page_not_found(request):
    return django.views.defaults.page_not_found(request, None)

def custom_server_error(request):
    return django.views.defaults.server_error(request)

urlpatterns = [
	path("404/", custom_page_not_found),
	path("500/", custom_page_not_found),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('store.urls', namespace='store')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
