from django.conf.urls import url

from . import views

app_name = 'crawler'
urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name='index'),
    #url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    #url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    #url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    #url(r'^test$', views.test, name='test'),
    url(r'^$', views.index, name='index'),
    url(r'^create_source$', views.create_source, name='create_source'),
    url(r'^refresh$', views.refresh , name='refresh'),
    url(r'^list_sources$', views.list_sources, name='list_sources'),
    url(r'^show_source/(?P<id>[0-9]+)/$', views.show_source, name='show_source'),
    url(r'^edit_source/(?P<id>[0-9]+)/$', views.edit_source, name='edit_source'),
    url(r'^list_endpoints/(?P<source_id>[0-9]+)/$', views.list_endpoints, name='list_endpoints'),
    #url(r'^$', views.index, name='index'),
    #url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    #url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    #url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
]
