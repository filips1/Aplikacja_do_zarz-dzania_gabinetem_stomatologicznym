from django.test import SimpleTestCase
from account.forms import PatientForm

class TestForms(SimpleTestCase):
    def test_patient_form_valid_data(self):
        form = PatientForm(data ={
            'First_Name': 'Zbigniew', 'Surname': 'Polak', 'phone_number': '44444444444', 'city': 'Poznań', 'adress': '60-166 Poznań Grunwaldzka 186', 'email_conversation': 'op@op.pl', 'age': 12
            })
        self.assertTrue(form.is_valid())
    def test_patient_form_invalid_data(self):
        form = PatientForm(data ={
            })
        self.assertFalse(form.is_valid())
