from django.forms import ModelForm, DateInput, HiddenInput, TimeInput
from visit.models import Visit, tooth_healing_destruction
from tooth.models import Tooth
from account.models import Patient
from django import forms
from django.contrib.admin.widgets import AdminTimeWidget
from datetime import date, datetime
from tooth.widget import DateTimeWidget

PLANNED = 'zaplanowana'
FINISHED = 'odbyła sie'
UNAPROVED_BY_PATIENT = 'do zatwierdzenia przez pacjenta'
STATUS = (
        (PLANNED, 'Wizyta jest zaplanowana'),
        (FINISHED, 'Wizyta się odbyła'),
        (UNAPROVED_BY_PATIENT, 'do zatwierdzenia przez pacjenta')
)

class VisitForm(ModelForm):
  class Meta:
    model = Visit
    widgets = {
      'day_of_visit': DateInput(attrs={'type': 'date'},),
      'time_of_the_visit': TimeInput(attrs={'type': 'time'}, ),
      'time_end_visit': TimeInput(attrs={'type': 'time'}, ),
    }
    status = forms.ChoiceField(choices=STATUS)

    fields = '__all__'
  def __init__(self, *args, **kwargs):
    set_dentist = None
    set_patient = None
    curr_dentist = kwargs.pop('curr_dentist')
    if 'set_dentist' in kwargs:
      set_dentist = kwargs.pop('set_dentist')
    if 'set_patient' in kwargs:
      set_patient = kwargs.pop('set_patient')
    curr_patient = kwargs.pop('curr_patient')
    super(VisitForm, self).__init__(*args, **kwargs)


    if curr_dentist==None:
      self.fields['Patient'].initial = curr_patient
      self.fields['Patient'].widget = forms.HiddenInput()
      self.fields['desc'].widget = forms.HiddenInput()

      self.fields['Dentist'].queryset = curr_patient.dentist.all()
      self.fields['Dentist'].initial = curr_patient.dentist.first()    
      self.fields['Dentist'].empty_label = None
      self.fields['status'].initial = 'nie potwierdzona'
      self.fields['status'].widget= forms.HiddenInput()
      self.fields["Tooth_Repaired"].queryset = Tooth.objects.filter(patient =curr_patient) 

    else:
      if curr_patient !=None:
        self.fields['Patient'].initial = curr_patient
      self.fields['Patient'].queryset = Patient.objects.filter(dentist__in=[curr_dentist])
      self.fields['Dentist'].initial = curr_dentist
      self.fields['Dentist'].widget = forms.HiddenInput()

      self.fields['status'] = forms.ChoiceField(choices=STATUS)
      self.fields['status'].initial = 'Wizyta jest zaplanowana'
    self.fields['cost'].widget = forms.HiddenInput()      
    self.fields["cost"].required=False
    self.fields["desc"].required=False
    self.fields["Tooth_Repaired"].required=False
    self.fields["Tooth_Repaired"].widget = forms.HiddenInput()
    if not set_dentist == None:
      self.fields['Dentist'].initial = set_dentist
    elif not set_patient == None:
      self.fields['Patient'].initial = set_patient
  def save(self, commit=True):
    instance = forms.ModelForm.save(self, False)
    old_save_m2m = self.save_m2m
    def save_m2m():
        old_save_m2m()
        instance.Tooth_Repaired.clear()
        for toot in self.cleaned_data['Tooth_Repaired']:
            instance.Tooth_Repaired.add(toot)
    self.save_m2m = save_m2m
    instance.save()
    self.save_m2m()
    return instance  


class Visit_Edit_Form(ModelForm):
  class Meta:
    model = Visit
    fields = ('Type_of','desc','cost')
class Visit_patient_form(ModelForm):

  class Meta:
    model = Visit

    fields = ('Patient',)


class Visit_change_date_form(ModelForm):
  class Meta:
    model = Visit
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'day_of_visit': DateInput(attrs={'type': 'date'},),
      'time_of_the_visit': TimeInput(attrs={'type': 'time'}, ),
      'time_end_visit': TimeInput(attrs={'type': 'time'}, ),

    }

    fields = ('day_of_visit', 'time_of_the_visit', 'time_end_visit','Dentist')
  def __init__(self, *args, **kwargs):
    super(Visit_change_date_form, self).__init__(*args, **kwargs)
    self.fields['Dentist'].widget = forms.HiddenInput()

class tooths_healing_form(ModelForm):
    class Meta:

        model = tooth_healing_destruction
        fields = ('type_of', 'about_healing')
    def __init__(self, *args, **kwargs):
        super(tooths_healing_form, self).__init__(*args, **kwargs)
