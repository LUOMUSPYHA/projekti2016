from django.conf.urls import url

from . import views

app_name = 'pyha'
urlpatterns = [
    url(r'^/?$', views.index, name='index'),
    url(r'^login/?$', views.login, name='login'),
    url(r'^logout/?$', views.logout, name='logout'),
    url(r'^index/?$', views.index, name='index'),
    
    url(r'^api/request/?$', views.receiver, name='receiver'),
    url(r'^mock/jsonmock/?$', views.jsonmock, name='jsonmock'),

    url(r'^request/[1-9][0-9]*/?$', views.show_request),
    url(r'^description/?$', views.change_description, name='description'),
    url(r'^role/?', views.change_role, name='change_role'),
    url(r'^approve/?$', views.approve, name='approve'),
    url(r'^answer/?$', views.answer, name='answer'),
    url(r'^removeCollection/?$', views.removeCollection, name='removeCollection')
]
