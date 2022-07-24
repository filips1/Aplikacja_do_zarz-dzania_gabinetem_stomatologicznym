from django.forms import ModelForm, DateInput, HiddenInput
from visit.models import Visit
from tooth.models import Tooth, Tooth_destructions
from account.models import Patient
from django import forms
from datetime import date, datetime




class DateTimeWidget(forms.DateTimeInput):
  class Media:
    js = ('js/jquery-ui-timepicker-addon.js',)
  def __init__(self, attrs=None):
    if attrs is not None:
      self.attrs = attrs.copy()
    else:
      self.attrs = {'class': 'datetimepicker'}

    if not 'format' in self.attrs:
        self.attrs['format'] = '%Y-%m-%d %H:%M'