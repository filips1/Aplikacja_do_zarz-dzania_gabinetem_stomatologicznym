from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from mixer.backend.django import mixer
import pytest
from django.contrib.auth.models import User, AnonymousUser
from account.models import *
import json
import datetime
from tooth.models import Tooth
from visit.models import Visit
import json
from django.http import JsonResponse
from visit.views import *
from visit.models import *
from datetime import date, datetime, time, timedelta
from tooth.models import *
import unittest


@pytest.mark.django_db
class new_visit_tests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(new_visit_tests,cls).setUpClass()
        cls.path = reverse('new_visit')
        cls.factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
        user = mixer.blend(Account)
        user.is_dentist = True
        user.save()
        cls.user = user
        dentist = mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        patient = mixer.blend(Patient)
        acc = mixer.blend(Account)
        patient.dentist.add(dentist)
        patient.account = acc
        patient.save()
        cls.patient = patient
        cls.dentist = dentist
        WeekdayHoursOpen.objects.create(dentist = dentist, start_hour = time(0,0,0,0), end_hour = time(23,59,0,0), open_days = [1,2,3,4,5,6,7])
        cennik = mixer.blend(Cennik)
        cennik.dentist = dentist
        cennik.save()

    def test_new_visit_view_GET(self):
        request = self.factory.get(self.path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = new_visit_view(request)
        assert response.status_code == 200


    def test_new_visit_view_POST(self):
        path = self.path
        factory = self.factory
        request = factory.post(path, {'day_of_visit': datetime.today().date()+ timedelta(days = 1), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'zaplanowana', 'Type_of': 'wyrywanie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0})
        request.user =  self.user
        response = new_visit_view(request)
        assert response.status_code == 302

    def test_new_visit_view_POST_later(self):
        path = self.path
        factory = self.factory
        request = factory.post(path, {'day_of_visit': datetime.today().date() + timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'zaplanowana', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0})
        request.user =  self.user
        response = new_visit_view(request)
        assert response.status_code == 302

    def test_new_visit_view_POST_to_accept_by_patient(self):
        path = self.path
        factory = self.factory
        request = factory.post(path, {'day_of_visit': datetime.today().date() + timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'do zatwierdzenia przez pacjenta', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0})
        request.user =  self.user
        response = new_visit_view(request)
        assert response.status_code == 302

    def test_new_visit_view_POST_wrong(self):
        path = self.path
        factory = self.factory
        request = factory.post(path, {'day_of_visit': datetime.today().date() - timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'do zatwierdzenia przez pacjenta', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0})
        request.user = self.user
        response = new_visit_view(request)
        print(response.content)
        assert response.status_code == 200
        a = json.loads(response.content)
        assert(a['form_is_fine'] == False)


@pytest.mark.django_db
class TestUnaprovedVisitView(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestUnaprovedVisitView,cls).setUpClass()
        cls.factory = RequestFactory()
        cls.user = mixer.blend(Account)


    def test_VisitUnaprovedShowView_as_dentist(self):
        path = reverse('unaproved')
        request = self.factory.get(path)
        request.user =  self.user
        user = request.user
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        dentist.account = user
        dentist.save()
        visit = mixer.blend(Visit)
        visit.Dentist = dentist
        visit.status = "do zatwierdzenia przez pacjenta"
        visit.save()
        response = VisitUnaprovedShowView(request)
        assert response.status_code == 200
        self.assertTemplateUsed('visit/unaproved.html')

    def test_VisitUnaprovedShowView_as_patietn(self):
        path = reverse('unaproved')
        request = self.factory.get(path)
        request.user =  self.user
        user = request.user
        user.is_dentist = False
        user.save()
        patient = mixer.blend(Patient)

        patient.account = user
        patient.save()
        visit = mixer.blend(Visit)
        visit.Patient = patient
        visit.status = "do zatwierdzenia przez pacjenta"
        visit.save()

        response = VisitUnaprovedShowView(request)
        assert response.status_code == 200
        self.assertTemplateUsed('visit/unaproved.html')

    def test_VisitApproveView_as_patient(self):
        visit = mixer.blend(Visit)
        path = reverse('visit_approve',kwargs={"visit_id": visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        user = request.user
        user.is_dentist = False
        user.save()
        patient = mixer.blend(Patient)
        den = mixer.blend(Dentist)
        acc = mixer.blend(Account)
        den.account = acc
        visit.Dentist = den
        den.save()
        patient.account = user
        patient.save()

        visit.Patient = patient
        visit.status = "do zatwierdzenia przez pacjenta"
        visit.save()

        response = VisitApprove(request, visit_id = visit.id)
        assert response.status_code == 302

    def test_VisitApproveView_as_dentist(self):
        visit = mixer.blend(Visit)
        path = reverse('visit_approve',kwargs={"visit_id": visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        user = request.user
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        pat = mixer.blend(Patient)
        acc = mixer.blend(Account)
        pat.account = acc
        visit.Patient = pat
        pat.save()
        dentist.account = user
        dentist.save()
        visit.Dentist = dentist
        visit.status = 'nie potwierdzona'

        visit.save()
        response = VisitApprove(request, visit_id = visit.id)
        assert response.status_code == 302

    def test_VisitRejectView_as_patient(self):
        visit = mixer.blend(Visit)
        path = reverse('visit_reject',kwargs={"visit_id": visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        den = mixer.blend(Dentist)
        acc = mixer.blend(Account)
        den.account = acc
        visit.Dentist = den
        den.save()
        user = request.user
        user.is_dentist = False
        user.save()
        patient = mixer.blend(Patient)

        patient.account = user
        patient.save()

        visit.Patient = patient
        visit.status = "do zatwierdzenia przez pacjenta"
        visit.save()

        response = VisitReject(request, visit_id = visit.id)
        assert response.status_code == 302

    def test_VisitRejectView_as_dentist(self):
        visit = mixer.blend(Visit)
        path = reverse('visit_reject',kwargs={"visit_id": visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        user = request.user
        user.is_dentist = True
        user.save()
        dentist = mixer.blend(Dentist)
        pat = mixer.blend(Patient)
        acc = mixer.blend(Account)
        pat.account = acc
        pat.save()


        dentist.account = user
        dentist.save()
        visit.Dentist = dentist
        visit.status = 'nie potwierdzona'
        visit.Patient = pat

        visit.save()
        response = VisitReject(request, visit_id = visit.id)
        assert response.status_code == 302

@pytest.mark.django_db
class TestInfo(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestInfo,cls).setUpClass()
        cls.factory = RequestFactory()
        cls.user = mixer.blend(Account)
        info = mixer.blend(Wiadomosc)
        info.target = cls.user
        info.save()
        cls.info = info
    def test_info_view(self):
        path = reverse('info')
        request = self.factory.get(path)
        request.user =  self.user
        response = InfoView(request)
        assert response.status_code == 200
        self.assertTemplateUsed('visit/informations.html')


    def test_info_seen_view(self):
        self.info.read = False
        self.info.save()
        path = reverse('info_seen',kwargs={'info_id':self.info.id})
        request = self.factory.get(path)
        request.user =  self.user
        response = InfoSeenView(request, info_id = self.info.id)
        assert response.status_code == 302


    def test_info_delete_view(self):
        path = reverse('info_delete',kwargs={'info_id':self.info.id})
        request = self.factory.get(path)
        request.user =  self.user
        response = InfoDeleteView(request, info_id = self.info.id)
        assert response.status_code == 302


@pytest.mark.django_db
class TestVistisByPatient(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestVistisByPatient,cls).setUpClass()
        cls.factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
        user = mixer.blend(Account)
        user.is_dentist = False
        user.save()
        cls.user = user
        dentist = mixer.blend(Dentist)
        acc = mixer.blend(Account)
        dentist.account = acc
        dentist.save()
        patient = mixer.blend(Patient)
        patient.dentist.add(dentist)
        patient.account = user
        patient.save()
        cls.patient = patient
        cls.dentist = dentist
        cennik = mixer.blend(Cennik)
        cennik.dentist = dentist
        cennik.save()
        WeekdayHoursOpen.objects.create(dentist = dentist, start_hour = time(0,0,0,0), end_hour = time(23,59,0,0), open_days = [1,2,3,4,5,6,7])

    def test_new_visit_dentist_chosen_view_GET(self):
        path =  reverse('new_visit_heh',kwargs={'id':self.dentist.id})
        request = self.factory.get(path)
        request.user =  self.user

        response = new_visit_dentist_chosen_view(request, id = self.dentist.id)
        assert response.status_code == 200

    def test_new_visit_dentist_chosen_view_POST(self):
        path =  reverse('new_visit_heh',kwargs={'id':self.dentist.id})
        data = {'day_of_visit': datetime.today().date() + timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'nie potwierdzona', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0}
        request = self.factory.post(path,id = self.dentist.id, data = data)
        request.user =  self.user
        response = new_visit_dentist_chosen_view(request, id = self.dentist.id)
        assert response.status_code == 302

    def test_new_visit_dentist_chosen_view_POST_wrong(self):
        path =  reverse('new_visit_heh',kwargs={'id':self.dentist.id})
        data = {'day_of_visit': datetime.today().date() - timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'nie potwierdzona', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0}
        request = self.factory.post(path,id = self.dentist.id, data = data)
        request.user =  self.user
        response = new_visit_dentist_chosen_view(request, id = self.dentist.id)
        assert response.status_code == 200

    def test_new_visit_by_patient_view_GET(self):
        path = reverse('new_by_patient')
        request = self.factory.get(path)
        request.user =  self.user

        response = new_visit_by_patient_view(request)
        assert response.status_code == 200

    def test_new_visit_by_patient_view_POST(self):
        path = reverse('new_by_patient')
        data = {'day_of_visit': datetime.today().date() + timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'nie potwierdzona', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0}
        request = self.factory.post(path,id = self.dentist.id, data = data)
        request.user =  self.user
        response = new_visit_by_patient_view(request)
        assert response.status_code == 302

    def test_new_visit_by_patient_view_POST_wrong(self):
        path = reverse('new_by_patient')
        data = {'day_of_visit': datetime.today().date() - timedelta(days = 15), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12), 'status': 'nie potwierdzona', 'Type_of': 'leczenie', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0}
        request = self.factory.post(path,id = self.dentist.id, data = data)
        request.user =  self.user
        response = new_visit_by_patient_view(request)
        assert response.status_code == 200

    def test_cancel_visit_view_POST_as_patient(self):
        visit = mixer.blend(Visit)
        path = reverse('visit_cancel',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        visit.Dentist = self.dentist
        visit.Patient = self.patient
        visit.save()
        request.content_type = 'application/json'
        response = VisitCancelView(request, visit_id = visit.id)
        assert response.status_code == 200

    def test_revive_visit_view_POST_as_patient(self):
        visit = mixer.blend(Visit)   
        path = reverse('visit_revive',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        visit.day_of_visit = datetime.today().date()+ timedelta(days = 1)
        visit.Dentist = self.dentist
        visit.Patient = self.patient
        visit.save()
        request.content_type = 'application/json'
        response = VisitReviveView(request, visit_id = visit.id)
        assert response.status_code == 200


    def test_visit_date_change_view_POST_as_patient(self):
        visit = mixer.blend(Visit)
        visit.Dentist = self.dentist
        visit.day_of_visit = datetime.today().date() + timedelta(days = 1)
        visit.time_of_the_visit = time(11,2)
        visit.time_end_visit = time(12,2)
        visit.status = "zaplanowana"
        visit.Type_of = "wyrywanie"
        visit.Patient = self.patient
        visit.save()
        path = reverse('visit_date_change',kwargs={'visit_id':visit.id})
        request = self.factory.post(path,{'day_of_visit': datetime.today().date() + timedelta(days= 1), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12),})
        request.user =  self.user
        response = VisitDateChangeView(request, visit_id = visit.id)
        assert response.status_code == 200




@pytest.mark.django_db
class TestVisitEdit(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestVisitEdit,cls).setUpClass()
        cls.factory = RequestFactory(HTTP_X_REQUESTED_WITH ='XMLHttpRequest')
        user = mixer.blend(Account)
        user.is_dentist = True
        user.save()
        cls.user = user
        dentist = mixer.blend(Dentist)
        acc = mixer.blend(Account)

        patient = mixer.blend(Patient)
        patient.dentist.add(dentist)
        patient.account = acc
        patient.save()
        dentist.account = user
        dentist.save()
        cls.patient = patient
        cls.dentist = dentist
        WeekdayHoursOpen.objects.create(dentist = dentist, start_hour = time(0,0,0,0), end_hour = time(23,59,0,0), open_days = [1,2,3,4,5,6,7])
        cennik = mixer.blend(Cennik)
        cennik.dentist = dentist
        cennik.save()  
        cls.visit = mixer.blend(Visit)  
        cls.visit.Dentist = dentist
        cls.visit.Patient = patient
        cls.visit.save()

    def test_edit_visit_view_GET(self):

        path = reverse('visit_edit_new',kwargs={'visit_id':self.visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = VisitEditNew(request,visit_id = self.visit.id)
        assert response.status_code == 200

    def test_edit_visit_view_POST(self):
        visit = self.visit
        visit.day_of_visit = datetime.today().date() + timedelta(days = 1)
        visit.time_of_the_visit = time(11,2)
        visit.time_end_visit = time(12,2)
        visit.status = "zaplanowana"
        visit.Type_of = "wyrywanie"
        visit.save()
        path = reverse('visit_edit_new',kwargs={'visit_id':visit.id})
        request = self.factory.post(path,{'Type_of': 'wizyta kontrolna', 'desc': '1231143', 'cost': 123.0})
        request.user =  self.user
        response = VisitEditNew(request, visit_id = visit.id)
        assert response.status_code == 200

    def test_edit_visit_view_POST_wrong(self):
        visit = self.visit
        visit.Type_of = "wyrywanie"
        visit.save()
        path = reverse('visit_edit_new',kwargs={'visit_id':visit.id})
        data = {'day_of_visit': datetime.today().date(), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(9, 12), 'status': 'zaplanowana', 'Type_of': 'wizyta kontrolna', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0}
        request = self.factory.post(path,data = data)
        request.user =  self.user
        response = VisitEditNew(request,visit_id = visit.id)
        assert response.status_code == 200

    def test_delete_visit_view_GET(self):
        path = reverse('visit_delete',kwargs={'visit_id':self.visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = VisitDeleteView(request, visit_id = self.visit.id)
        assert response.status_code == 200

    def test_delete_visit_view_POST_old(self):
        visit = self.visit
        visit.Type_of = "leczenie"
        visit.status = "odbyła sie"
        visit.day_of_visit = datetime.today().date() - timedelta(days = 15)
        visit.time_of_the_visit = time(11,2)
        visit.time_end_visit = time(12,2)
        visit.save()
        th_oth = mixer.blend(tooth_healing_destruction)
        th = mixer.blend(tooth_healing_destruction)
        td = mixer.blend(Tooth_destructions)
        th_oth.Tooth_destructions = td
        th_oth.save()
        th.visit = visit
        th.tooth_destructions = td
        th.save()
        td.healed = True
        td.save()
        path = reverse('visit_delete',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        response = VisitDeleteView(request,visit_id = visit.id)
        assert response.status_code == 200

    def test_delete_visit_view_POST_wronh(self):
        visit = self.visit
        visit.Type_of = "wyrywanie"
        visit.status = "odbyła sie"
        visit.day_of_visit = datetime.today().date() + timedelta(days = 15)
        visit.save()
        path = reverse('visit_delete',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        response = VisitDeleteView(request,visit_id = visit.id)
        assert response.status_code == 200

    def test_delete_visit_view_POST_new(self):
        visit = self.visit
        visit.Type_of = "wyrywanie"
        visit.status = "zaplanowana"
        visit.day_of_visit = datetime.today().date() + timedelta(days = 15)
        visit.save()
        path = reverse('visit_delete',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        response = VisitDeleteView(request,visit_id = visit.id)
        assert response.status_code == 200

    def test_cancel_visit_view_GET(self):   
        path = reverse('visit_cancel',kwargs={'visit_id':self.visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = VisitCancelView(request, visit_id = self.visit.id)
        assert response.status_code == 200

    def test_cancel_visit_view_POST(self): 
        path = reverse('visit_cancel',kwargs={'visit_id':self.visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = VisitCancelView(request, visit_id = self.visit.id)
        assert response.status_code == 200

    def test_revive_visit_view_GET(self):     
        path = reverse('visit_revive',kwargs={'visit_id':self.visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = VisitReviveView(request, visit_id = self.visit.id)
        assert response.status_code == 200

    def test_revive_visit_view_GET_change_date(self):
        visit = self.visit  
        path = reverse('visit_revive',kwargs={'visit_id':visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        visit.status = ' zmiana daty'
        visit.save()
        request.content_type = 'application/json'
        response = VisitReviveView(request, visit_id = visit.id)
        assert response.status_code == 200

    def test_revive_visit_view_POST_old(self):
        visit = self.visit   
        path = reverse('visit_revive',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        visit.day_of_visit = datetime.today().date() - timedelta(days = 1)
        visit.status = "odwołana"
        visit.save()
        request.content_type = 'application/json'
        response = VisitReviveView(request, visit_id = visit.id)
        assert response.status_code == 200

    def test_revive_visit_view_POST(self):
        visit = self.visit   
        path = reverse('visit_revive',kwargs={'visit_id':visit.id})
        request = self.factory.post(path)
        request.user =  self.user
        visit.day_of_visit = datetime.today().date()+ timedelta(days = 1)
        visit.status = "odwołana"
        visit.save()
        request.content_type = 'application/json'
        response = VisitReviveView(request, visit_id = visit.id)
        assert response.status_code == 200

    def test_visit_date_change_view_GET(self):
        path = reverse('visit_date_change',kwargs={'visit_id':self.visit.id})
        request = self.factory.get(path)
        request.user =  self.user
        request.content_type = 'application/json'
        response = VisitDateChangeView(request,visit_id = self.visit.id)
        assert response.status_code == 200

    def test_visit_date_change_view_POST(self):
        visit = self.visit
        visit.day_of_visit = datetime.today().date() + timedelta(days = 1)
        visit.time_of_the_visit = time(11,2)
        visit.time_end_visit = time(12,2)
        visit.status = "zaplanowana"
        visit.Type_of = "wyrywanie"
        visit.save()
        path = reverse('visit_date_change',kwargs={'visit_id':visit.id})
        request = self.factory.post(path,{'day_of_visit': datetime.today().date() + timedelta(days= 1), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(12, 12),})
        request.user =  self.user
        response = VisitDateChangeView(request, visit_id = visit.id)
        assert response.status_code == 200

    def test_visit_date_change_view_POST_wrong(self):
        visit = self.visit

        visit.Type_of = "wyrywanie"
        visit.save()
        path = reverse('visit_date_change',kwargs={'visit_id':visit.id})
        data = {'day_of_visit': datetime.today().date(), 'time_of_the_visit': time(11, 11), 'time_end_visit': time(9, 12), 'status': 'zaplanowana', 'Type_of': 'wizyta kontrolna', 'Dentist': self.dentist.id, 'Patient': self.patient.id,  'desc': '12311', 'cost': 123.0}
        request = self.factory.post(path,data = data)
        request.user =  self.user
        response = VisitDateChangeView(request,visit_id = visit.id)
        assert response.status_code == 200







        
















