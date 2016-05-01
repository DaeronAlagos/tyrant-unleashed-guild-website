from django.conf.urls import url, include
from conquest import views

urlpatterns = [
    url(r'^overview/$', views.conquest_overview, name='conquest_overview'),
    url(r'^command/$', views.command, name='command'),
]
