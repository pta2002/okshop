import uuid, os

from django.db import models
from django.db.models import F
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
from django_countries.fields import CountryField
from django.conf import settings
from . import cryptomethods as cm
from decimal import Decimal
import cryptonator, pyotp

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "%s.%s" % (uuid.uuid4(), ext)
	return os.path.join('upload', filename)


def get_protected_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "%s.%s" % (uuid.uuid4(), ext)
	return os.path.join('protected', filename)


def send_confirmation_email(user):
	if user.email != '':
		v = VerifyEmail(user=user)
		v.save()
		body = """
		Hello, %s! To complete your registration on OKShop, please verify your email by clicking the following link:
		https://%s%s
		""" % (user.username, getattr(settings, 'URL', 'okcart.net'), reverse('shop:verifyemail', kwargs={'uuid': v.verify_url}))
		send_mail('Complete your OKShop registration!', body, 'no-reply@okcash.net', [user.email])

class Product(models.Model):
	product_name = models.CharField(max_length=140) # If you can't fit your product's name into a tweet you need a better name...
	product_description = models.TextField()
	approved = models.BooleanField(default=True)

	price = models.DecimalField(max_digits=2**16, decimal_places=8)
	price_currency = models.CharField(max_length=16, default='OK')
	cached_rate = models.DecimalField(blank=True, null=True, max_digits=2**16, decimal_places=8)
	rate_lastupdated = models.DateTimeField(default=timezone.now)

	physical = models.BooleanField(default=0)
	stock = models.IntegerField(blank=True,null=True)

	date = models.DateTimeField(default=timezone.now)

	seller = models.ForeignKey(User)

	free_shipping = models.BooleanField(default=False)
	worldwide_shipping = models.BooleanField(default=False)
	ships_from = CountryField(null=True, blank=True)
	local_price = models.DecimalField(max_digits=2**16, decimal_places=8, default=0)
	outside_price = models.DecimalField(max_digits=2**16, decimal_places=8, default=0)

	redeeming_instructions = models.TextField(default='', blank=True, null=True)
	unlimited_stock = models.BooleanField(default=False)

	can_purchase_multiple = models.BooleanField(default=True)

	def __str__(self):
		return self.product_name

	def in_stock(self):
		if self.stock == 0 and not self.unlimited_stock:
			return False
		else:
			return True

	def get_absolute_url(self):
		return reverse('shop:viewproduct', kwargs={'id':self.id})

	def ships_to(self, address):
		if self.worldwide_shipping  or not self.physical:
			return True
		if self.shippingcountry_set.filter(country=address.country[0]).count() >= 1:
			return True
		return False

	def get_shipping_price(self, address=None):
		if self.free_shipping or not self.physical:
			return 0
		if self.ships_from == address.country:
			if self.price_currency != 'OK':
				if not self.cached_rate or timezone.now() - self.rate_lastupdated >= timezone.timedelta(hours=1):
					self.rate_lastupdated = timezone.now()
					self.cached_rate = Decimal(cryptonator.get_exchange_rate(self.price_currency, 'ok'))
					self.save()
				return Decimal(self.cached_rate) * Decimal(self.local_price)
			return self.local_price
		if self.price_currency != 'OK':
			if not self.cached_rate or timezone.now() - self.rate_lastupdated >= timezone.timedelta(hours=1):
				self.rate_lastupdated = timezone.now()
				self.cached_rate = Decimal(cryptonator.get_exchange_rate(self.price_currency, 'ok'))
				self.save()
			return Decimal(self.cached_rate) * Decimal(self.outside_price)
		return self.outside_price

	def buy(self, address, wallet, ammount, gift=False):
		if (self.stock >= ammount or self.unlimited_stock) and self.ships_to(address):
			if getattr(settings, 'FEE_ADDRESS', '') != '':
				wallet.send_to(getattr(settings, 'FEE_ADDRESS', ''), (self.get_shipping_price(address)+self.get_item_price()*ammount)*Decimal(0.005))
				wallet.send_to(self.seller.usershop.pay_to_address.address, (self.get_shipping_price(address)+self.get_item_price()*ammount)*Decimal(0.995))
				fee=0.995
			else:
				wallet.send_to(self.seller.usershop.pay_to_address.address, (self.get_shipping_price(address)+self.get_item_price()*ammount)*1)
				fee=1
			if not self.unlimited_stock: 
				self.stock -= ammount
			self.save()
			send_mail("Someone bought one of your items!", """Hello %s,

The user %s has purchased your product, %s.
We recommend you get in contact with the buyer as fast as possible.

Thanks for selling with OKCart!""" % (self.seller.username, wallet.user.username, self.product_name), "no_reply@okcart.net", [self.seller.email])
			return PurchaseItem(product=self, gift=gift, price=self.get_item_price(), quantity=ammount, shipping_price=self.get_shipping_price(address), address=address, fee=fee)

	def get_earnings(self):
		s = 0
		for p in PurchaseItem.objects.filter(product=self):
			s += p.price
		return s

	def get_purchases(self):
		return PurchaseItem.objects.filter(product=self)

	def get_item_price(self):
		if self.price_currency != 'OK':
			if not self.cached_rate or timezone.now() - self.rate_lastupdated >= timezone.timedelta(hours=1):
				self.rate_lastupdated = timezone.now()
				self.cached_rate = Decimal(cryptonator.get_exchange_rate(self.price_currency, 'ok'))
				self.save()
			return Decimal(self.cached_rate) * Decimal(self.price)
		return self.price

	def update_rates(self):
		self.cached_rate = cryptonator.get_exchange_rate(self.price_currency, 'ok')
		self.save()

	def ships_to_country(self, country):
		return self.shippingcountry_set.filter(country=country[0]).count() > 0

