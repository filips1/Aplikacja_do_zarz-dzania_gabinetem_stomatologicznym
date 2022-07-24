from datetime import datetime, date
from django.shortcuts import render,  get_object_or_404,redirect
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from django.utils.timezone import timedelta
import calendar
from django.urls import reverse
from django.contrib.auth import login, authenticate,logout
from django.db.models import Q

from django.http import HttpResponse
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from tooth.views import CheckifVisitUserWithPatient

from visit.models import Visit, tooth_healing_destruction
from visit.utils import Calendar
from visit.forms import VisitForm, Visit_change_date_form, Visit_Edit_Form
from django.http import HttpResponse, HttpResponseRedirect
from account.models import *
from account.decorators import user_is_fully_registered, login_required_mk2, user_is_dentist, user_is_patient, is_ajax_dec
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from datetime import datetime, timedelta, time, date
from dateutil.relativedelta import *
from tooth.views import CheckToothStatusView
from tooth.models import Tooth, Tooth_destructions
from account.decorators import user_is_fully_registered, login_required_mk2, user_is_dentist, user_is_patient, is_ajax_dec
from django.http import Http404
from account.decorators import *

class CalendarView(generic.ListView):
    model = Visit
    template_name = 'visit/calendar.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        if self.kwargs.get("dentist_id"):
            user = self.request.user
            if not user.is_receptionist:
                return redirect('calendar')
            receptionist = get_object_or_404(Receptionist, account = user)
            dentist_id  = self.kwargs.get("dentist_id")
            print(dentist_id)
            dentist = get_object_or_404(Dentist, id = dentist_id)
            if receptionist.dentist.filter(id = dentist.id):
                a = dentist.account.id
                context['dentist_id'] = dentist.id
                context['receptionist'] = True
            else:
                return redirect('/')
        else:
            if self.request.user.is_receptionist:
                return redirect('/')
            a=self.request.user.id
        d = get_date(self.request.GET.get('month', None))
        if Dentist.objects.filter(account=a).exists():
            curr_dentist = get_object_or_404(Dentist, account = a)
            context['curr_dentist_patients'] = Patient.objects.filter(dentist__in=[curr_dentist])
        else:
            curr_dentist = None

        if Account.objects.filter(id = a).exists():
            user = get_object_or_404(Account, id=a)
            if user.is_dentist == False:
                if Patient.objects.filter(account=user).exists():
                    curr_patient = get_object_or_404(Patient, account = a)
                    context['is_patient'] = True
                else:
                    curr_patient = None
            else:
                curr_patient = None 

        else:
            return redirect('/')

        cal = Calendar(d.year, d.month)

        html_cal = cal.formatmonth(a=curr_dentist,b = curr_patient,withyear=True)

        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()



def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

@login_required
@user_is_fully_registered
def VisitUnaprovedShowView(request,dentist_id = None):
    user = request.user

    context = {}

    if Dentist.objects.filter(account=user).exists():
        curr_dentist = get_object_or_404(Dentist, account = user)
        visits = Visit.objects.filter(Q(Dentist = curr_dentist,status = 'nie potwierdzona')|Q(Dentist = curr_dentist, status = 'do zatwierdzenia przez pacjenta')).order_by('day_of_visit')
    elif Patient.objects.filter(account = user).exists():
        curr_patient = get_object_or_404(Patient, account = user)
        visits = Visit.objects.filter(Q(Patient = curr_patient,status = 'nie potwierdzona')|Q(Patient = curr_patient, status = 'do zatwierdzenia przez pacjenta')).order_by('day_of_visit')
    elif dentist_id != None:
        curr_dentist = get_object_or_404(Dentist, id = dentist_id)
        receptionist = get_object_or_404(Receptionist, account = user, dentist__in = [curr_dentist])
        context['dentist_id'] = curr_dentist.id
        visits = Visit.objects.filter(Q(Dentist = curr_dentist,status = 'nie potwierdzona')|Q(Dentist = curr_dentist, status = 'do zatwierdzenia przez pacjenta')).order_by('day_of_visit')
    context['visits']=visits
    return render(request,'visit/unaproved.html',context)

@login_required
@user_is_fully_registered
def VisitApprove(request,visit_id, dentist_id = None):
    user = request.user
    context = {}
    if not CheckifVisitUserWithPatient(visit_id, user.id):
        return redirect('/')
    visit = get_object_or_404(Visit,id = visit_id)
    if visit.status == "do zatwierdzenia przez pacjenta":
        visit.status = 'zaplanowana'
        visit.save()
        if not (user.is_dentist and user.is_receptionist):
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "zaplanowana wizyta na"+ str(visit.day_of_visit) + str(visit.time_of_the_visit) + " została zatwierdzona przez pacjenta", target = visit.Dentist.account)
            new_info.save()

    elif visit.status == 'nie potwierdzona'  and user.is_dentist or user.is_receptionist:
        visit.status = 'zaplanowana'
        visit.save()
        if visit.Patient.account:
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "zaplanowana wizyta na"+ str(visit.day_of_visit) + str(visit.time_of_the_visit) + " została zatwierdzona przez dentystę", target = visit.Patient.account)
            new_info.save()
    visit_remove_special(visit)
    if request.user.is_receptionist:
        return redirect('unaproved',dentist_id)
    return redirect('unaproved')


def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
    overlap = False
    if new_start == fixed_end or new_end == fixed_start:    
        overlap = False
    elif (new_start >= fixed_start and new_start <= fixed_end) or (new_end >= fixed_start and new_end <= fixed_end): 
        overlap = True
    elif new_start <= fixed_start and new_end >= fixed_end:
        overlap = True

    return overlap

def visit_remove_special(new_visit):

    visits = Visit.objects.filter(Q(day_of_visit=new_visit.day_of_visit, status='nie potwierdzona')|Q(day_of_visit=new_visit.day_of_visit, status='do zatwierdzenia przez pacjenta'))
    
    if visits.exists():
        for visit in visits:
            if new_visit.Dentist == visit.Dentist:
                if new_visit!= visit:
                    if new_visit.check_overlap(visit.time_of_the_visit, visit.time_end_visit, new_visit.time_of_the_visit, new_visit.time_end_visit):
                        visit.delete()
    print("halo")
    return True


@login_required
@user_is_fully_registered
def VisitReject(request,visit_id,dentist_id = None):
    user = request.user
    context = {}
    if not CheckifVisitUserWithPatient(visit_id, user.id):
        return redirect('/')
    visit = get_object_or_404(Visit,id = visit_id)
    if visit.status == "do zatwierdzenia przez pacjenta":
        if not (user.is_dentist and user.is_receptionist):
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "zaplanowana wizyta na"+ str(visit.day_of_visit) + str(visit.time_of_the_visit) + "został  odrzucona przez pacjenta", target = visit.Dentist.account)
            new_info.save()
        visit.delete()
    elif visit.status == 'nie potwierdzona' and user.is_dentist or user.is_receptionist:
        if visit.Patient.account:
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "zaplanowana wizyta na"+ str(visit.day_of_visit) + str(visit.time_of_the_visit) + " została odrzucona przez dentystę", target = visit.Patient.account)
            new_info.save()
        visit.delete()
    if request.user.is_receptionist:
        return redirect('unaproved',dentist_id)
    return redirect('unaproved')
    
@login_required
def InfoView(request):
    user = request.user
    context = {}
    Info = Wiadomosc.objects.filter(target = user)
    data = []


    context['info'] = Info
    return render(request,'visit/informations.html',context)

@login_required
def InfoSeenView(request, info_id):
    user = request.user
    context = {}
    if Wiadomosc.objects.filter(target = user, id = info_id).exists() or Wiadomosc.objects.filter(target = user, id = info_id).exists():
        Info = get_object_or_404(Wiadomosc, id = info_id)
        Info.czytano = True
        Info.save()
    return redirect('info')

@login_required
def InfoDeleteView(request, info_id):
    user = request.user
    context = {}
    if Wiadomosc.objects.filter(target = user, id = info_id).exists() or Wiadomosc.objects.filter(target = user, id = info_id).exists():
        Info = get_object_or_404(Wiadomosc, id = info_id)
        Info.delete()
    return redirect('info')







