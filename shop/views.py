from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.template import defaultfilters as df
from django.conf import settings
from django.db import models
from django_countries import countries
from decimal import Decimal
from sendfile import sendfile
from .models import *
from .decorators import *
from . import cryptomethods as cm
import re, json, qrcode, pyotp
from PIL import Image

# Create your views here.
def view_product(request, id):
	product = get_object_or_404(Product, id=id)
	if request.user.is_authenticated:
		cart = Cart.objects.get(user=request.user)
		return render(request, "shop/product.html", {'product': product, 'incart': cart.in_cart(product), 'can_buy': request.user.userextra.can_purchase_item(product)})
	return render(request, "shop/product.html", {'product': product})

@login_required
def view_cart(request):
	return render(request, "shop/cart.html")

@login_required
def add_to_cart(request, id):
	cart = request.user.cart
	product = get_object_or_404(Product, id=id)
	if request.user.userextra.can_purchase_item(product):
		if product.in_stock():
			if cart.in_cart(product):
				messages.warning(request, "Product is already in cart. Maybe you meant to change the quantity?")
			else:
				ce = CartEntry(product=product, cart=cart)
				ce.save()
				messages.success(request, "Product added to cart!")
		else:
			messages.warning(request, "Product is out of stock. Stop trying to cheat!")
	else:
		messages.warning(request, "You already own this!")
	return redirect(product)

@login_required
def remove_cart(request, id):
	u = request.user
	entry = get_object_or_404(CartEntry, id=id)
	if entry.cart.user == u:
		messages.success(request, 'Removed %s from cart!' % entry.product.product_name)
		entry.delete()
	if 'next' in request.GET and request.GET['next'] != '':
		return redirect(request.GET['next'])
	else:
		return redirect('shop:cart')

def login_view(request):
	if request.method == 'POST':
		if 'username' in request.POST and 'password' in request.POST:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)

			if user is not None:
				if not hasattr(user, 'userextra'):
					ue = UserExtra(user=user)
					ue.save()
				if user.userextra.verified:
					if user.userextra.verify_2fa(request.POST.get('2facode', '')):
						login(request, user)
						messages.success(request, "Welcome back, %s!" % user.username)

						# If user has no cart, give them one.
						if not hasattr(user, 'cart'):
							cart = Cart(user=user)
							cart.save()
						if user.wallet_set.count() <= 0:
							w = Wallet(label='default', user=user)
							w.save()
						if 'next' in request.GET and request.GET['next'] != '':
							return redirect(request.GET['next'])
						else:
							return redirect('/')
					else:
						messages.warning(request, "Incorrect 2FA code.")
				else:
					messages.warning(request, "Email hasn't been verified yet! A new verification email has been sent.")
					send_confirmation_email(user)
			else:
				messages.warning(request, 'Invalid username/password!')

	return render(request, 'shop/login.html')

