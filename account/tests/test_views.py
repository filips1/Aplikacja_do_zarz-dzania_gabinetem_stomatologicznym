from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from mixer.backend.django import mixer
import pytest
from django.contrib.auth.models import User, AnonymousUser
from account.models import Account, Dentist, Patient, Comment, Images_aboutme, Location, Achievements, Specialisation
import json
from account.views import *
from account.forms import RegistrationForm
import os
import datetime
from tooth.models import Tooth
from visit.models import Visit
import json
from django.http import JsonResponse
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestViews(TestCase):



    def test_reg(self):
        path = reverse('register')
        factory = RequestFactory()
        request = factory.post(path, {'email': 'admin@admins.eu', 'username': 'adminfdsa12jl3', 'password1': 'polikujy123', 'password2': 'polikujy123', 'is_dentist': False})
        request.user = AnonymousUser()
        response = self.client.post(path,{'email': 'admin@admins.eu', 'username': 'adminfdsa12jl3', 'password1': 'polikujy123', 'password2': 'polikujy123', 'is_dentist': False})
        assert response.status_code == 302
        assert request.method == 'POST'
        self.assertTemplateUsed('account/register.html')

    def test_regnew(self):
        path = reverse('register')
        factory = RequestFactory()
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        response = registration_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/register.html')
 #   def setUp(self):
  #      self.client = Client()
   #     self.app_url = reverse('app')


    def test_register_view_if_is_authenticated(self):
        path = reverse('register')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)

        response = registration_view(request)
        assert response.status_code == 302

 #   def test_project_app_GET(self):
  #      response = self.client.get(reverse('app'))
#
 #       self.assertEquals(response.status_code, 200)
  #      self.assertTemplateUsed(response,'home.html')



