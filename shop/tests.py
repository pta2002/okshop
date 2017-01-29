from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import *
from django.urls import reverse

# Create your tests here.
# TODO: Mock okcashd

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
		response = self.client.post(reverse('shop:register'), {'user name': 'u3', 'email': 'test5@example', 'password': 'pass1234', 'passwordconfirm': 'pass1234'},follow=True)
		self.assertEquals(response.status_code, 200)

		for m in list(response.context['messages']):
			self.assertNotEqual(m.tags, 'success')

class LoginTestCase(TestCase):
	pass