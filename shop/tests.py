from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import *
from django.urls import reverse

# Create your tests here.
# TODO: Mock okcashd

class LoginRegisterTestCase(TestCase):
	def setUp(self):
		return
		self.u1 = User.objects.create_user('u1','','')
		ue1 = UserExtra(user=self.u1)
		ue1.save()
		self.u1.save()

	def test_user_empty_shop(self):
		return
		response = self.client.get(reverse('shop:shop', kwargs={'user':self.u1.username}))