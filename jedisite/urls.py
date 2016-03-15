from django.conf.urls import url, include
from jedisite import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile/settings/$', views.user_settings, name='user_settings'),
    url(r'^profile/accounts/$', views.user_accounts, name='user_accounts'),
    url(r'^profile/decks/$', views.user_decks, name='user_decks'),
    url(r'^delete_account/$', views.delete_account, name='delete_account'),
    url(r'^update_postdata/$', views.update_postdata, name='update_postdata'),
    url(r'^owned_cards/$', views.get_owned_cards, name='owned_cards'),
    url(r'^benchmarks/$', views.benchmarks, name='benchmarks'),
    url(r'^war-ranks/$', views.ranks_war, name='ranks_war'),
    url(r'^members/$', views.members, name='members'),
    url(r'^accounts/$', views.accounts_list, name='accounts'),
    url(r'^open_canvas/$', views.open_canvas, name='open_canvas'),
    url(r'^gauntlets/$', views.gauntlets, name='gauntlets'),
    url(r'^deckslist/$', views.deckslist, name='deckslist'),
    url(r'^auth/$', views.force_auth, name='force_auth'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
