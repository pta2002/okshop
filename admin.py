from django.contrib import admin
from .models import *

# Register your models here.
class ShippingCountryInline(admin.TabularInline):
	model = ShippingCountry
	classes = ['collapse']

class ProductImageInline(admin.StackedInline):
	model = ProductImage
	classes = ['collapse']


class DigitalFileInline(admin.StackedInline):
	model = DigitalFile
	classes = ['collapse']


class DigitalKeyInline(admin.TabularInline):
	model = DigitalKey
	classes = ['collapse']


@admin.register(DigitalKeySet)
class KeySetAdmin(admin.ModelAdmin):
	list_display = ('name', 'product', 'get_stock')
	inlines = [DigitalKeyInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('product_name', 'seller', 'price', 'stock', 'physical', 'approved')
	list_filter = ('approved', 'physical','worldwide_shipping','free_shipping')
	fieldsets = (
		('Product info', {'fields': ('product_name', 'product_description', 'price', 'seller')}),
		('Moderation', {'fields': ('approved',)}),
		('Shipping/Delivery', {'fields': (('stock', 'physical'), ('ships_from', 'worldwide_shipping'), ('local_price', 'outside_price', 'free_shipping'))}),
		('Digital', {'fields': ('redeeming_instructions',('unlimited_stock','can_purchase_multiple'))})
	)

	inlines = (ProductImageInline, DigitalFileInline, ShippingCountryInline)


class CartEntryInline(admin.TabularInline):
	model = CartEntry
	readonly_fields = ['in_stock']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ('user', 'get_number_of_items', 'gettotal', 'has_physical_items')
	readonly_fields = ('user','gettotal')
	inlines = [CartEntryInline]


@admin.register(UserExtra)
class UserExtraAdmin(admin.ModelAdmin):
	list_display = ('user', 'verified', 'get_balance', 'get_pending')
	list_filter = ('verified',)
	readonly_fields = ('get_balance', 'get_pending')

	fieldsets = [
		('User info', {'fields': ['user']}),
		('Moderation', {'fields': ['verified']}),
		('Wallet', {'fields': [('get_balance', 'get_pending')]}),
		('2FA', {'fields': [('authenticator_id', 'authenticator_verified')]}),
	]


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
	list_display = ('label', 'user', 'address', 'get_balance', 'get_pending', 'active')
	list_filter = ('active',)
	list_editable = ('active',)
	readonly_fields = ('user', 'get_balance', 'get_pending', 'address')

	fieldsets = [
		('Moderation', {'fields': [('user', 'active')]}),
		('Wallet info', {'fields': [('label', 'address'), ('get_balance', 'get_pending')]})
	]


class PurchaseItemInline(admin.TabularInline):
	model = PurchaseItem

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
	list_display = ('by', 'get_price', 'get_number_of_items')
	readonly_fields = ('by','date','uuid')

	fieldsets = (
		(None, {'fields': (('by', 'uuid'), 'date')}),
		('Moderation', {'fields': ('notes',), 'classes': ['collapse']})
	)

	inlines = [PurchaseItemInline]

admin.site.register(UserShop)
admin.site.register(ShippingUpdate)