#{'First_Name': 'Janusz', 'Surname': 'Testowy', 'phone_number': '+444455552222', 'city': 'Poznań', 'clinic_adress': '60-166 Poznań Grunwaldzka 186'}
#{'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 12}

    def test_register_more_info_view_if_is_authenticated(self):
        path = reverse('registermore')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        response = more_info_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/registermore.html')

    def test_register_more_info_view_as_dentist_if_is_authenticated(self):
        path = reverse('registermore')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        response = more_info_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/registermore.html')

    def test_mo_info_if_dentist_fully_reg(self):
        path = reverse('registermore')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)
        dentist = mixer.blend(Dentist)
        dentist.account = request.user
        dentist.save()
        response = more_info_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/registermore.html')

    def test_mo_info_if_patient_fully_reg(self):
        path = reverse('registermore')

        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)
        patient = mixer.blend(Patient)
        patient.account = request.user
        patient.save()
        response = more_info_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/registermore.html')

    def test_register_more_info_view_if_is_authenticated_with_form(self):
        path = reverse('registermore')
        factory = RequestFactory()
        request = factory.post(path,{'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 12})
        request.user = mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        response = more_info_view(request)
        assert response.status_code == 302

    def test_register_more_info_view_if_is_authenticated_with_form_young(self):
        path = reverse('registermore')
        factory = RequestFactory()
        request = factory.post(path,{'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 10})
        request.user = mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        response = more_info_view(request)
        assert response.status_code == 302

    def test_register_more_info_view_as_dentist_if_is_authenticated_with_form(self):
        path = reverse('registermore')
        factory = RequestFactory()
        request = factory.post(path,{'First_Name': 'Janusz', 'Surname': 'Testowy', 'phone_number': '+444455552222', 'city': 'Poznań', 'clinic_adress': '60-166 Poznań Grunwaldzka 186'})
        request.user = mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        response = more_info_view(request)
        assert response.status_code == 302

    def test_mo_info_if_dentist_fully_reg_with_form(self):
        path = reverse('registermore')        
        factory = RequestFactory()
        request = factory.post(path,{'First_Name': 'Janusz', 'Surname': 'Testowy', 'phone_number': '+444455552222', 'city': 'Poznań', 'clinic_adress': '60-166 Poznań Grunwaldzka 186'})

        request.user = mixer.blend(Account)
        dentist = mixer.blend(Dentist)
        dentist.account = request.user
        dentist.save()
        response = more_info_view(request)
        assert response.status_code == 302

    def test_mo_info_if_patient_fully_reg_with_form(self):
        path = reverse('registermore')
        factory = RequestFactory()
        request = factory.post(path,{'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 12})
        request.user = mixer.blend(Account)
        patient = mixer.blend(Patient)
        patient.account = request.user
        patient.save()
        response = more_info_view(request)
        assert response.status_code == 302


    def test_login(self):
        path = reverse('login')
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        response = login_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/logins.html')


    def test_login_view_if_is_authenticated(self):
        path = reverse('login')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)

        response = login_view(request)
        assert response.status_code == 302

    def test_logout(self):
        path = reverse('logout')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)
        response = self.client.get(path)
        assert response.status_code == 302

    def test_must_auth_test_View(self):
        path = reverse('must_authenticate')
        request = RequestFactory().get(path)
        request.user = mixer.blend(Account)

        response = must_authenticate_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/must_authenticate.html')

    def test_must_fully_register_view(self):
        path = reverse('must_authenticate')
        request = RequestFactory().get(path)
        request.user =  AnonymousUser()

        response = must_fully_register_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/must_fully_register.html')

    def test_patients_view(self):
        path = reverse('patients')
        request = RequestFactory().get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient = mixer.blend(Patient)
        if patient.age < 12:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
        else:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="stały",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="prawy",level="dolny",number=b)])

        response = patients_view(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/must_fully_register.html')

    def test_patients_view_only_mine(self):
        path = reverse('patients')
        request = RequestFactory().get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient = mixer.blend(Patient)
        patient.dentist.add(dentist)
        patient.save()
        if patient.age < 12:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
        else:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="stały",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="prawy",level="dolny",number=b)])
           
        response = patients_view(request, "mine")
        assert response.status_code == 200
        self.assertTemplateUsed('account/must_fully_register.html')

    def test_patients_view_only_mine_with_visit(self):
        path = reverse('patients')
        request = RequestFactory().get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient = mixer.blend(Patient)
        patient.dentist.add(dentist)
        patient.save()
        if patient.age < 12:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
        else:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="stały",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="prawy",level="dolny",number=b)])
        
        visit = mixer.blend(Visit)
        visit.Patient = patient
        visit.Dentist = dentist
        visit.Type_of = 'wizyta kontrolna'
        visit.save()

        response = patients_view(request, "mine")

        assert response.status_code == 200
        self.assertTemplateUsed('account/must_fully_register.html')



    def test_patients_view_only_mine_ajax_with_visit(self):
        path = '/patients/?q=name%2F--%2Fasa'
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient = mixer.blend(Patient)
        patient.dentist.add(dentist)
        patient.save()
        if patient.age < 12:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
        else:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="stały",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="prawy",level="dolny",number=b)])
        
        visit = mixer.blend(Visit)
        visit.Patient = patient
        visit.Dentist = dentist
        visit.Type_of = 'wizyta kontrolna'
        visit.save()
        request.content_type = 'application/json'
        response = patients_view(request,"test")

        assert response.status_code == 200

    def test_create_new_patient_view_ajax(self):
        path = reverse('create_new_patient')
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        request.content_type = 'application/json'
        response = create_new_patient_view(request)


        assert response.status_code == 200
    def test_create_new_patient_view_ajax_with_form(self):
        path = reverse('create_new_patient')
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path,{'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 12})
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        response = create_new_patient_view(request)

        assert response.status_code == 302

    def test_create_new_patient_view_ajax_with_wrong_form(self):
        path = reverse('create_new_patient')
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        response = create_new_patient_view(request)

        assert response.status_code == 200

    def test_create_new_patient_view_ajax_with_form_young(self):
        path = reverse('create_new_patient')
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
        request = factory.post(path,{'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 10})
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        response = create_new_patient_view(request)

        assert response.status_code == 302

    def test_update_patient_list_view_ajax(self):
        path = reverse('update_patient_list')
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient = mixer.blend(Patient)
        if patient.age < 12:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
        else:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="stały",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="prawy",level="dolny",number=b)])
        
        patientoth = mixer.blend(Patient)
        patientoth.dentist.add(dentist)
        patientoth.save()
        if patientoth.age < 12:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
        else:
            for b in range(1,9):
                Tooth.objects.bulk_create([Tooth(patient=patient,tooth_type="stały",side="prawy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="górny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                    Tooth(patient=patient,tooth_type="stały",side="prawy",level="dolny",number=b)])
        visit = mixer.blend(Visit)
        visit.Patient = patientoth
        patient.dentist.add(dentist)
        patient.save()
        visit.Dentist = dentist
        visit.Type_of = 'wizyta kontrolna'
        visit.save()
        request.content_type = 'application/json'
        response = update_patient_list_view(request)

        assert response.status_code == 200


    def test_update_new_patient_view_ajax_with_form_(self):
        patient = mixer.blend(Patient)
        path = reverse('patient_update', kwargs={"id": patient.id})
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
        data = {'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 10}
        request = factory.post(path,data)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient.account = None
        patient.dentist.add(dentist)
        patient.save()


        response = update_patient_view(request, id = patient.id)

        assert response.status_code == 302
    def test_update_new_patient_view_ajax(self):
        patient = mixer.blend(Patient)
        path = 'patients/'+str(patient.id)+'/update'
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()

        patient.account = None
        patient.dentist.add(dentist)
        patient.save()
        request.content_type = 'application/json'
        response = update_patient_view(request, id = patient.id)

        assert response.status_code == 200

    def test_update_new_patient_view_get_ajax(self):
        patient = mixer.blend(Patient)
        path = 'patients/'+str(patient.id)+'/update'
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()

        patient.account = None
        patient.dentist.add(dentist)
        patient.save()
        request.content_type = 'application/json'
        response = update_patient_view(request, id = patient.id)

        assert response.status_code == 200

    def test_delete_patient_view_ajax_yes(self):
        patient = mixer.blend(Patient)
        path = reverse('patient_delete', kwargs={"id": patient.id})
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
    
        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient.account = None
        patient.dentist.add(dentist)
        patient.save()
        request.content_type = 'application/json'

        response = delete_patient_view(request, id = patient.id)

        assert response.status_code == 302

    def test_delete_patient_view_ajax_no(self):
        patient = mixer.blend(Patient)
        path = reverse('patient_delete', kwargs={"id": patient.id})
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
    
        request = factory.get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist =  mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient.account = None
        patient.dentist.add(dentist)
        patient.save()
        request.content_type = 'application/json'

        response = delete_patient_view(request, id = patient.id)

        assert response.status_code == 200

    def test_dentist_view(self):
        path = reverse('choose_dentist')
        request = RequestFactory().get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        dentist =  mixer.blend(Dentist)


        patient = mixer.blend(Patient)
        patient.account = user
        patient.save()

        response = choose_dentist_ciew(request)
        assert response.status_code == 200
        self.assertTemplateUsed('account/choose_dentist.html')

    def test_dentist_view_only_mine(self):
        path = reverse('choose_dentist')
        request = RequestFactory().get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        dentist =  mixer.blend(Dentist)
        patient = mixer.blend(Patient)
        patient.account = user
        patient.dentist.add(dentist)
        patient.save()
        response = choose_dentist_ciew(request, "mine")
        assert response.status_code == 200
        self.assertTemplateUsed('account/account/choose_dentist.html')

    def test_dentist_view_only_mine_with_search(self):
        path = '/choose_dentist/?q=name%2F--%2Fasa'
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        dentist =  mixer.blend(Dentist)
        patient = mixer.blend(Patient)
        patient.account = user
        patient.dentist.add(dentist)
        patient.save()
        response = choose_dentist_ciew(request, "mine")
        assert response.status_code == 200
        self.assertTemplateUsed('account/account/choose_dentist.html')

    def test_dentist_view_change_stat_remove(self):
        dentist =  mixer.blend(Dentist)
        path = reverse('dentist_change_stat',  kwargs={"dentist_id": dentist.id} )
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        dentst_oth = mixer.blend(Dentist)
        patient = mixer.blend(Patient)
        patient.account = user
        patient.dentist.add(dentist)
        patient.save()
        response = dentist_change_stat_view(request,dentist.id)
        assert response.status_code == 302

    def test_dentist_view_change_stat_add(self):
        dentist =  mixer.blend(Dentist)
        path = reverse('dentist_change_stat',  kwargs={"dentist_id": dentist.id} )
        factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')

        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        dentst_oth = mixer.blend(Dentist)
        patient = mixer.blend(Patient)
        patient.account = user
        patient.save()
        response = dentist_change_stat_view(request,dentist.id)
        assert response.status_code == 302

    def test_location_add_view(self):
        dentist =  mixer.blend(Dentist)
        path = reverse('location_add')
        factory = RequestFactory()

        request = factory.get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist.account = user
        dentist.save()

        response = location_add_view(request)
        assert response.status_code == 200

        self.assertTemplateUsed('account/location_add.html')







    def test_location_add_view_exists(self):
        dentist =  mixer.blend(Dentist)
        path = reverse('location_add')
        factory = RequestFactory()
        location = Location.objects.create( about = "HAHAHAHHA", location = '17.03564894189674,51.09632746597592')
        location.dentist.add(dentist)
        location.save()
        request = factory.get(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist.account = user
        dentist.save()

        response = location_add_view(request, location.id)
        assert response.status_code == 200

        self.assertTemplateUsed('account/location_add.html')



    def test_all_den_loc_view_as_patient(self):
        path = reverse('locations')
        factory = RequestFactory()
        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = False
        user.save()
        dentist = mixer.blend(Dentist)
        loc = Location.objects.create(about = "HAHAHAHHA", location = '17.03564894189674,51.09632746597592')
        loc.dentist.add(dentist)
        loc.save()
        patient = mixer.blend(Patient)
        patient.account = user
        patient.save()
        response = all_den_loc_view(request)
        assert response.status_code == 200


    def test_all_den_loc_view_as_dentist(self):
        path = reverse('locations')
        factory = RequestFactory()
        request = factory.post(path)
        request.user =  mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        loc = Location.objects.create(about = "HAHAHAHHA", location = '17.03564894189674,51.09632746597592')
        loc.dentist.add(dentist)
        loc.save()
        dentist.account = user
        dentist.save()
        response = all_den_loc_view(request)
        assert response.status_code == 200

    def test_home_view(self):
        path = reverse('app')
        factory = RequestFactory()
        request = factory.post(path)
        request.user =  mixer.blend(Account)
        response = home_view(request)
        assert response.status_code == 200

    def test_home_view(self):
        path = reverse('app')
        factory = RequestFactory()
        request = factory.post(path)
        request.user =  mixer.blend(Account)
        response = home_view(request)
        assert response.status_code == 200




    def test_dentist_profile_view(self):
        with open('static/brak.png', 'rb') as img:
            dentist = mixer.blend(Dentist)
            path = reverse('dentist_profile')
            factory = RequestFactory()
            data = {'dentist': dentist.id, 'about': 'afdsa3', "Image": img}
            request = factory.post(path, data)
            request.user = mixer.blend(Account)
            user = request.user

            dentist.account = user
            dentist.save()
            for i in range(12):
                comment = mixer.blend(Comment)
                comment.dentist = dentist
                comment.save()

            image = mixer.blend(Images_aboutme)
            image.dentist = dentist
            image.save()

            location = Location.objects.create(about = "HAHAHAHHA", location = '17.03564894189674,51.09632746597592')
            location.dentist.add(dentist)
            location.save()
            response = dentist_profile_view(request)
            assert response.status_code == 302

    def test_dentist_profile_view_POST(self):
        with open('static/brak.png', 'rb') as img:
            dentist = mixer.blend(Dentist)
            path = reverse('dentist_profile')
            factory = RequestFactory()
            data = {'dentist': dentist.id, 'about': 'afdsa3', "Image": img}
            request = factory.post(path, data)
            request.user = mixer.blend(Account)
            user = request.user

            dentist.account = user
            dentist.save()
            for i in range(12):
                comment = mixer.blend(Comment)
                comment.dentist = dentist
                comment.save()

            image = mixer.blend(Images_aboutme)
            image.dentist = dentist
            image.save()

            response = dentist_profile_view(request)
            assert response.status_code == 302

    def test_dentist_profile_view_GET_as_me(self):
        dentist = mixer.blend(Dentist)
        path = reverse('dentist_profile')
        factory = RequestFactory()
        request = factory.get(path)
        request.user = mixer.blend(Account)
        user = request.user

        dentist.account = user
        dentist.save()
        for i in range(12):
            comment = mixer.blend(Comment)
            comment.dentist = dentist
            comment.save()

        image = mixer.blend(Images_aboutme)
        image.dentist = dentist
        image.save()
        response = dentist_profile_view(request, dentist_id= dentist.id)
        assert response.status_code == 200


    def test_account_view_GET(self):

        path = reverse('account')
        factory = RequestFactory()
        request = factory.get(path)
        request.user = mixer.blend(Account)

        user = request.user
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        dentist.account = user
        dentist.save()  
        who = mixer.blend(WeekdayHoursOpen) 
        who.dentist = dentist
        who.save()
        cennik = mixer.blend(Cennik)
        cennik.dentist = dentist
        cennik.save()

        response = account_view(request)
        assert response.status_code == 200

    def test_account_view_POST_email(self):
        path = reverse('account')
        factory = RequestFactory()
        request = factory.post(path,{'form_type': 'form_account','email': 'admin@adpd.pl', 'username': 'admin'})
        request.user = mixer.blend(Account)
        user = request.user
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        who = mixer.blend(WeekdayHoursOpen) 
        who.dentist = dentist
        who.save() 
        cennik = mixer.blend(Cennik)
        cennik.dentist = dentist
        cennik.save()   
        response = account_view(request)
        assert response.status_code == 200

    def test_account_view_POST_password(self):
        path = reverse('account')
        factory = RequestFactory()
        request = factory.post(path,{'old_password': 'testowe1234', 'new_password1': 'testowe123', 'new_password2': 'testowe123'})
        user = mixer.blend(Account)
        request.user = user
        user.password = 'testowe1234'
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        dentist.account = user
        dentist.save()   
        who = mixer.blend(WeekdayHoursOpen) 
        who.dentist = dentist
        who.save()
        cennik = mixer.blend(Cennik)
        cennik.dentist = dentist
        cennik.save()
        response = account_view(request)
        assert response.status_code == 200

    def test_account_view_POST_image(self):
        with open('static/brak.png', 'rb') as img:
            path = reverse('account')
            factory = RequestFactory()
            user = mixer.blend(Account)
            request = factory.post(path,{'form_type': 'form_image','profile_pic': img})
            request.user = user
            user.is_dentist = True
            user.save()
            dentist = mixer.blend(Dentist)
            dentist.account = user
            dentist.save()    
            who = mixer.blend(WeekdayHoursOpen) 
            who.dentist = dentist
            who.save()
            cennik = mixer.blend(Cennik)
            cennik.dentist = dentist
            cennik.save()
            response = account_view(request)
            assert response.status_code == 200







