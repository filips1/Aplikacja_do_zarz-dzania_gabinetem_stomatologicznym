from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from account.models import *

from django.shortcuts import render, redirect, get_object_or_404

class SpecialisationForm(forms.ModelForm):
    class Meta:
        model = Specialisation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        dentist = kwargs.pop('dentist')
        super(SpecialisationForm, self).__init__(*args, **kwargs)
        self.fields['dentist'].initial = dentist
        self.fields['dentist'].widget = forms.HiddenInput()

class LocationForm(forms.ModelForm):
    about = forms.CharField(required=False)
    class Meta:
        model = Location
        fields = ("name", "about", "location")




class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text='Email jest wyamgany do założenia konta')
    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2","is_dentist","profile_pic",'is_receptionist')
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['profile_pic'].required=False


class DentistForm(forms.ModelForm):
    class Meta:
        model = Dentist
        fields = ["First_Name", "Surname", "phone_number", "city","clinic_adress"]


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["First_Name", "Surname", "phone_number", "city" , "adress", "email_conversation","age" ]

class ReceptionistForm(forms.ModelForm):
    class Meta:
        model = Receptionist
        fields = ["First_Name", "Surname", "phone_number"]




class AccountAuthenticationForm(forms.ModelForm):
    
    password = forms.CharField(label = 'Password', widget=forms.PasswordInput)
    class Meta:
        model = Account
        fields = ('username', 'password')

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            if not authenticate(username = username, password = password):
                raise forms.ValidationError("Podano błędne dane logowania")

class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('email', 'username')

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
            except Account.DoesNotExist:
                return email
            raise forms.ValidationError('Email "%s"jest już w użyciu' % email)

    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
            except Account.DoesNotExist:
                return username
            raise forms.ValidationError('Username "%s"jest już w użyciu' % username)


class AccountImageForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("profile_pic",)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('dentist','account','body')
    def __init__(self, *args, **kwargs):
        dentist = kwargs.pop('dentist')
        account = kwargs.pop('account')
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['dentist'].initial = dentist
        self.fields['account'].initial = account
        self.fields['dentist'].widget = forms.HiddenInput()
        self.fields['account'].widget = forms.HiddenInput()



class AchievementsForm(forms.ModelForm):
    class Meta:
        model = Achievements
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        dentist = kwargs.pop('dentist')
        super(AchievementsForm, self).__init__(*args, **kwargs)
        self.fields['dentist'].initial = dentist
        self.fields['dentist'].widget = forms.HiddenInput()


class WeekdayHoursOpenForm(forms.ModelForm):
    class Meta:
        model = WeekdayHoursOpen
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        dentist = kwargs.pop('dentist')
        super(WeekdayHoursOpenForm, self).__init__(*args, **kwargs)
        self.fields['dentist'].initial = dentist
        self.fields['dentist'].widget = forms.HiddenInput()

class CennikForm(forms.ModelForm):
    class Meta:
        model = Cennik
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        dentist = kwargs.pop('dentist')
        super(CennikForm, self).__init__(*args, **kwargs)
        self.fields['dentist'].initial = dentist
        self.fields['dentist'].widget = forms.HiddenInput()



class ImagesForm(forms.ModelForm):
    Image = forms.ImageField()
    class Meta:
        model = Images_aboutme
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        dentist = kwargs.pop('dentist')
        super(ImagesForm, self).__init__(*args, **kwargs)
        self.fields['dentist'].initial = dentist
        self.fields['dentist'].widget = forms.HiddenInput()


class AboutMeForm(forms.ModelForm):
     class Meta:
        model = Dentist
        fields = ('about_me',)

