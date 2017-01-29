from django.test import TestCase
from django.contrib.auth.models import User
from .models import *

# Create your tests here.
# Unfortunatelly you can't really test most of this without spending money...
class WalletTestCase(TestCase):
	def setUp(self):
		self.u1 = User.objects.create_user('u1','','')
		ue1 = UserExtra(user=self.u1)
		ue1.save()
		self.u1.save()

		self.u2 = User.objects.create_user('u2','','')
		ue2 = UserExtra(user=self.u2)
		ue2.save()
		self.u2.save()

	def test_get_balance(self):
		self.assertEqual(self.u1.userextra.get_balance(), 0)