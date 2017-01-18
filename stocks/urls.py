from django.conf.urls import url, include 
from django.contrib import admin 
urlpatterns = [
url(r'trading/', include('apps.trading.urls')), 
url(r'', include('apps.users.urls')) # And now we use include to pull in our first_app.urls... 
] 
