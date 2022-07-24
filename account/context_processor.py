from account.models import Dentist, Patient, Account, Wiadomosc, Receptionist, Location

from django.shortcuts import render, redirect, get_object_or_404


def base_context(request):
        user = request.user
        context = {}
        if user.is_authenticated:
            if Dentist.objects.filter(account=user).exists() or Patient.objects.filter(account = user).exists() or Receptionist.objects.filter(account = user).exists():
                context['has_account'] = True
                if user.is_dentist:
                    dentist = get_object_or_404(Dentist,account = user)
                    context['dentist'] = dentist
                    location = Location.objects.filter(dentist__account = user)
                    context['my_locations'] = location
                elif user.is_receptionist:
                    receptionist = get_object_or_404(Receptionist, account = user)
                    context['receptionist_main'] = receptionist
                    location = Location.objects.filter(receptionist__account = user)
                    context['my_locations'] = location

            else:
                context['has_account'] = False

            context['infos'] = Wiadomosc.objects.filter(target = user).count()
        return context 

