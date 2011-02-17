from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from pysession.admin import site
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pysession.views.home', name='home'),
    # url(r'^pysession/', include('pysession.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'views.index'),			   
    (r'^(?P<pk>\d+)$', 'snippits.views.snippit'),
    (r'^new/$', 'snippits.views.paste'),
    url(r'^admin/', include(site.urls)),
)
