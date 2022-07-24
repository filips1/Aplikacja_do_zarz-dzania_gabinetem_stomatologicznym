from selenium import webdriver
from account.models import *
from visit.models import *
from tooth.models import *
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
import time
from mixer.backend.django import mixer

class Acceptance_Tests(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('account/functional_tests/chromedriver.exe')
        self.browser.set_window_size(1920, 1080)

    def tearDown(self):
        self.browser.close()

    def test_dentist_register_then_add_patient_then_create_visit(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('register').click()
        register = self.live_server_url + reverse('register')

        assert self.browser.current_url == register
        username = "test"
        password = "specjalne_haselko123"
        email = "specjalne@mail.pl"
        time.sleep(5)
        self.browser.find_element_by_id('inputEmail').send_keys(email)
        self.browser.find_element_by_id('inputUsername').send_keys(username)
        self.browser.find_element_by_id('inputPassword1').send_keys(password)
        self.browser.find_element_by_id('inputPassword2').send_keys(password)
        self.browser.find_element_by_id('inputis_dentist').click()
        self.browser.find_element_by_id("submit").click()
        url = self.live_server_url + reverse('registermore')
        assert self.browser.current_url == url  

        First_Name = "Imię"
        Surname = "Nazwisko"
        phone_number = "+664000111"
        city = "Miastko"
        adres = "ul. Wielka 2"
        self.browser.find_element_by_id("inputFirst_Name").send_keys(First_Name)
        self.browser.find_element_by_id("inputSurname").send_keys(Surname)
        self.browser.find_element_by_id("inputphone_number").send_keys(phone_number)
        self.browser.find_element_by_id("inputcity").send_keys(city)
        self.browser.find_element_by_id("inputadress").send_keys(adres)
        self.browser.find_element_by_id("submit").click()
        time.sleep(5)
        assert self.browser.current_url == self.live_server_url + "/"
        assert Account.objects.filter(username = "test").exists()
        a = Account.objects.get(username = "test")
        dentist = Dentist.objects.get(account = a)
        assert Dentist.objects.filter(account = a).exists()
        assert WeekdayHoursOpen.objects.filter(dentist = dentist)
        assert Cennik.objects.filter(dentist = dentist)

        self.browser.find_element_by_id('dropdown_patient').click()
        self.browser.find_element_by_id('patient_list_header').click()
        url = self.live_server_url + reverse('patients')
        time.sleep(5)
        assert self.browser.current_url == url
        self.browser.find_element_by_id('dentist_create_patient').click()

        age = "12"
        email = "test@email.pl"
        time.sleep(5)
        self.browser.find_element_by_id("inputFirst_Name").send_keys(First_Name)
        self.browser.find_element_by_id("inputSurname").send_keys(Surname)
        self.browser.find_element_by_id("inputphone_number").send_keys(phone_number)
        self.browser.find_element_by_id("inputcity").send_keys(city)
        self.browser.find_element_by_id("inputadress").send_keys(adres)
        self.browser.find_element_by_id("inputage").send_keys(age)
        self.browser.find_element_by_id("inputconversation_email").send_keys(email)
        self.browser.find_element_by_id("create_patient").click()
        time.sleep(5)
        self.browser.switch_to.alert.accept();
        time.sleep(5)
        assert Patient.objects.filter(dentist__in = [dentist])
        patient = Patient.objects.get(dentist__in = [dentist])
        assert Tooth.objects.filter(patient = patient).count() == 32
        self.browser.find_element_by_id("new_visit"+str(patient.id)).click()
        time.sleep(5)
        self.browser.find_element_by_id("visit_form_submit").click()
        time.sleep(5)
        self.browser.switch_to.alert.accept();
        time.sleep(5)
        self.browser.find_element_by_id("tooth_add_btn").click()
        patient = Patient.objects.get(dentist__in = [dentist])
        tooth = Tooth.objects.filter(patient = patient).first()
        time.sleep(10)

        self.browser.find_element_by_id("tooth_a_"+str(tooth.id)).click()
        time.sleep(5)
        self.browser.find_element_by_id("add_tooth_to_visit").click()
        time.sleep(15)
        assert Visit.objects.filter(Patient = patient, Dentist = dentist, Tooth_Repaired__in = [tooth]).exists()

    def test_patient_register_plus_join_dentist(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('register').click()
        register = self.live_server_url + reverse('register')

        assert self.browser.current_url == register
        username = "test"
        password = "specjalne_haselko123"
        email = "specjalne@mail.pl"
        time.sleep(5)
        self.browser.find_element_by_id('inputEmail').send_keys(email)
        self.browser.find_element_by_id('inputUsername').send_keys(username)
        self.browser.find_element_by_id('inputPassword1').send_keys(password)
        self.browser.find_element_by_id('inputPassword2').send_keys(password)
        self.browser.find_element_by_id("submit").click()
        url = self.live_server_url + reverse('registermore')
        assert self.browser.current_url == url  

        First_Name = "Imię"
        Surname = "Nazwisko"
        phone_number = "+664000111"
        city = "Miastko"
        adres = "ul. Wielka 2"
        age = "12"
        email = "test@email.pl"
        self.browser.find_element_by_id("inputFirst_Name").send_keys(First_Name)
        self.browser.find_element_by_id("inputSurname").send_keys(Surname)
        self.browser.find_element_by_id("inputphone_number").send_keys(phone_number)
        self.browser.find_element_by_id("inputcity").send_keys(city)
        self.browser.find_element_by_id("inputadress").send_keys(adres)
        self.browser.find_element_by_id("inputage").send_keys(age)
        self.browser.find_element_by_id("inputconversation_email").send_keys(email)
        self.browser.find_element_by_id("submit").click()
        time.sleep(5)
        assert self.browser.current_url == self.live_server_url + "/"
        assert Account.objects.filter(username = "test").exists()
        a = Account.objects.get(username = "test")
        patient = Patient.objects.get(account = a)
        assert Patient.objects.filter(account = a).exists()
        dentist = mixer.blend(Dentist)
        den_acc = mixer.blend(Account)
        den_acc.is_dentist == True
        den_acc.save()
        dentist.account = den_acc
        dentist.save()

        self.browser.find_element_by_id('dentist_dropdown').click()
        self.browser.find_element_by_id('dentist_list_header').click()
        url = self.live_server_url + reverse('choose_dentist')
        time.sleep(5)
        assert self.browser.current_url == url
        self.browser.find_element_by_id("dentist_join_"+str(dentist.id)).click()
        time.sleep(25)
        assert Patient.objects.filter(account = a, dentist__in = [dentist]).exists()







        
