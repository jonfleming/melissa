from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from info.views import ChatterBotAppView, ChatterBotApiView

app_name = 'info'
urlpatterns = [
    path('', ChatterBotAppView.as_view(), name='info'),
    #path('api/chatterbot/', ChatterBotApiView.as_view(), name='chatterbot'),
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    #url(r'^$', ChatterBotAppView.as_view(), name='info'),
    #url(r'^info/', ChatterBotAppView.as_view(), name='info'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^api/chatterbot/', ChatterBotApiView.as_view(), name='chatterbot'),
]
