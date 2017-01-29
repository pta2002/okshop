from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import *
from django.urls import reverse
import pyotp

# Create your tests here.
class RegisterTestCase(TestCase):
	def setUp(self):
		self.u1 = User.objects.create_user('u1','email@example.com','')
		ue1 = UserExtra(user=self.u1)
		ue1.save()
		self.u1.save()

	def test_user_register_all_valid(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u3', 'email': 'test@example.com', 'password': 'pass1234', 'passwordconfirm': 'pass1234'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertEquals(m.tags, 'success')

	def test_user_register_invalid_email(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u4', 'email': 'test1@example', 'password': 'pass1234', 'passwordconfirm': 'pass1234'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_user_register_password_too_short(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u5', 'email': 'test2@example.com', 'password': 'pass123', 'passwordconfirm': 'pass123'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_user_register_password_mismatch(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u6', 'email': 'test3@example.com', 'password': 'pass1234', 'passwordconfirm': 'pass4'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_user_register_username_in_use(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u1', 'email': 'test4@example.com', 'password': 'pass1234', 'passwordconfirm': 'pass1234'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_user_email_in_use(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u7', 'email': 'email@example.com', 'password': 'pass1234', 'passwordconfirm': 'pass1234'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_user_invalid_username(self):
		response = self.client.post(reverse('shop:register'), {'username': 'u3', 'email': 'test5@example', 'password': 'pass1234', 'passwordconfirm': 'pass1234'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

class LoginTestCase(TestCase):
	def setUp(self):
		self.u1 = User.objects.create_user('_u1','email@example.com','p4ssw0rd')
		ue1 = UserExtra(user=self.u1, verified=True)
		ue1.save()
		self.u1.save()

		self.u2 = User.objects.create_user('_u2', 'email2@example.com', 'p4ssw0rd')
		ue2 = UserExtra(user=self.u2, verified=False)
		ue2.save()
		self.u2.save()

		self.u3 = User.objects.create_user('_u3','email3@example.com','p4ssw0rd')
		ue3 = UserExtra(user=self.u3, verified=True, authenticator_id='testing', authenticator_verified=True)
		ue3.save()
		self.u1.save()

	def test_login_all_valid_no_2fa(self):
		response = self.client.post(reverse('shop:login'), {'username': '_u1', 'password': 'p4ssw0rd'},follow=True)
		self.assertEquals(response.status_code, 200)

		self.assertEquals(str(list(response.context['messages'])[0]), 'Welcome back, _u1!')

	def test_login_all_invalid_no_2fa(self):
		response = self.client.post(reverse('shop:login'), {'username': 'invalidname', 'password': 'paaaaaaaaaaaa'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_login_invalid_pass_no_2fa(self):
		response = self.client.post(reverse('shop:login'), {'username': '_u1', 'password': 'paaaaaaaaaaaa'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_login_not_verified(self):
		response = self.client.post(reverse('shop:login'), {'username': '_u2', 'password': 'p4ssw0rd'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

	def test_login_all_valid_2fa(self):
		totp = pyotp.TOTP('testing')
		response = self.client.post(reverse('shop:login'), {'username': '_u3', 'password': 'p4ssw0rd', '2facode': totp.now()},follow=True)
		self.assertEquals(str(list(response.context['messages'])[0]), 'Welcome back, _u3!')

	def test_login_invalid_2fa(self):
		response = self.client.post(reverse('shop:login'), {'username': '_u3', 'password': 'p4ssw0rd', '2facode': ''},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')
