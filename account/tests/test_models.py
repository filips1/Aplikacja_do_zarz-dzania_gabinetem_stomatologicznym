from django.test import TestCase
from account.models import Account, Dentist, Patient
from django.utils import timezone
from django.urls import reverse
from account.forms import RegistrationForm
import datetime
import pytest
from mixer.backend.django import mixer

# models test
@pytest.mark.django_db
class AccountModelTest(TestCase):

    def register_test(self, email="tesdast@test.pl", username="nowe username", password="adminsi23120",date_joined=datetime.date.today(),is_dentist = True, is_admin = True, is_active = True, is_staff = True, is_superuser = True, profile_pic ='default_profile.jpg'):
        return Account.objects.create(email=email, username=username, password=password, date_joined = date_joined, is_dentist = is_dentist, profile_pic = profile_pic, is_admin = is_admin, is_active = is_active, is_staff = is_staff, is_superuser = is_superuser)

    def dentist_test(self, account, First_Name="Imie", Surname="Zbigniew",phone_number=55423432,city = "test", clinic_adress ='test',about_me = "test"):
        return Dentist.objects.create(account = account,First_Name=First_Name, Surname=Surname, phone_number=phone_number, city = city, clinic_adress = clinic_adress, about_me = about_me)

    def patient_test(self, account, First_Name="Imie", Surname="Zbigniew",phone_number=55423432,city = "test", adress ='test', email_conversation="test@fsaf.pl", age=15):
        return Patient.objects.create(account = account,First_Name=First_Name, Surname=Surname, phone_number=phone_number, city = city, adress = adress, email_conversation = email_conversation, age = age)

    def test_register_creation(self):
        w = self.register_test()
        self.assertTrue(isinstance(w, Account))
        self.assertEqual(str(w), w.username)

    def test_dentist_creation(self):
        a = self.register_test()
        w = self.dentist_test(account = a)
        self.assertTrue(isinstance(w, Dentist))
        self.assertEqual(str(w), w.First_Name + " " + w.Surname)

    def test_patient_creation(self):
        a = self.register_test(is_dentist = False)
        w = self.patient_test(account = a)
        self.assertTrue(isinstance(w, Patient))
        self.assertEqual(str(w), w.First_Name + " " + w.Surname)

    def test_patient_no_account_creation(self):
        w = self.patient_test(account = None)
        self.assertTrue(isinstance(w, Patient))
        self.assertEqual(str(w), w.First_Name + " " + w.Surname)
        self.assertEqual(w.account, None)
        
    def test_patient_no_account_creations(self):
        w = mixer.blend('account.Patient', account = None)
        assert w.account == None

    def test_patient_if_account_creations(self):
        a = self.register_test()
        w = self.dentist_test(account = a)
        assert w.account != None



