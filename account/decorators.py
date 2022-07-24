from django.core.exceptions import PermissionDenied
from account.models import Dentist, Patient, Account, Receptionist
from django.shortcuts import redirect
from django.http import HttpResponseNotFound


def user_is_fully_registered(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if Dentist.objects.filter(account=user).exists() or Patient.objects.filter(account = user).exists() or Receptionist.objects.filter(account = user).exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('must_finish_registration')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def login_required_mk2(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            return redirect('must_authenticate')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def user_is_dentist(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_dentist:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def user_is_dentist_or_receptionist(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_dentist or user.is_receptionist:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def user_is_patient(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_dentist:
            return redirect('/')            
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def user_is_receptionist(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_receptionist:
            return function(request, *args, **kwargs)          
        else:
            return redirect('/')   

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_ajax_dec(function):
    def wrap(request, *args, **kwargs):
        if request.is_ajax(): 
            return function(request, *args, **kwargs)
        else:
            return HttpResponseNotFound()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap