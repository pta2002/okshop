from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import *
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import pyotp
import json


# Create your tests here.
class RegisterTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('u1', 'email@example.com', '')
        ue1 = UserExtra(user=self.u1)
        ue1.save()
        self.u1.save()

    def test_user_register_all_valid(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u3',
            'email': 'test@example.com',
            'password': 'pass1234',
            'passwordconfirm': 'pass1234'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertEquals(m.tags, 'success')

    def test_user_register_invalid_email(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u4',
            'email': 'test1@example',
            'password': 'pass1234',
            'passwordconfirm':
            'pass1234'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_user_register_password_too_short(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u5',
            'email': 'test2@example.com',
            'password': 'pass123',
            'passwordconfirm': 'pass123'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_user_register_password_mismatch(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u6',
            'email': 'test3@example.com',
            'password': 'pass1234',
            'passwordconfirm': 'pass4'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_user_register_username_in_use(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u1',
            'email': 'test4@example.com',
            'password': 'pass1234',
            'passwordconfirm':
            'pass1234'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_user_email_in_use(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u7',
            'email': 'email@example.com',
            'password': 'pass1234',
            'passwordconfirm': 'pass1234'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_user_invalid_username(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'u3',
            'email': 'test5@example',
            'password': 'pass1234',
            'passwordconfirm': 'pass1234'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')


class LoginTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('_u1', 'email@example.com',
                                           'p4ssw0rd')
        ue1 = UserExtra(user=self.u1, verified=True)
        ue1.save()
        self.u1.save()

        self.u2 = User.objects.create_user('_u2', 'email2@example.com',
                                           'p4ssw0rd')
        ue2 = UserExtra(user=self.u2, verified=False)
        ue2.save()
        self.u2.save()

        self.u3 = User.objects.create_user('_u3', 'email3@example.com',
                                           'p4ssw0rd')
        ue3 = UserExtra(user=self.u3, verified=True, authenticator_id='test',
                        authenticator_verified=True)

        ue3.save()
        self.u1.save()

    def test_login_all_valid_no_2fa(self):
        response = self.client.post(reverse('shop:login'), {
            'username': '_u1',
            'password': 'p4ssw0rd'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        self.assertEquals(str(list(response.context['messages'])[0]),
                          'Welcome back, _u1!')

    def test_login_all_invalid_no_2fa(self):
        response = self.client.post(reverse('shop:login'), {
            'username': 'invalidname',
            'password': 'paaaaaaaaaaaa'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_login_invalid_pass_no_2fa(self):
        response = self.client.post(reverse('shop:login'), {
            'username': '_u1',
            'password': 'paaaaaaaaaaaa'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_login_not_verified(self):
        response = self.client.post(reverse('shop:login'), {
            'username': '_u2',
            'password': 'p4ssw0rd'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')

    def test_login_all_valid_2fa(self):
        totp = pyotp.TOTP('test')
        response = self.client.post(reverse('shop:login'), {
            'username': '_u3',
            'password': 'p4ssw0rd',
            '2facode': totp.now()
        }, follow=True)
        self.assertEquals(str(list(response.context['messages'])[0]),
                          'Welcome back, _u3!')

    def test_login_invalid_2fa(self):
        response = self.client.post(reverse('shop:login'), {
            'username': '_u3',
            'password': 'p4ssw0rd',
            '2facode': ''
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        for m in list(response.context['messages']):
            self.assertNotEqual(m.tags, 'success')


class TestUploadFiles(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('__u1', '', 'passw0rd')
        ue1 = UserExtra(user=self.u1, verified=True)
        ue1.save()
        self.u1.save()

        self.p1 = Product(
            product_name='T',
            product_description='d',
            price=0,
            physical=False,
            seller=self.u1
        )
        self.p1.save()

        self.u2 = User.objects.create_user('__u2', '', 'passw0rd')
        ue2 = UserExtra(user=self.u2, verified=True)
        ue2.save()
        self.u2.save()

    def test_upload_product_not_found(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.post(
            reverse('shop:uploadfile', kwargs={'id': '291827346271725623'}),
            {
                'file': SimpleUploadedFile("file.txt", b"t",
                                           content_type="text/txt"),
                'name': 'n'
            }
        )
        self.assertEqual(r.status_code, 404)

    def test_upload_product_not_logged_in(self):
        r = self.client.post(
            reverse('shop:uploadfile', kwargs={'id': self.p1.id}),
            {
                'file': SimpleUploadedFile("file.txt", b"t",
                                           content_type="text/txt"),
                'name': 'n'
            }
        )
        self.assertNotEqual(r.status_code, 200)

    def test_upload_product_no_permission(self):
        self.client.login(username=self.u2.username, password='passw0rd')
        r = self.client.post(
            reverse('shop:uploadfile', kwargs={'id': self.p1.id}),
            {
                'file': SimpleUploadedFile("file.txt", b"t",
                                           content_type="text/txt"),
                'name': 'n'
            }
        )
        self.assertEqual(r.status_code, 403)

    def test_upload_incomplete_request(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.post(
            reverse('shop:uploadfile', kwargs={'id': self.p1.id}),
            {}
        )
        self.assertEqual(r.status_code, 400)

    def test_upload_name_too_big(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.post(
            reverse('shop:uploadfile', kwargs={'id': self.p1.id}),
            {
                'file': SimpleUploadedFile("file.txt", b"t",
                                           content_type="text/txt"),
                'name': 'a'*201
            }
        )
        self.assertEqual(r.status_code, 400)

    def test_upload_no_name(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.post(reverse(
            'shop:uploadfile', kwargs={'id': self.p1.id}),
            {
                'file': SimpleUploadedFile("file.txt", b"t",
                                           content_type="text/txt"),
                'name': ''
            }
        )
        self.assertEqual(r.status_code, 400)

    # Can't seem to fake file size... I'll have to rely on my intuition
    """def test_upload_file_too_large(self):
            self.client.login(username=self.u1.username, password='passw0rd')
            r = self.client.post(
                reverse('shop:uploadfile', kwargs={'id': self.p1.id}),
                {
                    'file': InMemoryUploadedFile(
                        BytesIO(b"d"),
                        None,
                        'file.txt',
                        "text/txt",
                        10**10,
                        None,
                        None
                    ),
                    'name': 's'
                }
            )
            self.assertEqual(r.status_code, 400)"""

    def test_upload_all_fine(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.post(
            reverse('shop:uploadfile', kwargs={'id': self.p1.id}),
            {
                'file': SimpleUploadedFile("file.txt", b"t",
                                           content_type="text/txt"),
                'name': 's'
            }
        )

        # TODO: Get this to work on py3.5
        """rjson = json.loads(str(r.content))
                file = DigitalFile.objects.get(id=rjson['file'])

                self.assertEqual(file.file.read(), b't')"""
        self.assertEqual(r.status_code, 200)


class TestDeleteFile(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('___u1', '', 'passw0rd')
        ue1 = UserExtra(user=self.u1, verified=True)
        ue1.save()
        self.u1.save()

        self.u2 = User.objects.create_user('___u2', '', 'passw0rd')
        ue2 = UserExtra(user=self.u2, verified=True)
        ue2.save()
        self.u1.save()

        self.p1 = Product(product_name='T', product_description='d', price=0,
                          physical=False, seller=self.u1)
        self.p1.save()

        self.file1 = DigitalFile(
            file=SimpleUploadedFile("file.txt", b"t", content_type="text/txt"),
            name='test',
            product=self.p1
        )
        self.file1.save()
        self.file2 = DigitalFile(
            file=SimpleUploadedFile("file.txt", b"t", content_type="text/txt"),
            name='test',
            product=self.p1
        )
        self.file2.save()

    def test_file_not_logged_in(self):
        r = self.client.get(reverse('shop:deletefile',
                                    kwargs={'id': self.file1.id}))
        self.assertNotEqual(r.status_code, 200)

    def test_file_no_permission(self):
        self.client.login(username=self.u2.username, password='passw0rd')
        r = self.client.get(reverse('shop:deletefile',
                                    kwargs={'id': self.file1.id}))
        self.assertEqual(r.status_code, 403)

    def test_file_not_exists(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.get(reverse('shop:deletefile',
                                    kwargs={'id': 2912787347128272}))
        self.assertEqual(r.status_code, 404)

    def test_file_all_fine(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        r = self.client.get(reverse('shop:deletefile',
                                    kwargs={'id': self.file2.id}), follow=True)
        self.assertEqual(r.status_code, 200)


class CheckoutTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('____u1', '', 'passw0rd')
        self.u1.save()
        self.u2 = User.objects.create_user('____u2', '', 'passw0rd')
        self.u2.save()
        self.u3 = User.objects.create_user('____u3', '', 'passw0rd')
        self.u3.save()

        ue1 = UserExtra(user=self.u1, verified=True)
        ue1.save()
        ue2 = UserExtra(user=self.u2, verified=True)
        ue2.save()
        ue3 = UserExtra(user=self.u3, verified=True)
        ue3.save()

        w = Wallet(user=self.u1)
        w.save()
        w1 = Wallet(user=self.u2)
        w2 = Wallet(user=self.u2, label='2')
        w3 = Wallet(user=self.u3, label='3', redeemed=Decimal(-10000))
        w4 = Wallet(user=self.u3, label='3', redeemed=Decimal(-500))
        w1.save()
        w2.save()
        w3.save()
        w4.save()

        self.p1 = Product(
            product_name='t',
            seller=self.u1,
            price=0,
            physical=False,
            stock=10
        )
        self.p1.save()
        self.p2 = Product(
            product_name='t',
            seller=self.u1,
            price=0,
            physical=True,
            stock=10,
            worldwide_shipping=True,
            free_shipping=True
        )
        self.p2.save()
        self.expensiveproduct = Product(
            product_name='t',
            seller=self.u1,
            price=2**32,
            stock=10
        )
        self.expensiveproduct.save()
        self.reasonableproduct = Product(
            product_name='t',
            seller=self.u1,
            price=10,
            stock=10
        )
        self.reasonableproduct.save()
        self.outofstock = Product(
            product_name='t',
            seller=self.u1,
            price=0,
            stock=0
        )
        self.outofstock.save()

    def test_checkout_not_logged_in(self):
        r = self.client.get(reverse('shop:checkout'))
        self.assertNotEqual(r.status_code, 200)

    def test_checkout_cart_empty(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        r = self.client.get(reverse('shop:checkout'))
        self.assertNotEqual(r.status_code, 200)

    def test_checkout_no_money(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        self.u1.userextra.add_to_cart(self.expensiveproduct)
        r = self.client.get(reverse('shop:checkout'))
        self.assertNotEqual(r.status_code, 200)

    def test_checkout_outofstock(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        self.u1.userextra.add_to_cart(self.outofstock)
        r = self.client.get(reverse('shop:checkout'))
        self.assertNotEqual(r.status_code, 200)

    def test_physical_one_wallet_free(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        self.u1.userextra.add_to_cart(self.p2)
        r = self.client.get(reverse('shop:checkout'))
        self.assertTemplateUsed(r, 'shop/checkout1.html')

    def test_physical_one_wallet_free_incomplete_data(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        self.u1.userextra.add_to_cart(self.p2)
        r = self.client.get(reverse('shop:checkout'))
        self.assertTemplateUsed(r, 'shop/checkout1.html')
        c = r.context['checkout']
        r = self.client.post(reverse('shop:checkout'), {'checkout': str(c.uuid)})
        self.assertGreater(len(r.context['messages']), 0)

    def test_physical_one_wallet_free_new_address(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        self.u1.userextra.add_to_cart(self.p2)
        r = self.client.get(reverse('shop:checkout'))
        self.assertTemplateUsed(r, 'shop/checkout1.html')

        c = r.context['checkout']
        r = self.client.post(reverse('shop:checkout'), {
            'checkout': str(c.uuid),
            'name': "Mr. Testing",
            'address1': "Somewhere, Norcross",
            'state': "GA",
            'country': "US",
            'zip': "30092",
            'use_custom_address': ""
        })

        self.assertTemplateUsed(r, 'shop/checkout3.html')
        r = self.client.post(reverse('shop:checkout'),
                             {'checkout': str(c.uuid), 'confirm': ''})
        self.assertEqual(r.status_code, 302)

    def test_digital_one_wallet_free(self):
        self.client.login(username=self.u1.username, password='passw0rd')
        self.u1.userextra.clear_cart()
        self.u1.userextra.add_to_cart(self.p1)
        r = self.client.get(reverse('shop:checkout'))
        self.assertTemplateUsed(r, 'shop/checkout3.html')

    def test_digital_multiple_wallets_free(self):
        self.client.login(username=self.u2.username, password='passw0rd')
        self.u2.userextra.clear_cart()
        self.u2.userextra.add_to_cart(self.p1)
        r = self.client.get(reverse('shop:checkout'))
        self.assertTemplateUsed(r, 'shop/checkout3.html')

    def test_digital_multiple_wallets_enough_money(self):
        self.client.login(username=self.u3.username, password='passw0rd')
        self.u3.userextra.clear_cart()
        self.u3.userextra.add_to_cart(self.reasonableproduct)
        r = self.client.get(reverse('shop:checkout'))
        self.assertTemplateUsed(r, 'shop/checkout2.html')


class ReviewTestCase(TestCase):
    def setUp(self):
        # These names are getting ridiculous
        self.u1 = User.objects.create_user('______u1', '', 'passw0rd')