@is_ajax_dec
@login_required
@user_is_fully_registered
@user_is_dentist
def new_visit_view(request, id=None):
 
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    datatimes = first_day_visit(dentist_id = dentist.id)
    if id!= None:
        patient = get_object_or_404(Patient, id = id)

    freetimedays = []
    i = 1
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    for i in range(7):
        if not str(i) in weekday:
            if i == 7:
                freetimedays.append(0)
            else:
                freetimedays.append(i)
    if request.method == 'POST':
        if id == None:
            form = VisitForm( request.POST,curr_dentist=dentist,curr_patient=None)
        else:
            form = VisitForm( request.POST,curr_dentist=dentist,curr_patient=None, set_patient = patient) 
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            data['form_is_fine'] = True
            print(form.instance.id)
            new_visit= get_object_or_404(Visit, id = form.instance.id)
            if new_visit.Patient.account!= None:
                if form.instance.status =='zaplanowana':
                    visit_remove_special(form.instance)
                    a = (form.instance.day_of_visit - date.today()).days
                    if a == 1 or a == 0:
                        new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Przypominam o zbliżającej się wizycie"+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit), target = form.instance.Patient.account )
                        new_info.save()
                    else:
                        new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Nowa wizyta została zaplanowana na "+str(form.instance.day_of_visit) +" od godz" + str(form.instance.time_of_the_visit) + "do godz." +str(form.instance.time_end_visit), target = form.instance.Patient.account )
                        new_info.save()
                elif form.instance.status =='do zatwierdzenia przez pacjenta':
                    new_info = Wiadomosc(date_of_change = datetime.now(), special_data=new_visit.id, type_of = "zatwierdzenie", desc = "Dentysta zaproponował wizytę na "+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit), target = form.instance.Patient.account )
                    new_info.save()
            if form.instance.Type_of=="leczenie":
                return redirect('check_tooth_status',visit_id= form.instance.id)
            elif form.instance.Type_of =="wyrywanie":

                return redirect('add_tooth_to_visit', visit_id = form.instance.id)
            else:
                data['refresh'] = True
                cennik = get_object_or_404(Cennik, dentist = form.instance.Dentist)
                visit = form.instance
                visit.cost = cennik.wizyta_kontrolna
                print(cennik.wizyta_kontrolna)
                visit.save()
        else:
            data['form_is_fine'] = False 
    else:
        if id == None:
            form = VisitForm(curr_dentist=dentist,curr_patient=None)
        else:
            form = VisitForm(curr_dentist=dentist,curr_patient=None, set_patient = patient)
    context["new_visit"] = True              
    context['form'] = form
    context['new_visit_auto'] = True
    context['time'] = datatimes.strftime('%H:%M')
    context['date'] = datatimes.strftime('%Y-%m-%d')
    context['weekends'] = freetimedays
    if datatimes.hour == 23:
        context['time_plus_hour'] = '23:59'
    else:
        context['time_plus_hour'] = (datatimes + timedelta(hours = 1)).strftime('%H:%M')
    data['html_form'] = render_to_string('visit/visit_new_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)

@is_ajax_dec
@login_required
@user_is_fully_registered
@user_is_receptionist
def new_visit_receptionist_view(request, dentist_id=None, patient_id = None):
 
    context = {}
    data = dict()
    user = request.user
    receptionist = get_object_or_404(Receptionist, account = user)
    dentist = receptionist.dentist.filter(id = dentist_id).first()
    datatimes = first_day_visit(dentist_id = dentist.id)
    freetimedays = []
    i = 1
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    for i in range(7):
        if not str(i) in weekday:
            if i == 7:
                freetimedays.append(0)
            else:
                freetimedays.append(i)

    if request.method == 'POST':
        if patient_id!=None:
            form = VisitForm( request.POST,curr_dentist=dentist,curr_patient=None, set_patient = patient_id)
        else:
            form = VisitForm( request.POST,curr_dentist=dentist,curr_patient=None)
        if form.is_valid():
            print(form.cleaned_data)
            print(form.instance.day_of_visit)
            form.save()
            data['form_is_fine'] = True
            print(form.instance.id)
            new_visit= get_object_or_404(Visit, id = form.instance.id)
            if new_visit.Patient.account!= None:
                if form.instance.status =='zaplanowana':
                    visit_remove_special(form.instance)
                    a = (form.instance.day_of_visit - date.today()).days
                    if a == 1 or a == 0:
                        new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Przypominam o zbliżającej się wizycie"+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit), target = form.instance.Patient.account )
                        new_info.save()
                    else:
                        new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Nowa wizyta została zaplanowana na "+str(form.instance.day_of_visit) +" od godz" + str(form.instance.time_of_the_visit) + "do godz." +str(form.instance.time_end_visit), target = form.instance.Patient.account )
                        new_info.save()
                elif form.instance.status =='do zatwierdzenia przez pacjenta':
                    new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "Dentysta zaproponował wizytę na "+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit), target = form.instance.Patient.account )
                    new_info.save()
            if form.instance.Type_of=="leczenie":
                return redirect('check_tooth_status',visit_id= form.instance.id)
            elif form.instance.Type_of =="wyrywanie":
                return redirect('add_tooth_to_visit', visit_id = form.instance.id)
            else:
                data['refresh'] = True
                cennik = get_object_or_404(Cennik, dentist = form.instance.Dentist)
                visit = form.instance
                visit.cost = cennik.wizyta_kontrolna
                print(cennik.wizyta_kontrolna)
                visit.save()
        else:
            data['form_is_fine'] = False 
            print(form.cleaned_data)
            print(form.errors)
            if patient_id!=None:
                form = VisitForm(curr_dentist=dentist,curr_patient=None, set_patient = patient_id)
            else:
                form = VisitForm(curr_dentist=dentist,curr_patient=None)
    else:
        if patient_id!=None:
            form = VisitForm(curr_dentist=dentist,curr_patient=None, set_patient = patient_id)
        else:
            form = VisitForm(curr_dentist=dentist,curr_patient=None)
    context['id'] = dentist.id
    context["receptionist_new"] = True              
    context['form'] = form
    context['new_visit_auto'] = True
    context['time'] = datatimes.strftime('%H:%M')
    context['date'] = datatimes.strftime('%Y-%m-%d')
    context['weekends'] = freetimedays
    if datatimes.hour == 23:
        context['time_plus_hour'] = '23:59'
    else:
        context['time_plus_hour'] = (datatimes + timedelta(hours = 1)).strftime('%H:%M')
    data['html_form'] = render_to_string('visit/visit_new_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)

@is_ajax_dec
@login_required
@user_is_fully_registered
@user_is_patient
def new_visit_dentist_chosen_view(request,id):
 
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, id = id)
    patient = get_object_or_404(Patient, account = user)
    datatimes = first_day_visit(dentist_id = dentist.id)
    freetimedays = []
    i = 1
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    for i in range(7):
        if not str(i) in weekday:
            if i == 7:
                freetimedays.append(0)
            else:
                freetimedays.append(i)
    if not dentist in patient.dentist.all():
        patient.dentist.add(dentist)
        patient.save()
    if request.method == 'POST':
        form = VisitForm( request.POST,set_dentist =  dentist,curr_patient=patient, curr_dentist=None)
        if form.is_valid():
            form.save()
            data['form_is_fine'] = True
            a = (form.instance.day_of_visit - date.today()).days
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "Pacjent zaproponował wizytę na "+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit), target = form.instance.Dentist.account )
            new_info.save()

            if form.instance.Type_of !="wizyta kontrolna":
                return redirect('add_tooth_to_visit', visit_id = form.instance.id)
            else:
                data['refresh'] = True
                cennik = get_object_or_404(Cennik, dentist = form.instance.Dentist)
                visit = form.instance
                visit.cost = cennik.wizyta_kontrolna
                visit.save()
        else:
            data['form_is_fine'] = False   
        a = []
        dentist = Dentist.objects.all()
        for d in dentist:
            if d in patient.dentist.all():
                a.append(True)
            else:
                a.append(False)
        print(dentist)
        dentist = zip(dentist,a)
        context['dentist'] = dentist
        data['html_dentist_list'] = render_to_string('account/snippets/dentist_list.html', {
                        'dentist': dentist
                    })


        return JsonResponse(data) 
    else:
        form = VisitForm(set_dentist=dentist,curr_patient=patient, curr_dentist=None)
        context["isd"] = True

    data['modal'] = "#visit_tooth_modal"
    context['patient_create'] = True
    context['form'] = form
    context['id'] = id
    context['new_visit_auto'] = True
    context['time'] = datatimes.strftime('%H:%M')
    context['date'] = datatimes.strftime('%Y-%m-%d')
    context['weekends'] = freetimedays
    if datatimes.hour == 23:
        context['time_plus_hour'] = '23:59'
    else:
        context['time_plus_hour'] = (datatimes + timedelta(hours = 1)).strftime('%H:%M')
    data['html_form'] = render_to_string('visit/visit_new_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)


@is_ajax_dec
@login_required
@user_is_fully_registered
@user_is_patient
def new_visit_by_patient_view(request):
    context = {}
    data = dict()
    user = request.user
    patient = get_object_or_404(Patient, account = user)
    a = patient.dentist.all()
    a = a.first()
    datatimes = first_day_visit(dentist_id = a.id)
    print(datatimes)
    freetimedays = []
    i = 1
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = a)
    weekday = opentime.open_days
    for i in range(7):
        if not str(i) in weekday:
            if i == 7:
                freetimedays.append(0)
            else:
                freetimedays.append(i)
    context['patient_create'] = True
    if request.method == 'POST':
        form = VisitForm( request.POST,curr_patient=patient, curr_dentist=None)
        if form.is_valid():
            form.save()
            data['form_is_fine'] = True
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "zatwierdzenie", desc = "Pacjent zaproponował wizytę na "+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit), target = form.instance.Dentist.account )
            new_info.save()
            if form.instance.Type_of !="wizyta kontrolna":
                return redirect('add_tooth_to_visit', visit_id = form.instance.id)
            else:
                data['refresh'] = True
                cennik = get_object_or_404(Cennik, dentist = form.instance.Dentist)
                visit = form.instance
                visit.cost = cennik.wizyta_kontrolna
                visit.save()
        else:
            data['form_is_fine'] = False 
            print(form.errors)  
    else:
        form = VisitForm(curr_dentist=None,curr_patient=patient)
    context['form'] = form

    context['new_visit_auto'] = True
    context['time'] = datatimes.strftime('%H:%M')
    context['date'] = datatimes.strftime('%Y-%m-%d')
    context['weekends'] = freetimedays
    if datatimes.hour == 23:
        context['time_plus_hour'] = '23:59'
    else:
        context['time_plus_hour'] = (datatimes + timedelta(hours = 1)).strftime('%H:%M')
    data['html_form'] = render_to_string('visit/visit_new_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)


def CheckifVisitUser(visit_id,user_id):
    curr_visit = get_object_or_404(Visit,id = visit_id)
    user = get_object_or_404(Account, id = user_id)
    if Receptionist.objects.filter(account = user, dentist__in = [curr_visit.Dentist]).exists() or curr_visit.Dentist.account == user:
        return True
    return False

def CheckifVisitUserWithPatient(visit_id,user_id):
    curr_visit = get_object_or_404(Visit,id = visit_id)
    user = get_object_or_404(Account, id = user_id)
    if Receptionist.objects.filter(account = user, dentist__in = [curr_visit.Dentist]).exists() or curr_visit.Dentist.account == user or curr_visit.Patient.account == user:
        return True
    return False
    




@is_ajax_dec
@login_required
@user_is_fully_registered
def VisitEditNew(request,visit_id):
    user = request.user
    context = {}
    data = dict()
    if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
        raise Http404
    curr_visit = get_object_or_404(Visit,id = visit_id)
    curr_dentist = curr_visit.Dentist
    curr_visit_type = curr_visit.Type_of
    if request.POST:
        form = Visit_Edit_Form( request.POST, instance=curr_visit)
        form.Dentist = curr_dentist
        if form.is_valid():
            if curr_visit_type != form.instance.Type_of:
                if form.instance.Type_of == 'wyrywanie' or form.instance.Type_of == 'wizyta kontrolna':
                    tooth_healing_destruction.objects.filter(visit = form.instance).delete()
                    if form.instance.Type_of =='wizyta kontrolna':
                        form.instance.Tooth_Repaired.clear()

            form.save()
            data['form_is_fine'] = True
            data['refresh'] = True
        else:
            data['form_is_fine'] = False 
    else:
        form = Visit_Edit_Form(instance=curr_visit)
    context['form'] = form
    context['edit'] = True
    context['id'] = visit_id
    data['html_form'] = render_to_string('visit/visit_new_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)
#    return render(request, 'visit/visit.html',context )
@is_ajax_dec
@login_required
@user_is_fully_registered
def VisitDeleteView(request, visit_id):
    user = request.user
    context = {}
    data = dict()
    if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
        raise Http404
    curr_visit = get_object_or_404(Visit,id = visit_id)
    curr_dentist = curr_visit.Dentist
    if request.method == 'POST':
        if curr_visit.status == "odbyła sie":
            if curr_visit.Type_of == "leczenie":
                th = tooth_healing_destruction.objects.filter(visit = curr_visit, tooth_destructions__healed = True)
                for t in th:
                    td = t.tooth_destructions
                    if tooth_healing_destruction.objects.filter(tooth_destructions = td, visit__status ='odbyła sie' ).count() == 1:
                        td.healed = False
                        td.save()
        elif curr_visit.status != "odwołana" and curr_visit.Patient.account!=None:
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "usunięcie", desc = "Wizyta zaplanowana na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została usunięta przez dentystę", target = curr_visit.Patient.account )
            new_info.save()

        curr_visit.delete()
        data['form_is_fine'] = True
        data['refresh'] = True
    else:
        context['visit'] = curr_visit
        data['html_form'] = render_to_string('visit/visit_delete.html',
                context,
                request=request,
        )
    return JsonResponse(data)
@is_ajax_dec
@login_required
@user_is_fully_registered
def VisitCancelView(request, visit_id):
    user = request.user
    context = {}
    data = dict()
    if not CheckifVisitUserWithPatient(visit_id = visit_id, user_id= user.id):
        raise Http404
    curr_visit = get_object_or_404(Visit, id = visit_id)
    if request.method == 'POST':
        if request.user.is_dentist or request.user.is_receptionist:
            print("HALOSSAFLK")
            if curr_visit.Patient.account!=None:
                new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "usunięcie", desc = "Wizyta zaplanowana na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została odwołana przez dentystę", target = curr_visit.Patient.account )
                new_info.save()
            curr_visit.status = 'odwołana'
            curr_visit.save()
        else:
            curr_visit.status = 'odwołana przez pacjenta'
            new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "odwołanie", desc = "Wizyta zaplanowana na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została odwołana przez pacjenta", target = curr_visit.Dentist.account )
            new_info.save()
        curr_visit.save()
        data['form_is_fine'] = True
        data['refresh'] = True
    else:
        context['cancel'] = True
        context['visit'] = curr_visit
        data['html_form'] = render_to_string('visit/visit_delete.html',
                context,
                request=request,
        )
    return JsonResponse(data)
