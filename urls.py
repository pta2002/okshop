from django.conf.urls import url
from . import views

app_name='shop'
urlpatterns = [
	url(r'^$', views.homepage, name='homepage'),
	url(r'^product/(?P<id>\d*[1-9]\d*)/addtocart/$', views.add_to_cart, name='addtocart'),
	url(r'^product/(?P<id>\d*[1-9]\d*)/$', views.view_product, name='viewproduct'),
	url(r'^shop/(?P<user>[A-Za-z0-9\-\_]{1,150})/$', views.shop, name='shop'),
	url(r'^me/cart/$', views.view_cart, name='cart'),
	url(r'^me/cart/remove/(?P<id>\d*[1-9]\d*)/$', views.remove_cart, name='removecart'),
	url(r'^me/cart/checkout/$', views.checkout, name='checkout'),
	url(r'^me/shop/edit/$', views.editshop, name='editshop'),
	url(r'^me/wallets/$', views.wallets, name='wallets'),
	url(r'^me/settings/$', views.my_settings, name='settings'),
	url(r'^me/purchases/$', views.purchases, name='purchases'),
	url(r'^me/purchases/keys/$', views.keys, name='keys'),
	url(r'^me/purchases/keys/download/(?P<id>\d*[1-9]\d*)/$', views.download_file, name='download'),
	url(r'^me/purchases/orders/$', views.orders, name='orders'),
	url(r'^me/purchases/orders/(?P<id>\d*[1-9]\d*)/$', views.view_order, name='vieworder'),
	url(r'^me/purchases/(?P<uuid>[A-Za-z0-9\-\_]{36})/$', views.view_purchase, name='purchase'),
	url(r'^me/dashboard/$', views.dashboard, name='dashboard'),
	url(r'^accounts/login/$', views.login_view, name='login'),
	url(r'^accounts/register/$', views.register_view, name='register'),
	url(r'^accounts/logout/$', views.logoutview, name='logout'),
	url(r'^accounts/authorize/(?P<forid>[A-Za-z0-9\-\_]{1,32})/$', views.authorize, name='authorize'),
	url(r'^accounts/verify/(?P<uuid>[^/]+)/$', views.verify_email, name='verifyemail'),
	url(r'^api/wallets/newwallet/$', views.api_newwallet, name='apinewwallet'),
	url(r'^api/wallets/checkaddress/$', views.api_checkaddress, name='apicheckaddress'),
	url(r'^api/wallets/send/$', views.api_send, name='apisend'),
	url(r'^api/keys/get/$', views.get_key, name='getkey'),
]