class ShippingCountry(models.Model):
	product = models.ForeignKey(Product)
	country = CountryField()

	class Meta:
		verbose_name_plural = "shipping countries"

	def __str__(self):
		return '%s ships to %s!' % (self.product, self.country)

class ProductImage(models.Model):
	product = models.ForeignKey(Product, blank=True, null=True)
	image = models.ImageField(upload_to=get_file_path)
	uuid = models.CharField(max_length=36,default=uuid.uuid4)

class Cart(models.Model):
	user = models.OneToOneField(User)

	def __str__(self):
		return self.user.username

	def in_cart(self, product):
		for entry in self.cartentry_set.all():
			if entry.product == product:
				return True
				break
		return False

	def gettotal(self):
		p = 0
		for entry in self.cartentry_set.all():
			if entry.in_stock():
				p += entry.gettotal()
		return p
	gettotal.short_description = 'total'

	def get_number_of_items(self):
		return self.cartentry_set.all().count()
	get_number_of_items.short_description = 'number of items'

	def has_physical_items(self):
		return self.cartentry_set.filter(product__physical=True).count() >= 1
	has_physical_items.boolean = True

	def clear(self):
		for entry in self.cartentry_set.all():
			entry.delete()

	def has_something_in_stock(self):
		for item in self.cartentry_set.all():
			if item.in_stock:
				return True
				break
		return False

class CartEntry(models.Model):
	product = models.ForeignKey(Product)
	cart = models.ForeignKey(Cart)
	quantity = models.IntegerField(default=1)
	gift = models.BooleanField(default=False)

	def __str__(self):
		return "%d %s in %s" %  (self.quantity, self.product, self.cart)

	def gettotal(self):
		return self.product.get_item_price() * self.quantity

	def in_stock(self):
		return self.quantity <= self.product.stock or self.product.unlimited_stock
	in_stock.boolean = True

	class Meta:
		verbose_name_plural = 'cart entries'

class VerifyEmail(models.Model):
	user = models.ForeignKey(User)
	verify_url = models.CharField(max_length=32, default=uuid.uuid4, unique=True)
	sent = models.DateTimeField(default=timezone.now)
	valid = models.BooleanField(default=True)

	def __str__(self):
		return '%s: %s' % (self.user, self.verify_url)


class UserExtra(models.Model):
	user = models.OneToOneField(User)
	verified = models.BooleanField(default=False)

	authenticator_id = models.CharField(max_length=16, default='', null=True, blank=True)
	authenticator_verified = models.BooleanField(default=False)

	def authorize(self, forid):
		a = Authorization(user=self.user, allowto=forid)
		a.save()
		return a

	def has_authorization(self, request, forid):
		if 'auth_%s' % forid  not in request.COOKIES:
			return False
		cookie = request.get_signed_cookie('auth_%s' % forid, salt=request.user.username, default='')
		return self.user.authorization_set.filter(valid=True, code=cookie, expires__gt=timezone.now()).count() >= 1

	def __str__(self):
		return self.user.username

	def get_balance(self):
		b = 0
		for w in self.user.wallet_set.filter(active=True):
			b += w.get_balance()
		return b
	get_balance.short_description = 'balance'

	def verify_2fa(self, code):
		if self.authenticator_verified:
			totp = pyotp.TOTP(self.authenticator_id)
			return totp.verify(code)
		return True

	def get_highest_balance_wallet(self):
		b = Wallet(user=self.user,label='')
		for w in self.user.wallet_set.filter(active=True):
			if w.get_balance() > b.get_balance():
				b = w
		return b

	def get_pending(self):
		b = 0
		for w in self.user.wallet_set.filter(active=True):
			b += w.get_pending()
		return b
	get_pending.short_description = 'pending'

	def get_highest_pending_wallet(self):
		b = Wallet(user=self.user,label='',address='')
		for w in self.user.wallet_set.filter(active=True):
			if w.get_pending() > b.get_pending():
				b = w
		return b

	def can_purchase_item(self, item):
		if item.can_purchase_multiple:
			return True

		return PurchaseItem.objects.filter(purchase__by=self.user, product=item).count() == 0

