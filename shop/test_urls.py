from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^', include('shop.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