@is_ajax_dec
@login_required
@user_is_fully_registered
def VisitReviveView(request, visit_id):
    user = request.user
    context = {}
    data = dict()
    if not CheckifVisitUserWithPatient(visit_id = visit_id, user_id= user.id):
        raise Http404
    curr_visit = get_object_or_404(Visit, id = visit_id)
    today = datetime.today().date()
    time = datetime.now().time()
    if request.method == 'POST':
        if (curr_visit.day_of_visit < today) or (curr_visit.day_of_visit == today and curr_visit.time_end_visit < time):
            curr_visit.status = 'odbyła sie'
        else:
            if curr_visit.status == 'odwołana':
                if  curr_visit.Patient.account!=None:
                    new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Wizyta zaplanowana na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została przywrócona przez dentystę", target = curr_visit.Patient.account )
                    new_info.save()    
            else:
                new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Wizyta zaplanowana na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została przywrócona przez pacjenta", target = curr_visit.Dentist.account )
                new_info.save() 
            curr_visit.status = 'zaplanowana'

        curr_visit.save()
        data['form_is_fine'] = True
        data['refresh'] = True
    else:
        if curr_visit.status == ' zmiana daty' or curr_visit.status == 'zmiana daty przez pacjenta':
            context['accept'] = True
        else:    
            context['revive'] = True
        context['visit'] = curr_visit
        data['html_form'] = render_to_string('visit/visit_delete.html',
                context,
                request=request,
        )
    return JsonResponse(data)