# Helper function!
def validateEmail( email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def register_view(request):
	if request.method == 'POST':
		if 'username' in request.POST and \
			'password' in request.POST and \
			'passwordconfirm' in request.POST and \
			'email' in request.POST:
			username = request.POST['username'].strip()
			password = request.POST['password']
			passwordconfirm = request.POST['passwordconfirm']
			email = request.POST['email'].strip()

			errors = []
			if re.match('^[\w-]+$', username) is None or \
				len(username) > 150 or \
				username == '':
				errors.append('Invalid username!')
			if len(password) < 8:
				errors.append("Password must be at least 8 characters long")
			if password != passwordconfirm:
				errors.append('Passwords don\'t match')
			if not validateEmail(email):
				errors.append('Invalid email!')
			if User.objects.filter(username=username).count() > 0:
				errors.append('Username is already in use!')
			if User.objects.filter(email=email).count() > 0:
				errors.append('Email is already in use!')

			for e in errors:
				messages.warning(request, e)

			if len(errors) == 0:
				messages.success(request, 'User registered! Please check your email to complete your verification.')
				u = User.objects.create_user(username, email, password)
				send_confirmation_email(u)
				if 'next' in request.GET and request.GET['next'] != '':
					return redirect(request.GET['next'])
				else:
					return redirect('shop:login')

	return render(request, 'shop/register.html')

def logoutview(request):
	if request.user.is_authenticated:
		messages.success(request, "See you next time!")
	logout(request)
	if 'next' in request.GET and request.GET['next'] != '':
		return redirect(request.GET['next'])
	else:
		return redirect('/')

def verify_email(request, uuid):
	verify = get_object_or_404(VerifyEmail, verify_url=uuid)
	if verify.valid:
		verify.valid = False
		if not hasattr(verify.user, 'userextra'):
			ue = UserExtra(user=verify.user)
			ue.save()
		verify.user.userextra.verified = True
		verify.user.userextra.save()
		verify.save()
		messages.success(request, 'You can now log in.')
	else:
		messages.warning(request, 'This verification link is no longer valid.')
	return redirect('shop:login')

@login_required
@auth_required(forid='wallets')
def wallets(request):
	wallets = request.user.wallet_set.filter(active=True)
	return render(request, 'shop/wallets.html',  {'wallets': wallets})


@login_required
@csrf_exempt
@auth_required_api(forid='wallets', goto='/me/wallets')
def api_newwallet(request):
	response = {'status':""}
	errors = []
	if request.method == 'POST' and 'wallet_name' in request.POST:
		if len(request.POST['wallet_name'])>30:
			response['status'] = 'error'
			errors.append('Wallet name has to be 30 characters or less.')
	else:
		response['status'] = 'error'
		errors.append('Malformed request')

	if response['status'] == 'error':
		response['errors'] = errors
	else:
		w = Wallet(user=request.user, label=request.POST['wallet_name'])
		w.save()
		_ = {
			'label': w.label,
			'address': w.address,
			'balance': w.get_balance(),
			'pending': w.get_pending(),
			'totalbal': request.user.userextra.get_balance(),
			'totalpend': request.user.userextra.get_pending(),
			'id': w.id,
		}
		response['wallet'] = _
		response['status'] = 'success'

	return JsonResponse(response)

@login_required
@csrf_exempt
@auth_required_api(forid='wallets', goto='/me/wallets')
def api_send(request):
	response = {}
	errors = []
	if request.method == 'POST' and 'wallet' in request.POST and \
		'address' in request.POST and \
		'ammount' in request.POST:
		try:
			ammount = Decimal(request.POST['ammount'])
			try:
				wallet = Wallet.objects.get(id=int(request.POST['wallet']), user=request.user)
				r = wallet.send_to(request.POST['address'], ammount)
				if r['status'] == 'error':
					errors += r['errors']
			except:
				errors.append('Wallet not found')
		except:
			errors.append('Invalid ammount')
	else:
		errors.append('Malformed request')

	if len(errors) > 0:
		response['status'] = 'error'
		response['errors'] = errors
	else:
		response['status'] = 'success'
		response['wallets'] = []
		for wallet in request.user.wallet_set.filter(active=True):
			response['wallets'].append({
				'balance': wallet.get_balance(),
				'pending': wallet.get_pending(),
				'address': wallet.address,
				'label': wallet.label,
				'id': wallet.id,
				})
		response['balance'] = request.user.userextra.get_balance()
		response['pending'] = request.user.userextra.get_pending()

	return JsonResponse(response)

def api_checkaddress(request):
	response = {'status':""}
	errors = []
	if 'address' in request.GET:
		validate = cm.validateaddress(request.GET['address'])

		if validate['isvalid']:
			response['valid'] = True
			if Wallet.objects.filter(address=request.GET['address']).count()>0:
				response['type'] = 'site'
			else:
				response['type'] = 'external'
		else:
			response['valid'] = False
	else:
		errors.append('Malformed request')
	if len(errors) > 0:
		response['status'] = 'error'
		response['errors'] = errors
	else:
		response['status'] = 'success'
	return JsonResponse(response)

@login_required
def my_settings(request):
	return render(request, 'shop/settings.html')

@login_required
@auth_required(forid='checkout')
def checkout(request):
	if request.user.cart.has_something_in_stock():
		if request.POST.get('checkout', False) and request.user.checkout_set.filter(uuid=request.POST.get('checkout', '')).count() >= 1:
			chkout = request.user.checkout_set.get(uuid=request.POST.get('checkout'))
			if chkout.step == 0:
				if request.POST.get('shipping', False) and request.user.physicaladdress_set.filter(id=request.POST.get('shipping', 0)).count() >= 1:
					chkout.shipping = request.user.physicaladdress_set.get(id=request.POST.get('shipping', 0))
					chkout.step = 1
					for item in chkout.cart.cartentry_set.all():
						t = False
						if not item.product.ships_to(chkout.shipping):
							messages.warning(request, "%s doesn\'t ship to the selected address! Please fix your order and try again." % (item.product.product_name))
							t = True
						if t:
							return redirect('shop:cart')
				elif 'use_custom_address' in request.POST and 'zip' in request.POST and 'address1' in request.POST and 'country' in request.POST and 'state' in request.POST and 'name' in request.POST:
					print('ddd')
					if 0 < len(request.POST['zip'].strip()) <= 15 and 0 < len(request.POST['name'].strip()) <= 200 and request.POST['address1'].strip() != '' and request.POST['country'].strip() in dict(countries) and request.POST['state'].strip() != '':
						a = PhysicalAddress(user=request.user, zipcode=request.POST['zip'], address1=request.POST['address1'], name=request.POST['name'], country=request.POST['country'], state=request.POST['state'])
						if request.POST.get('address2', '').strip() != '':
							a.address2 = request.POST['address2']
						a.save()
						chkout.shipping = a
						chkout.step = 2
					else:
						messages.warning(request, "Please properly fill out all required fields")
				else:
					messages.warning(request, "Please fill out all required fields")
			elif chkout.step == 1 and (not chkout.cart.has_physical_items() or hasattr(chkout, 'shipping')):
				if request.POST.get('address', False) and request.user.wallet_set.filter(id=request.POST.get('address', 0)).count() >= 1:
					chkout.wallet = request.user.wallet_set.get(id=request.POST.get('address', 0))
					chkout.step = 2
			elif chkout.step == 2 and 'confirm' in request.POST and (not chkout.cart.has_physical_items() or hasattr(chkout, 'shipping')) and hasattr(chkout, 'wallet') is not None:
				p = chkout.buy()
				chkout.cart.clear()
				messages.success(request, 'Paid!')
				return redirect('shop:purchases')
		else:
			chkout = Checkout(user=request.user, cart=request.user.cart)

		cart = request.user.cart

		if not cart.has_physical_items() and chkout.step==0:
			chkout.step = 1

		if chkout.step >= 1:
			addresses = []
			for address in request.user.wallet_set.filter(active=True):
				if address.get_balance() >= chkout.get_price():
					addresses.append(address)
			print(addresses, len(addresses), chkout.step)

		if chkout.step == 1 and len(addresses) == 1:
			chkout.step = 2
			chkout.wallet = addresses[0]
			print(chkout.wallet)
		elif chkout.step == 1 and len(addresses) == 0:
			messages.warning(request, "Not enough balance!")
			return redirect("shop:cart")

		chkout.save()

		if chkout.step == 0:
			physicaladdresses = request.user.physicaladdress_set.all()
			return render(request, 'shop/checkout1.html', {'addresses': physicaladdresses, 'checkout': chkout})
		elif chkout.step == 1:
			return render(request, 'shop/checkout2.html', {'addresses': addresses, 'checkout': chkout})
		elif chkout.step == 2:
			return render(request, 'shop/checkout3.html', {'checkout': chkout})
	else:
		messages.warning(request, 'Nothing on stock on cart')
		return redirect('shop:cart')

@login_required
def authorize(request, forid):
	if request.method == 'POST' and 'password' in request.POST:
		u = authenticate(username=request.user.username, password=request.POST.get('password', ''))
		if u is not None:
			if u.userextra.verify_2fa(request.POST.get('2facode', '')):
				a = u.userextra.authorize(forid)
				if 'next' in request.GET:
					r = redirect(request.GET['next'])
				else:
					r = redirect('/')
				r.set_signed_cookie('auth_%s' % forid, a.code, max_age=600, salt=u.username)
				return r
			else:
				messages.warning(request, "Wrong 2FA code")
		else:
			messages.warning(request, "Incorrect password.")
	
	return render(request, 'shop/confirmpassword.html')


@login_required
def purchases(request):
	all_purchases = request.user.purchase_set.all().order_by('-date')
	return render(request, 'shop/purchases.html', {'purchases': all_purchases})

@login_required
def keys(request):
	digital_purchases = PurchaseItem.objects.filter(purchase__by=request.user, product__physical=False).order_by('-purchase__date')
	return render(request, 'shop/keys.html', {'purchases': digital_purchases})


def shop(request, user):
	try:
		usershop = get_object_or_404(UserShop, user__username=user)
	except Http404:
		if request.user.username == user:
			return redirect('shop:editshop')
		else:
			raise Http404()

	return render(request, 'shop/shoppage.html', {'shop': usershop})

@login_required
def editshop(request):
	if request.method == 'POST' and hasattr(request.user, 'usershop'):
		if 'description' in request.POST:
			request.user.usershop.description = request.POST['description']
		if 'css' in request.POST and request.user.usershop.can_customcss:
			request.user.usershop.custom_css = request.POST['css']
		if 'address' in request.POST:
			try:
				address = int(request.POST['address'])
				if request.user.wallet_set.filter(id=address).count() > 0:
					request.user.usershop.pay_to_address = request.user.wallet_set.get(id=address)
			except:
				pass
		request.user.usershop.save()
		return redirect('shop:shop', user=request.user.username)
	if not hasattr(request.user, 'usershop'):
		us = UserShop(user=request.user, pay_to_address=request.user.wallet_set.first())
		us.save()
	else:
		us = request.user.usershop
	addresses = request.user.wallet_set.filter(active=True)
	return render(request, 'shop/editshop.html', {'shop': us, 'addresses': addresses})

def homepage(request):
	return render(request, 'shop/base.html')

@login_required
@csrf_exempt
def get_key(request):
	if request.method == 'POST' and 'purchaseid' in request.POST and 'keyid' in request.POST:
		try:
			purchase = PurchaseItem.objects.get(purchase__by=request.user, id=request.POST['purchaseid'])
			key = DigitalKeySet.objects.get(id=request.POST['keyid'], product=purchase.product)
			k = key.take_one(purchase)
			if k is not None:
				return JsonResponse({
					'status': 'success',
					'key': {
						'key': k.key,
						'name': key.name,
						'link': key.is_link,
					}
					})
			else:
				return JsonResponse({'errors': "The seller ran out of keys. Please try again later!"})
		except:
			return JsonResponse({'errors':"Can't find key"})

@login_required
def orders(request):
	order_list = PurchaseItem.objects.filter(purchase__by=request.user, product__physical=True).order_by('-purchase__date')
	return render(request, 'shop/orders.html', {'orders': order_list})

@login_required
def view_order(request, id):
	order = get_object_or_404(PurchaseItem, id=id, purchase__by=request.user)
	if order.product.physical:
		updates = order.shippingupdate_set.all().order_by('-date')
		return render(request, 'shop/vieworder.html', {'order': order, 'updates': updates})
	else:
		raise Http404()

@login_required
def view_purchase(request, uuid):
	purchase = get_object_or_404(Purchase, uuid=uuid, by=request.user)
	return render(request, 'shop/viewpurchase.html', {'purchase': purchase})

@login_required
def download_file(request, id):
	file = get_object_or_404(DigitalFile, id=id)
	if file.owned_by(request.user):
		return sendfile(request, file.file.path, attachment=True, attachment_filename=file.get_file_name())
	else:
		return Http404()

@login_required
def dashboard(request):
	return render(request, 'shop/dashboard.html')

@login_required
def seller_purchases(request):
	inproggress = PurchaseItem.objects.all()\
		.annotate(done=models.Count(models.Case(
			models.When(shippingupdate__done=True,then=1),output_field=models.CharField())))\
		.filter(product__seller=request.user,done=0, product__physical=True)\
		.order_by('-purchase__date')
	doneorders = PurchaseItem.objects.all()\
		.annotate(done=models.Count(models.Case(
			models.When(shippingupdate__done=True,then=1),output_field=models.CharField())))\
		.filter(product__seller=request.user,done__gt=0)\
		.order_by('-purchase__date')

	return render(request, 'shop/sales.html', {'inproggress': inproggress, 'done': doneorders})

@login_required
def manage_order(request, id):
	order = get_object_or_404(PurchaseItem, product__seller=request.user, id=id, product__physical=True)

	if request.method == 'POST':
		if request.POST.get('shortupdate', '').strip() != '':
			errors = []
			if len(request.POST.get('shortupdate', '').strip()) > 200:
				errors.append('Short update must be at most 200 characters')

			if not errors:
				u = ShippingUpdate(purchase=order, short_update=request.POST.get('shortupdate', '').strip(), update=request.POST.get('longupdate', '').strip(), done=request.POST.get('done', 'off') == 'on')
				u.save()
				messages.success(request, "Successfully updated")
				if not u.done:
					send_mail("Update on one of your orders", """Hello %s,

There's a new update for your order of %d %s.

	%s

	%s

Thanks for buying with OKCart!""" % (order.purchase.by, order.quantity, order.product.product_name, u.short_update, u.update), "no_reply@okcart.net", [order.purchase.by.email])
				else:
					send_mail("One of your orders is done", """Hello %s,

Your order for %d %s is done.

	%s

	%s

Thanks for buying with OKCart!""" % (order.purchase.by, order.quantity, order.product.product_name, u.short_update, u.update), "no_reply@okcart.net", [order.purchase.by.email])

			for error in errors:
				messages.warning(request, error)

	updates = order.shippingupdate_set.all().order_by('-date')
	return render(request, 'shop/manageorder.html', {'order': order, 'updates':updates})


def qr_code(request):
	t = request.GET.get('text', '')
	img = qrcode.make(t)
	response = HttpResponse(content_type="image/png")
	img.save(response, "PNG")
	return response


@login_required
@auth_required(forid='2fa')
def auth_settings(request):
	return render(request, 'shop/2fa_settings.html')

@login_required
@auth_required(forid='2fa')
def google_settings(request):
	args = {}
	if request.method == 'POST':
		if 'authcode' in request.POST and request.user.userextra.authenticator_id:
			totp = pyotp.TOTP(request.user.userextra.authenticator_id)
			try:
				authcode = int(request.POST['authcode'])
				if totp.verify(authcode):
					request.user.userextra.authenticator_verified = True
					request.user.userextra.save()
					messages.success(request, "Successfully added google authenticator!")
				else:
					messages.warning(request, "Your code doesn't seem right... Double check it!")
			except:
				messages.warning(request, "Your code doesn't seem right... Double check it!")

	if not request.user.userextra.authenticator_verified:
		request.user.userextra.authenticator_id = pyotp.random_base32()
		request.user.userextra.save()

	totp = pyotp.TOTP(request.user.userextra.authenticator_id)
	args['code'] = totp.provisioning_uri("OKCart: %s" % request.user.username)
	return render(request, 'shop/google_auth.html', args)

@login_required
def sell_new_product(request):
	if request.method == 'POST':
		# Get ready for all the ifs!
		errors = []
		if request.POST.get('product-name', '').strip() == '':
			errors.append("Product name can't be empty!")
		if (not request.POST.get('unlimited', 'off') == 'on'):
			try:
				stock = int(request.POST.get('stock', 0))
				if stock < 0:
					errors.append('Stock has to be at least 0')
			except ValueError:
				errors.append('Stock has to be at least 0')
		try:
			price = Decimal(request.POST.get('price', 0))
			if price < 0:
				errors.append('Price has to be at least 0')
		except ValueError:
			errors.append('Price has to be at least 0')
		try:
			cur = request.POST.get('currency', 'ok').strip()
			rate = cryptonator.get_exchange_rate(cur, 'ok')
		except cryptonator.CryptonatorException:
			errors.append("Currency doesn't exist!")
		if request.POST.get('is-physical', 'on') == 'on':
			if request.POST.get('ships-from', 'US') not in dict(countries):
				errors.append('%s is not a country!' % request.POST.get('ships-from', 'US'))
			if not request.POST.get('worldwide-shipping', 'on') == 'on':
				for country in request.POST.get('countries', []):
					if country not in dict(countries):
						errors.append('%s is not a country!' % country)
			if not request.POST.get('free-shipping', 'off') == 'on':
				try:
					local_shipping = Decimal(request.POST.get('local-price', 0))
					if local_shipping < 0:
						errors.append("Local shipping price must be at least 0")
				except ValueError:
					errors.append("Local shipping price must be at least 0")
				try:
					global_shipping = Decimal(request.POST.get('global-price', 0))
					if global_shipping < 0:
						errors.append("Global shipping price must be at least 0")
				except ValueError:
					errors.append("Global shipping price must be at least 0")
		_imgs = request.POST.getlist('images', [])
		imgs = []
		for img in _imgs:
			try:
				imgs.append(ProductImage.objects.get(uuid=img, product__isnull=True))
			except: pass
		if not imgs:
			errors.append("Please upload at least one image")

		if not errors:
			p = Product(
				product_name=request.POST.get('product-name', '').strip(),
				product_description=request.POST.get('description', '').strip(),
				price=Decimal(request.POST.get('price', 0)),
				price_currency=request.POST.get('currency', 'OK').strip(),
				physical=request.POST.get('is-physical', 'on') == 'on',
				stock=int(request.POST.get('stock', 0)),
				seller=request.user,
				free_shipping=request.POST.get('free-shipping', 'off') == 'on',
				unlimited_stock=request.POST.get('unlimited', 'off') == 'on'
				)
			p.save()
			for i in imgs:
				i.product = p
				i.save()
			if p.physical:
				p.local_price = Decimal(request.POST.get('local-price', 0))
				p.global_price = Decimal(request.POST.get('global-price', 0))
				p.worldwide_shipping = request.POST.get('worldwide-shipping', 'on') == 'on'
				p.ships_from = request.POST.get('ships-from', 'US').strip()
				p.save()
				for country in request.POST.get('countries', []):
					if country not in dict(countries):
						c = ShippingCountry(country=country, product=p)
						c.save()
			p.save()
			messages.success(request, "Added item!")
			return redirect(p)

		for error in errors:
			messages.warning(request, error)
	return render(request, 'shop/newproduct.html')

@csrf_exempt
@login_required
def upload_pic(request):
	response = {'images':[]}
	for pic in request.FILES.getlist('pics'):
		try:
			p = ProductImage(image=pic)
			p.save()
			response['images'].append({'url': p.image.url,'id': p.id, 'delete': p.uuid})
		except:
			pass
	return JsonResponse(response)

@csrf_exempt
@login_required
def delete_pic(request, uuid):
	pic = get_object_or_404(ProductImage, uuid=uuid)
	pic.delete()
	return JsonResponse({'status': 'ok'})

@login_required
def change_password(request):
	if request.method == 'POST':
		errors = []
		curpass = request.POST.get('curpassword', '')

		u = authenticate(username=request.user.username, password=curpass)
		if u is None:
			errors.append("Incorrect password")

		if len(request.POST.get('newpassword', '')) < 8:
			errors.append("Password must be at least 8 characters long")

		if not request.POST.get('newpassword', '') == request.POST.get('confirmnewpass', ''):
			errors.append("Passwords don't match!")

		if request.user.userextra.authenticator_verified:
			if not request.user.userextra.verify_2fa(request.POST.get('2facode', '')):
				errors.append("Google auth code is incorrect")

		if not errors:
			u.set_password(request.POST.get('newpassword', ''))
			u.save()
			messages.success(request, "Changed password!")
			return redirect("shop:settings")

		for error in errors:
			messages.warning(request, error)

	return render(request, 'shop/changepassword.html')

@login_required
def edit_product(request, id):
	product = get_object_or_404(Product, id=id, seller=request.user)
	return render(request, 'shop/editproduct.html', {'product': product})