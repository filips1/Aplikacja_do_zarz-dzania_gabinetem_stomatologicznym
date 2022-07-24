from django.test import SimpleTestCase
from django.urls import reverse, resolve
from account.views import *


class TestUrls(SimpleTestCase):

    def test_app_url_is_resolved(self):
        url = reverse('app')
        self.assertEqual(resolve(url).func, home_view)


    def test_register_url_is_resolved(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, registration_view)


    def test_registermore_url_is_resolved(self):
        url = reverse('registermore')
        self.assertEqual(resolve(url).func, more_info_view)

    def test_login_url_is_resolved(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_view)

    def test_logout_url_is_resolved(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_view)

    def test_account_url_is_resolved(self):
        url = reverse('account')
        self.assertEqual(resolve(url).func, account_view)


    def test_must_authenticate_url_is_resolved(self):
        url = reverse('must_authenticate')
        self.assertEqual(resolve(url).func, must_authenticate_view)  

    def test_must_finish_registration_url_is_resolved(self):
        url = reverse('must_finish_registration')
        self.assertEqual(resolve(url).func, must_fully_register_view)  

    def test_patient_url_is_resolved(self):
        url = reverse('patients')
        self.assertEqual(resolve(url).func, patients_view)  

    def test_choose_dentist_url_is_resolved(self):
        url = reverse('choose_dentist')
        self.assertEqual(resolve(url).func, choose_dentist_ciew)  



    def test_dentist_profile_url_is_resolved(self):
        url = reverse('dentist_profile', args  = "0")
        self.assertEqual(resolve(url).func, dentist_profile_view)  

    def test_location_add_url_is_resolved(self):
        url = reverse('location_add')
        self.assertEqual(resolve(url).func, location_add_view) 



    def test_add_comment_url_is_resolved(self):
        url = reverse('add_comment',args="0")
        self.assertEqual(resolve(url).func, add_comment_view) 



    def test_locations_url_is_resolved(self):
        url = reverse('locations')
        self.assertEqual(resolve(url).func, all_den_loc_view) 