@is_ajax_dec
@login_required
@user_is_fully_registered
def VisitDateChangeView(request, visit_id):
    user = request.user
    context = {}
    data = dict()
    if not CheckifVisitUserWithPatient(visit_id = visit_id, user_id= user.id):
        raise Http404
    curr_visit = get_object_or_404(Visit, id=visit_id)
    if request.POST:
        form = Visit_change_date_form( request.POST,instance=curr_visit)
        if form.is_valid():        
            new_visit = form.save(commit=False)
            if request.user.is_dentist or request.user.is_receptionist:
                new_visit.status = ' zmiana daty'
                if new_visit.Patient.account!=None:
                    new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Data wizyty zaplanowanej na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została zmieniona na"+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit) +"przez dentystę", target = form.instance.Patient.account )
                    new_info.save() 
            else:
                new_visit.status = 'zmiana daty przez pacjenta'
                new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Data wizyty zaplanowanej na "+str(curr_visit.day_of_visit) + " od godz" +str(curr_visit.time_of_the_visit)+ "do godz." +str(curr_visit.time_end_visit) +"została zmieniona na"+str(form.instance.day_of_visit) + " od godz" +str(form.instance.time_of_the_visit)+ "do godz." +str(form.instance.time_end_visit) +"przez pacjenta", target = form.instance.Dentist.account )
                new_info.save() 
            new_visit.save()
            data['form_is_fine'] = True
            data['refresh'] = True
   
        else:
            data['form_is_fine'] = False 
    else:
        form = Visit_change_date_form(instance=curr_visit)
    context['form'] = form
    context['date_change'] = True
    context['id'] = visit_id
    data['html_form'] = render_to_string('visit/visit_new_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)

@is_ajax_dec
def get_possible_hours(request, dates, dentist_id, length):
    length = int(length)
    print("length " + str(length))
    user = request.user
    context = {}
    data = dict()

    dentist = get_object_or_404(Dentist,id = dentist_id)
    visits = Visit.objects.filter(Q(day_of_visit = dates, Dentist = dentist, status = 'zaplanowana')|Q(day_of_visit = dates, Dentist = dentist, status = 'odbyła sie')).order_by("time_of_the_visit")
    first_v = visits.first()
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    open_hour = opentime.start_hour
    close_hour = opentime.end_hour
    now = datetime(2020,1,1,open_hour.hour,open_hour.minute,0,0)

    now_plus_h = now + timedelta(minutes = length)
    endv = 1
    h = "j"
    a = []
    b = []
    c = []

    if visits.exists():
        for visit in visits:
            time_of_curr = visit.time_of_the_visit
            if endv and now_plus_h.time() <= time_of_curr and now_plus_h.time() <= close_hour :
                c.append(now.strftime('%H:%M'))
                if now.minute < 15:
                    now = datetime.combine(now.date(),time(now.hour,15,0,0))
                elif now.minute < 30:
                    now = datetime.combine(now.date(),time(now.hour,30,0,0))
                elif now.minute < 45:
                    now = datetime.combine(now.date(),time(now.hour,45,0,0))
                else:
                    now = datetime.combine(now.date(),time(now.hour,0,0,0))+ timedelta(hours = 1)
                now_plus_h = now + timedelta(minutes= length)
                print(now_plus_h)
                print(now) 
            while (now_plus_h.time() <= time_of_curr and now_plus_h.time() <= close_hour ):
                print("while  now_h"+str(now_plus_h))
                print("while now" + str(now)) 
                c.append(now.strftime('%H:%M')) 
                now =  now + timedelta(minutes = 15)
                now_plus_h = now_plus_h + timedelta(minutes= 15)

            now = datetime.combine(now.date(),visit.time_end_visit)
            now_plus_h = now + timedelta(minutes= length)
            endv = True
        print(now)  
        if(now + timedelta(minutes= length)).time() <= close_hour:
            c.append(now.strftime('%H:%M'))
            if now.minute < 15:
                now = datetime.combine(now.date(),time(now.hour,15,0,0))
            elif now.minute < 30:
                now = datetime.combine(now.date(),time(now.hour,30,0,0))
            elif now.minute < 45:
                now = datetime.combine(now.date(),time(now.hour,45,0,0))
            else:
                now = datetime.combine(now.date(),time(now.hour,0,0,0))+ timedelta(hours = 1)       

    while True:
        if (now + timedelta(minutes= length)).time() > close_hour:
            break
        c.append(now.strftime('%H:%M'))
        now = now + timedelta(minutes= 15)
    data['first'] = c[0]
    times = datetime.strptime(c[0],'%H:%M') + timedelta(minutes= length)
    data['end_hour'] = times.strftime('%H:%M')
    data['times'] = c
    data['worked'] = "True"
    return JsonResponse(data)
@is_ajax_dec
def update_fin_hour(request,times,length):
    date_time_str = '2018-06-29 '
    time_sec = ':0.0'

    times = date_time_str + times + time_sec
    user = request.user
    context = {}
    data = dict()
    times = datetime.strptime(times,'%Y-%m-%d %H:%M:%S.%f')
    print(times.hour)

    visit_end_time = times + timedelta(minutes= int(length))
    visit_end_time = visit_end_time.time()
    if visit_end_time.hour == 0:
        visit_end_time = time(23,59,0,0)

    data['end_time'] = visit_end_time.strftime('%H:%M')
    return JsonResponse(data)

def first_day_visit(dentist_id):
    today = datetime.today()
    dentist = get_object_or_404(Dentist, id = dentist_id)
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    open_hour = opentime.start_hour
    close_hour = opentime.end_hour
    if today.time() > close_hour:
        today = datetime(today.year,today.month,today.day,open_hour.hour,open_hour.minute,0,0) + timedelta(days = 1)
    elif open_hour > today.time():
        today = datetime(today.year,today.month,today.day,open_hour.hour,open_hour.minute,0,0)
    time_plus = today + timedelta(hours = 1)
    print(today)

    print(Visit.objects.filter(Q(Dentist = dentist, time_of_the_visit__gt = time_plus.time()  ) & Q(Dentist = dentist, time_end_visit__lt = time_plus.time()))) 
    visits = Visit.objects.filter( Dentist = dentist, status = 'zaplanowana')
    while True:
        if not str(today.date().isoweekday()) in weekday or time_plus.time() >= close_hour:
            today = datetime(today.year, today.month, today.day,open_hour.hour,open_hour.minute,0,0) + timedelta(days = 1)
            time_plus = today + timedelta(hours = 1)
        else:
            visit = visits.filter(day_of_visit = today.date()).order_by("time_of_the_visit")
            print(today)
            if visits.exists():
                for v in visit:
                    if v.time_of_the_visit >= time_plus.time():
                        return today
                    else:
                        print(today)
                        today = datetime.combine(today.date(),v.time_end_visit)
                        time_plus = today + timedelta(hours= 1)

            if time_plus.time() <= close_hour:
                print(today.time())
                return today


    return today

@is_ajax_dec
def visit_length_change_update(request,dentist_id,length):
    today = datetime.today()
    user = request.user
    context = {}
    data = dict()
    length = int(length)
    dentist = get_object_or_404(Dentist, id = dentist_id)
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    open_hour = opentime.start_hour
    close_hour = opentime.end_hour
    if today.time() > close_hour:
        today = datetime(today.year,today.month,today.day,open_hour.hour,open_hour.minute,0,0) + timedelta(days = 1) + timedelta(minutes= 1)
    elif open_hour > today.time():
        today = datetime(today.year,today.month,today.day,open_hour.hour,open_hour.minute,0,0)
    time_plus = today + timedelta(minutes= length)
    visits = Visit.objects.filter( Dentist = dentist, status = 'zaplanowana')
    while True:
        if not str(today.date().isoweekday()) in weekday or time_plus.time() >= close_hour:
            today = datetime(today.year, today.month, today.day,open_hour.hour,open_hour.minute,0,0) + timedelta(days = 1)
            time_plus = today + timedelta(minutes= length)
        else:
            visit = visits.filter(day_of_visit = today.date()).order_by("time_of_the_visit")
            print(today)
            if visits.exists():
                for v in visit:
                    if v.time_of_the_visit >= time_plus.time():
                        data['date'] = today.strftime('%Y-%m-%d')
                        return JsonResponse(data)
                    else:
                        print(today)
                        today = datetime.combine(today.date(),v.time_end_visit)
                        time_plus = today + timedelta(minutes= length)

            if time_plus.time() <= close_hour:
                print(today.time())
                data['date'] = today.strftime('%Y-%m-%d')
                data['time'] = (today + timedelta(hours = 1)).strftime('%H:%M')
                return JsonResponse(data)


    data['date'] = today.strftime('%Y-%m-%d')
    data['time_plus_hour'] = (today + timedelta(hours = 1)).strftime('%H:%M')

    return JsonResponse(data)
@is_ajax_dec
def safe_days(request, year, month, dentist_id,length, typesy): 
    length = int(length)
    print(month) 
    user = request.user
    context = {}
    data = dict()
    dentist = get_object_or_404(Dentist,id = dentist_id)
    year = int(year)
    month = int(month)
    print(year)
    opentime = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
    weekday = opentime.open_days
    open_hour = opentime.start_hour
    close_hour = opentime.end_hour
    today = datetime(year+1900, month+1, 1,open_hour.hour,open_hour.minute,0,0)
    time_plus = today + timedelta(minutes = length)
    monthplus = today + relativedelta(months =+ 1)
    dentist = get_object_or_404(Dentist, id = dentist_id)
    taken = False
    green = []
    red = []
    yellow = []
    while today < monthplus:
        if not str(today.date().isoweekday()) in weekday:
            today = datetime(today.year, today.month, today.day,open_hour.hour,open_hour.minute,0,0) + timedelta(days = 1)
            time_plus = today + timedelta(minutes = length)


        else:
            visits = Visit.objects.filter(Q(day_of_visit = today.date(), Dentist = dentist,status = "zaplanowana")|Q(day_of_visit = today.date(), Dentist = dentist, status = 'odbyła sie'))
            if visits.exists():
                for visit in visits:
                    print(today)
                    if time_plus.time() > close_hour:
                        red.append(today.strftime('%d.%m.%Y'))
                        green.append(today.strftime('%d.%m.%Y,pełny,redcss'))
                        taken = True
                        break  
                    elif visit.time_of_the_visit >= time_plus.time():
                        green.append(today.strftime('%d.%m.%Y,częściowo wolny,yellowcss'))
                        break
                    today = datetime.combine(today.date(), visit.time_end_visit)
                    time_plus = today + timedelta(minutes= length)


                if time_plus.time() > close_hour:
                    red.append(today.strftime('%d.%m.%Y'))
                    green.append(today.strftime('%d.%m.%Y,pełny,redcss'))
                    taken = True
                else:
                    green.append(today.strftime('%d.%m.%Y,częściowo wolny,yellowcss'))

            else:
                green.append(today.strftime('%d.%m.%Y,wolny,testowycss'))
            today = datetime(today.year, today.month, today.day,open_hour.hour,open_hour.minute,0,0) + timedelta(days = 1)
            time_plus = today + timedelta(minutes= length)

    data['red'] = red
    data['green'] = green

    return JsonResponse(data)