class Wallet(models.Model):
	redeemed = models.DecimalField(max_digits=2**16, decimal_places=8, default=0)
	user = models.ForeignKey(User)
	label = models.CharField(max_length=30)
	active = models.BooleanField(default=True)
	address = models.CharField(max_length=34, default=cm.new_address)

	def __str__(self):
		return '%s: %s' % (self.user.username, self.label)

	def get_balance(self):
		return cm.getreceivedbyaddress(self.address, 3)-self.redeemed

	def get_pending(self):
		return cm.getreceivedbyaddress(self.address, 0)-self.get_balance()-self.redeemed

	def send_to(self, address, ammount):
		response = {}
		errors = []

		if Wallet.objects.filter(address=address).count()>0:
			# Address is in-site, instand+no fees!
			if self.get_balance() - ammount >= 0:
				self.redeemed += ammount
				self.save()

				w = Wallet.objects.get(address=address)
				w.redeemed -= ammount
				w.save()
			else:
				print(self.get_balance(), ammount, self.get_balance() - ammount)
				errors.append('Not enough funds!')
		else:
			if self.get_balance() - ammount - 1 >= 0:
				cm.settxfee(1)
				try:
					cm.sendtoaddress(address, ammount)
					self.redeemed += ammount + 1
					self.save()
				except:
					errors.append("Invalid ammount")
			else:
				errors.append('Not enough funds!')

		if len(errors) > 0:
			response['status'] = 'error'
			response['errors'] = errors
		else:
			response['status'] = 'success'

		return response

class PhysicalAddress(models.Model):
	address1 = models.TextField()
	address2 = models.TextField(blank=True, null=True)
	state = models.TextField()
	country = CountryField()
	zipcode = models.CharField(max_length=15)
	name = models.CharField(max_length=200)
	user = models.ForeignKey(User)
	extranotes = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

class Purchase(models.Model):
	by = models.ForeignKey(User)
	date = models.DateTimeField(default=timezone.now)
	uuid = models.CharField(max_length=32, default=uuid.uuid4, unique=True)
	notes = models.TextField(blank=True, null=True)
	shipped_to = models.ForeignKey(PhysicalAddress, blank=True, null=True)

	def __str__(self):
		return '%s\'s purchase' % self.by

	def get_price(self):
		#TODO: Item bundling, one shipping payment per shop.
		s = 0
		for item in self.purchaseitem_set.all():
			s += item.shipping_price
			s += item.price
		return s

	def get_item_price(self):
		s = 0
		for item in self.purchaseitem_set.all():
			s += item.price
		return s

	def get_shipping_price(self):
		s = 0
		for item in self.purchaseitem_set.all():
			s += item.shipping_price
		return s

	def get_number_of_items(self):
		return self.purchaseitem_set.count()
	get_number_of_items.short_description = 'number of items'

	get_price.short_description = 'price'


class PurchaseItem(models.Model):
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=2**16, decimal_places=8)
	quantity = models.IntegerField(default=1)
	gift = models.BooleanField(default=False)
	purchase = models.ForeignKey(Purchase)
	address = models.ForeignKey(PhysicalAddress, blank=True, null=True)
	shipping_price = models.DecimalField(max_digits=2**16, decimal_places=8, default=0)
	fee = models.DecimalField(max_digits=2**16, decimal_places=8, default=0.995)

	def done(self):
		return self.shippingupdate_set.filter(done=True).count() > 0

	def gettotal(self):
		return self.price * self.quantity + self.shipping_price

	def get_last_update(self):
		return self.shippingupdate_set.last()

	def __str__(self):
		return '%s: %s' % (self.product.product_name, self.quantity)

def in_ten_mins():
	return timezone.now()+timezone.timedelta(minutes=5)

class Authorization(models.Model):
	expires = models.DateTimeField(default=in_ten_mins)
	code = models.CharField(max_length=32, default=uuid.uuid4)
	user = models.ForeignKey(User)
	valid = models.BooleanField(default=True)
	allowto = models.CharField(max_length=32)

	def __str__(self):
		return '%s for %s' % (self.allowto, self.user.username)

	def is_valid(self):
		if not self.expires > timezone.now():
			self.valid = False
			self.save()
		return self.valid and self.expires > timezone.now()

