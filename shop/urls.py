from django.conf.urls import url
from . import views

app_name = 'shop'
urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^all/(?P<page>\d*[1-9]\d*/)?$', views.view_all, name='all'),
    url(r'^search/(?P<page>\d*[1-9]\d*/)?$', views.search, name='search'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/$', views.view_product,
        name='viewproduct'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/reviews/(?P<reviewid>\d*[1-9]\d*)'
        r'/delete/$', views.review_delete, name='deletereview'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/reviews/$', views.view_reviews,
        name='reviews'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/addtocart/$', views.add_to_cart,
        name='addtocart'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/edit/$', views.edit_product,
        name='editproduct'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/edit/files/$', views.edit_keys,
        name='editkeys'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/edit/files/key/'
        r'(?P<keyid>\d*[1-9]\d*)?/?$', views.manage_keyset, name='managekey'),
    url(r'^product/(?P<id>\d*[1-9]\d*)/edit/keys/upload/$',
        views.upload_file_noapi, name='uploadfilenoapi'),
    url(r'^shop/(?P<user>[A-Za-z0-9\-\_]{1,150})/$', views.shop, name='shop'),
    url(r'^me/cart/$', views.view_cart, name='cart'),
    url(r'^me/cart/remove/(?P<id>\d*[1-9]\d*)/$', views.remove_cart,
        name='removecart'),
    url(r'^me/cart/checkout/$', views.checkout, name='checkout'),
    url(r'^me/shop/edit/$', views.editshop, name='editshop'),
    url(r'^me/wallets/$', views.wallets, name='wallets'),
    url(r'^me/settings/$', views.my_settings, name='settings'),
    url(r'^me/settings/account/changepassword/$', views.change_password,
        name='changepassword'),
    url(r'^me/settings/2fa/$', views.auth_settings, name='2fasettings'),
    url(r'^me/settings/2fa/google/$', views.google_settings,
        name='googlesettings'),
    url(r'^me/purchases/$', views.purchases, name='purchases'),
    url(r'^me/purchases/keys/$', views.keys, name='keys'),
    url(r'^me/purchases/keys/download/(?P<id>\d*[1-9]\d*)/$',
        views.download_file, name='download'),
    url(r'^me/purchases/orders/$', views.orders, name='orders'),
    url(r'^me/purchases/orders/(?P<id>\d*[1-9]\d*)/$', views.view_order,
        name='vieworder'),
    url(r'^me/purchases/(?P<uuid>[A-Za-z0-9\-\_]{36})/$', views.view_purchase,
        name='purchase'),
    url(r'^me/dashboard/$', views.dashboard, name='dashboard'),
    url(r'^me/dashboard/sales/$', views.seller_purchases, name='sales'),
    url(r'^me/dashboard/sales/(?P<id>\d*[1-9]\d*)/$', views.manage_order,
        name='manageorder'),
    url(r'^me/dashboard/new/$', views.sell_new_product, name='sellproduct'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/register/$', views.register_view, name='register'),
    url(r'^accounts/logout/$', views.logoutview, name='logout'),
    url(r'^accounts/authorize/(?P<forid>[A-Za-z0-9\-\_]{1,32})/$',
        views.authorize, name='authorize'),
    url(r'^accounts/verify/(?P<uuid>[^/]+)/$', views.verify_email,
        name='verifyemail'),
    url(r'^api/wallets/newwallet/$', views.api_newwallet, name='apinewwallet'),
    url(r'^api/wallets/checkaddress/$', views.api_checkaddress,
        name='apicheckaddress'),
    url(r'^api/wallets/send/$', views.api_send, name='apisend'),
    url(r'^api/keys/get/$', views.get_key, name='getkey'),
    url(r'^api/qrcode/$', views.qr_code, name='qrcode'),
    url(r'^api/uploadpic/$', views.upload_pic, name='uploadpic'),
    url(r'^api/deletepic/(?P<uuid>[A-Za-z0-9\-\_]{36})/$', views.delete_pic,
        name='deletepic'),
    url(r'^api/uploadfile/(?P<id>\d*[1-9]\d*)/$', views.upload_file,
        name='uploadfile'),
    url(r'^api/deletefile/(?P<id>\d*[1-9]\d*)/$', views.delete_file,
        name='deletefile'),
    url(r'^api/vote/(?P<id>\d*[1-9]\d*)/(?P<vote>up|down)', views.toggle_vote,
        name='togglevote'),
]
