from django.conf.urls import url
from . import views
urlpatterns = [
url(r'^$', views.index),
url(r'company/(?P<id>\d+)/$', views.display_company),
url(r'company/(?P<id>\d+)/asks$', views.get_asks_for_company),
url(r'company/(?P<id>\d+)/bids$', views.get_bids_for_company),
url(r'company/(?P<id>\d+)/user$', views.get_user_orders_for_company),
url(r'company/(?P<id>\d+)/place_order$', views.place_order),
url(r'orders/(?P<id>\d+)/cancel$', views.cancel_order),
]
