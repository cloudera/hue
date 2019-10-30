# from django.urls import re_path # Django 2
from django.conf.urls import url


from notebook import consumer

websocket_urlpatterns = [
    url(r'ws/chat/(?P<room_name>[\w\-]+)/$', consumer.ChatConsumer),
]