class Checkout(models.Model):
	uuid = models.CharField(default=uuid.uuid4, max_length=32)
	step = models.IntegerField(default=0)
	cart = models.ForeignKey(Cart)
	user = models.ForeignKey(User)
	wallet = models.ForeignKey(Wallet, blank=True, null=True)
	shipping = models.ForeignKey(PhysicalAddress, blank=True, null=True)
	cached_price = models.DecimalField(max_digits=2**16, decimal_places=8, blank=True, null=True)
	cached_shipping = models.DecimalField(max_digits=2**16, decimal_places=8, blank=True, null=True)

	def buy(self):
		purchase = Purchase(by=self.user, shipped_to=self.shipping)
		for item in self.cart.cartentry_set.all():
			if self.user.userextra.can_purchase_item(item.product):
				purchase_item = item.product.buy(self.shipping, self.wallet, item.quantity, item.gift)
				if purchase_item is not None:
					purchase.save()
					purchase_item.purchase = purchase
					purchase_item.save()
					if purchase_item.product.physical:
						su = ShippingUpdate(purchase=purchase_item, update="Item purchased", short_update="Item purchased")
						su.save()

		send_mail("Receipt for your purchase on OKCart", """Hello %s,

Here's the receipt for your recent purchase on OKCart:
https://home.pta2002.com:8000%s

Thanks for buying with OKCart!""" % (self.user.username, reverse('shop:purchase', kwargs={'uuid':purchase.uuid})), "no_reply@okcart.net", [self.user.email])
		return purchase


	def get_shipping_price(self):
		if not self.cached_shipping:
			s = 0
			for item in self.cart.cartentry_set.filter(product__stock__gte=F('quantity'), product__physical=True):
				if item.product.ships_to(self.shipping) and self.user.userextra.can_purchase_item(item.product):
					s += item.product.get_shipping_price(self.shipping)
			self.cached_shipping = s
			self.save()
		return self.cached_shipping


	def get_price(self):
		#TODO: Item bundling, one shipping payment per shop.
		s = 0
		if not self.cached_price:
			self.cached_price = self.cart.gettotal()
			self.save()
		s += self.cached_price
		s += self.get_shipping_price()
		return s


	def __str__(self):
		return self.uuid 


class UserShop(models.Model):
	user = models.OneToOneField(User)
	pay_to_address = models.ForeignKey(Wallet)
	description = models.TextField(default='', blank=True, null=True)
	custom_css = models.TextField(blank=True, null=True)
	can_customcss = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

	def get_earnings(self):
		s = 0
		for p in PurchaseItem.objects.filter(product__seller=self.user):
			s += p.price * p.fee
		return s

	def get_purchases(self):
		return PurchaseItem.objects.filter(product__seller=self.user)

class DigitalFile(models.Model):
	file = models.FileField(upload_to=get_protected_file_path)
	name = models.CharField(max_length=200, default='', null=True, blank=True)
	description = models.TextField(default='', blank=True, null=True)
	product = models.ForeignKey(Product)

	def __str__(self):
		return '%s: %s' % (self.product.product_name, self.name)

	def owned_by(self, u):
		if PurchaseItem.objects.filter(purchase__by=u, product=self.product).count() > 0:
			return True
		return self.product.seller == u

	def get_file_name(self):
		return self.name.lower().replace(' ', '_') + '.' + self.file.path.split('.')[-1]

class DigitalKeySet(models.Model):
	product = models.ForeignKey(Product)
	name = models.CharField(max_length=200, default='', null=True, blank=True)
	description = models.TextField(default='', blank=True, null=True)
	is_link = models.BooleanField(default=False)

	def take_one(self, purchaseitem):
		if purchaseitem.digitalkey_set.filter(keyset=self).count() > 0:
			return purchaseitem.digitalkey_set.filter(keyset=self).first()
		elif self.get_stock() > 0:
			k = self.digitalkey_set.filter(taken_by_id__isnull=True).first()
			k.taken_by = purchaseitem
			k.save()
			return k

	def get_stock(self):
		return self.digitalkey_set.filter(taken_by_id__isnull=True).count()
	get_stock.short_description='stock'

	def create_from_file(self, string):
		# One per line!
		for line in string.split('\n'):
			k = DigitalKey(key=line, keyset=self)
			k.save()

	def __str__(self):
		return '%s: %s' % (self.product.product_name, self.name)

class DigitalKey(models.Model):
	keyset = models.ForeignKey(DigitalKeySet)
	key = models.TextField(default='')
	taken_by = models.ForeignKey(PurchaseItem, blank=True, null=True)

class ShippingUpdate(models.Model):
	purchase = models.ForeignKey(PurchaseItem)
	date = models.DateTimeField(default=timezone.now)
	short_update = models.CharField(max_length=200)
	update = models.TextField(default='')
	done = models.BooleanField(default=False)

	def __str__(self):
		return self.short_update