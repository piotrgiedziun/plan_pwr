from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='base.html')),

    # Examples:
    # url(r'^$', 'touristnavi.views.home', name='home'),
    # url(r'^touristnavi/', include('touristnavi.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
