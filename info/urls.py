from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from info.views import ChatterBotAppView, ChatterBotApiView

app_name = 'info'
urlpatterns = [
    path('', ChatterBotAppView.as_view(), name='info'),
    #url('admin/', admin.site.urls, name='admin'),
    url('api/chatterbot/', ChatterBotApiView.as_view(), name='chatterbot'),
]
