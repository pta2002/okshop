from django.test import TestCase
from django.contrib.auth.models import User
from .models import *

# Create your tests here.
class WalletTestCase(TestCase):
	def setUp(self):
		self.u1 = User.objects.create_user('u1','','')
		self.u1.save()

		self.u2 = User.objects.create_user('u2','','')
		self.u2.save()