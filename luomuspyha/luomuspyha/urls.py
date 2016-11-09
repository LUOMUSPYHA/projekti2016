"""luomuspyha URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.i18n import javascript_catalog
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^', include('pyha.urls')),
    url(r'^pyha/', include('pyha.urls')),
    url(r'^login/', include('pyha.urls')),
    url(r'^admin/', admin.site.urls),
    #url(r'^', include('pyyntojarjestelma.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


js_info_dict = {
    'domain': 'djangojs',
    'packages': ('pyha',),
}

urlpatterns += [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict,
      name='javascript-catalog'),
]
