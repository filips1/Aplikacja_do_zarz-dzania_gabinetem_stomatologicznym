from django.forms import ModelForm, DateInput, HiddenInput
from visit.models import Visit
from tooth.models import Tooth, Tooth_destructions, Tooth_rentgen
from visit.models import tooth_healing_destruction
from account.models import Patient
from django import forms
from datetime import date, datetime
from tooth.widget import DateTimeWidget
from django.shortcuts import render,  get_object_or_404,redirect


class tooth_destroy_form(ModelForm):
  class Meta:
    model = Tooth_destructions
    # datetime-local is a HTML5 input type, format to make date time show on fields
    
    fields = ('tooth','status','side', 'front','depth')
  def __init__(self, *args, **kwargs):
    tooth = kwargs.pop('tooth')
    super(tooth_destroy_form, self).__init__(*args, **kwargs)
    self.fields['tooth'].initial = tooth
    self.fields['tooth'].widget = forms.HiddenInput()

class tooth_rentgen_form(ModelForm):
    class Meta:

        model = Tooth_rentgen
        fields = '__all__'

    def __init__(self, *args, **kwargs):
      tooth_id = kwargs.pop('tooth_id')
      super(tooth_rentgen_form, self).__init__(*args, **kwargs)
      tooth = get_object_or_404(Tooth, id = tooth_id)
      self.fields['tooth'].initial=tooth




class tooth_healing_form_new(ModelForm):
    class Meta:

        model = tooth_healing_destruction
        fields = ('type_of', 'about_healing', 'date_of_fixing', 'tooth_destructions')
        widgets = {
      'date_of_fixing': DateInput(attrs={'type': 'date'}),
      }
    def __init__(self, *args, **kwargs):
      td_id = kwargs.pop('td_id')
      super(tooth_healing_form_new, self).__init__(*args, **kwargs)
      td = get_object_or_404(Tooth_destructions, id = td_id)
      self.fields['tooth_destructions'].initial=td
      self.fields['tooth_destructions'].widget= forms.HiddenInput()







