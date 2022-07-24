from django.shortcuts import render, redirect, get_object_or_404
from account.models import *
from account.forms import *
from django.contrib.auth import login, authenticate,logout
from tooth.models import Tooth
from visit.models import Visit
from django.utils import timezone
from account.decorators import *
from django.contrib.auth.decorators import login_required
import datetime
import json
from django.views.generic import FormView 
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import datetime, date, time, timedelta
from chat.models import *


# Create your views here.

def registration_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(username= username, password = raw_password)
            login(request, account)
            if form.instance.is_receptionist:
                return redirect('registermore_receptionist')
            return redirect('registermore')
    else:
        form = RegistrationForm()
    context['registration_form'] = form
    return render(request, 'account/register.html', context)

@login_required
def more_info_view(request):
    context = {}
    user = request.user
    context['user'] = user
    if Dentist.objects.filter(account=user).exists():
        dentist = get_object_or_404(Dentist, account = user)
        if request.POST:
            form = DentistForm(request.POST, instance = dentist)
            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            form = DentistForm(instance = dentist)
    elif Patient.objects.filter(account=user).exists():
        patient = get_object_or_404(Patient, account = user)
        if request.POST:
            form = PatientForm(request.POST, instance =patient)
            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            form = PatientForm(instance = patient)
    else:
        if request.POST:
            if user.is_dentist == True:
 
                form = DentistForm(request.POST)
                
                if form.is_valid():
                    new_dentist = form.save(commit=False)
                    new_dentist.account = user
                    new_dentist.save()
                    user.save()
                    print(form.cleaned_data)
                    WeekdayHoursOpen.objects.create(dentist = new_dentist, start_hour = time(8,0,0,0), end_hour = time(16,0,0,0), open_days = [1,2,3,4,5])
                    Cennik.objects.create(dentist = new_dentist,wizyta_kontrolna = 20, wyrywanie = 50, kanałowe = 200, plomba= 150, czyszczenie = 175, leczenie_długotrwałe = 100, lekarstwo = 120, operacja = 600,inne = 100)

                    return redirect('/')

            else:

                form = PatientForm(request.POST)
                if form.is_valid():
                    new_patient = form.save(commit=False)
                    new_patient.account = user
                    new_patient.save()
                    user.save()
                    print(form.cleaned_data)                    
                    if new_patient.age < 12:
                        for b in range(1,6):
                            Tooth.objects.bulk_create([Tooth(patient=new_patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                                Tooth(patient=new_patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                                Tooth(patient=new_patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                                Tooth(patient=new_patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
                        for b in range(6,9):
                                Tooth.objects.bulk_create([Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="górny",number=b, active = False),
                                Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="górny",number=b, active = False),
                                Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="dolny",number=b, active = False),
                                Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="dolny",number=b, active = False)])
                    else:
                        for b in range(1,9):
                            Tooth.objects.bulk_create([Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="górny",number=b),
                                Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="górny",number=b),
                                Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                                Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="dolny",number=b)])

                    return redirect('/')
        else:
            if user.is_dentist == True:
                form = DentistForm()
            else:
                form = PatientForm()
    context['form'] = form

    return render(request, 'account/registermore.html', context)

@login_required
@user_is_receptionist
def more_reg_receptionist_view(request):
    context = {}
    user = request.user
    if Receptionist.objects.filter(account=user).exists():
        receptionist = get_object_or_404(Receptionist, account = user)
        if request.POST:
            form = ReceptionistForm(request.POST, instance =receptionist)
            if form.is_valid():
                form.save()
                return redirect('/')

        form = ReceptionistForm(instance = receptionist)
    else:
        if request.POST:
            form = ReceptionistForm(request.POST)
            
            if form.is_valid():
                receptionist = form.save(commit=False)
                receptionist.account = user
                receptionist.save()
                return redirect('/')
        form = ReceptionistForm()       
    context['form'] = form

    return render(request, 'account/registermore_receptionist.html',context)

def login_view(request):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("/")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            print(form.cleaned_data)
            user = authenticate(username = username, password = password)
            if user:
                login(request, user)
                return redirect('/')
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render (request, 'account/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def account_view(request):
    context = {}
    user = request.user

    if request.POST:
        if Dentist.objects.filter(account = user).exists() and request.POST.get("form_type") == 'weekday_hours_form':
            dentist = get_object_or_404(Dentist, account = user)
            instance = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
            weekday_hours_form = WeekdayHoursOpenForm(request.POST, dentist = dentist, instance= instance)
            if weekday_hours_form.is_valid():
                weekday_hours_form.save()

                print(weekday_hours_form.cleaned_data)
            else:
                print(weekday_hours_form.errors)


        elif request.POST.get("form_type") == 'form_account':
            form = AccountUpdateForm(request.POST, instance = request.user)
            if form.is_valid():
                form.initial = {
                        "email": request.POST['email'],
                        "username": request.POST['username'],
                }
                form.save()
                context['success_message'] = "Zaktualizowano dane"
        elif request.POST.get("form_type") == 'form_image':
            newform = AccountImageForm(request.POST, request.FILES, instance= request.user)
            if newform.is_valid():
                newform.save()
                context['success_message'] = "Zaktualizowano dane"
        elif request.POST.get("form_type") == 'cennik_form':
            print("YAHALO")
            dentist = get_object_or_404(Dentist, account = user)
            cennik = get_object_or_404(Cennik, dentist = dentist)
            cennik_form = CennikForm(request.POST,dentist = dentist, instance= cennik)
            if cennik_form.is_valid():
                cennik_form.save()
            else:
                cennik_form = CennikForm(dentist = dentist, instance= cennik)
                
        else:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
            else:
                print(form.errors)
                print (user.password)
                print (form.cleaned_data)
                context['change_errors'] = form.errors

    change_password_form = PasswordChangeForm(request.user)
    form = AccountUpdateForm(
            initial = {
                "email": request.user.email,
                "username": request.user.username
            }
        )

    if Dentist.objects.filter(account = user).exists():
        dentist = get_object_or_404(Dentist, account = user) 
        instance = get_object_or_404(WeekdayHoursOpen, dentist = dentist)
        cennik = get_object_or_404(Cennik, dentist = dentist)
        cennik_form = CennikForm(dentist = dentist, instance= cennik)
        weekday_hours_form = WeekdayHoursOpenForm(dentist = dentist, instance = instance)   
        context['instance_hour'] = instance.start_hour.strftime('%H:%M')
        context['instance_end_hour'] = instance.end_hour.strftime('%H:%M')
        context['weekday_hours_form'] = weekday_hours_form
        context['dentysta'] =  True

    newform = AccountImageForm(instance= request.user)
    context['image'] = user.profile_pic
    context['form'] = form
    context['cennik_form'] = cennik_form
    context['change_password_form'] = change_password_form

    return render(request, 'account/account.html', context)

def must_authenticate_view(request):
    return render(request, 'account/must_authenticate.html',{}) 

def must_fully_register_view(request):
    return render(request, 'account/must_fully_register.html',{})  

@user_is_dentist_or_receptionist
@user_is_fully_registered
@login_required
def patients_view(request, type="", dentist_id = None):

    user = request.user
    context = {}

    if dentist_id is not None:
        receptionist = get_object_or_404(Receptionist, account = user)
        dentists = receptionist.dentist.all()
        if dentists.filter(id = dentist_id).exists():
            curr_dentist = dentists.filter(id = dentist_id).first()
            context['curr_dentist_id'] = curr_dentist.id
            context['dent_name_surname'] = curr_dentist.First_Name + " " + curr_dentist.Surname
        else:
            return redirect('/')
    else:
        curr_dentist = get_object_or_404(Dentist,account = user)

#    patients = Patient.objects.filter(dentist__in = [curr_dentist]
    patients = Patient.objects.filter(Q(private = False)|Q(private = True, dentist__in = [curr_dentist]))
    search_query = request.GET.get("q")
    if type == "mine":
        patients = patients.filter(dentist__in = [curr_dentist])
    if search_query:
        search_choice = search_query.split('/--/')[0]
        searched = search_query.split('/--/')[1]
        if search_choice == 'name':
            patients = patients.filter(First_Name__icontains = searched)
        elif search_choice == 'surname':
            patients = patients.filter(Surname__icontains = searched)
        elif search_choice == 'phone':
            patients = patients.filter(phone_number__icontains = searched)
        elif search_choice == 'city':
            patients = patients.filter(city__icontains = searched)


    a = []
    b = []
    c = []
    d = []
    print (patients)
    for p in patients:
        if p.dentist.filter(id = curr_dentist.id).exists():
            d.append(True)
        else:
            d.append(False)
        tooth = Tooth.objects.filter(patient = p, status = "wyleczony", replaced = False).count()
        a.append(tooth)
        tooth = Tooth.objects.filter(patient = p, status = "chory", replaced = False).count()
        b.append(tooth)
        if Visit.objects.filter(Dentist = curr_dentist, Patient = p,  Type_of='wizyta kontrolna').exists():
            visit = Visit.objects.filter(Dentist = curr_dentist, Patient = p, Type_of='wizyta kontrolna').order_by('-day_of_visit').first()
            if (datetime.today().date() - visit.day_of_visit).days <=0:
                c.append("zaplanowana")
            else:
                c.append(str((datetime.today().date() - visit.day_of_visit).days)+" dni")
        else:
            c.append("Żadna się nie odbyła")
    
    lista = zip(patients, a,b,c,d)
    context['lista'] = lista
    if request.is_ajax():
        patients_html = render_to_string(
            "account/patients_list.html", 
            context, request = request)

        datas = {"html_from_view": patients_html}

        return JsonResponse(data=datas, safe=False)

    return render(request, 'account/patients.html', context)

@is_ajax_dec
def update_patient_list_view(request, dentist_id = None):
    context = {}
    user = request.user

    data = dict()
    if dentist_id is not None:
        receptionist = get_object_or_404(Receptionist, account = user)
        dentists = receptionist.dentist.all()
        if dentists.filter(id = dentist_id).exists():
            curr_dentist = dentists.filter(id = dentist_id).first()
            context['curr_dentist_id'] = curr_dentist.id
        else:
            return redirect('/')
    else:
        curr_dentist = get_object_or_404(Dentist,account = user)

    data['form_is_fine'] = True
    patients = Patient.objects.filter(dentist__in = [curr_dentist])

    a = []
    b = []
    c = []
    d = []
    for p in patients:
        if p.dentist.filter(id = curr_dentist.id).exists():
            d.append(True)
        else:
            d.append(False)
        tooth = Tooth.objects.filter(patient = p, status = "wyleczony", replaced = False).count()
        a.append(tooth)
        tooth = Tooth.objects.filter(patient = p, status = "chory", replaced = False).count()
        b.append(tooth)
        if Visit.objects.filter(Dentist = curr_dentist, Patient = p,  Type_of='wizyta kontrolna').exists():
            visit = Visit.objects.filter(Dentist = curr_dentist, Patient = p, Type_of='wizyta kontrolna').order_by('-day_of_visit').first()
            if (datetime.today().date() - visit.day_of_visit).days <=0:
                c.append("zaplanowana")
            else:
                c.append(str((datetime.today().date() - visit.day_of_visit).days)+" dni")
        else:
            c.append("Żadna się nie odbyła")
    
    lista = zip(patients, a,b,c,d)
    context['lista'] = lista
    data['html_patient_list'] = render_to_string('account/patients_list.html',context, request = request)
    return JsonResponse(data)
@is_ajax_dec
@user_is_fully_registered
@user_is_dentist_or_receptionist
@login_required
def create_new_patient_view(request, dentist_id=None):
    context = {}
    user = request.user

    if dentist_id == None:
        dentist = get_object_or_404(Dentist, account = user)
    else:
        dentist = get_object_or_404(Dentist, id = dentist_id)
        receptionist = get_object_or_404(Receptionist, account = user, dentist__in = [dentist])
        context['curr_dentist_id'] = dentist.id

    data = dict()
    print("halo")
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            new_patient = form.save(commit=False)
            new_patient.save()
            new_patient.dentist.add(dentist)
            new_patient.save()
            if new_patient.age < 12:
                for b in range(1,6):
                    Tooth.objects.bulk_create([Tooth(patient=new_patient,tooth_type="mleczny",side="prawy",level="górny",number=b),
                        Tooth(patient=new_patient,tooth_type="mleczny",side="lewy",level="górny",number=b),
                        Tooth(patient=new_patient,tooth_type="mleczny",side="lewy",level="dolny",number=b),
                        Tooth(patient=new_patient,tooth_type="mleczny",side="prawy",level="dolny",number=b)])
                for b in range(6,9):
                        Tooth.objects.bulk_create([Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="górny",number=b, active = False),
                        Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="górny",number=b, active = False),
                        Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="dolny",number=b, active = False),
                        Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="dolny",number=b, active = False)])
            else:
                for b in range(1,9):
                    Tooth.objects.bulk_create([Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="górny",number=b),
                        Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="górny",number=b),
                        Tooth(patient=new_patient,tooth_type="stały",side="lewy",level="dolny",number=b),
                        Tooth(patient=new_patient,tooth_type="stały",side="prawy",level="dolny",number=b)])
            if dentist_id == None:
                return redirect('update_patient_list')
            else:
                return redirect('update_patient_list',dentist_id)
        else:
            data['form_is_fine'] = False
    else:
        form = PatientForm()
    context['form'] = form
    data['html_form'] = render_to_string('account/patients_add.html',
        context,
        request=request,
    )
    return JsonResponse(data)


def check_if_is_my_patient(request, id):
    patient = get_object_or_404(Patient, id = id)
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    if user.is_dentist:
        if dentist in patient.dentist.all():
            return True
        else:
            return False
    else:
        receptionist = get_object_or_404(Receptionist,account = user)
        for dentist in receptionist.dentist.all():
            if dentist in patient.dentist.all():
                return True

    return False



@is_ajax_dec
@user_is_fully_registered
@user_is_dentist_or_receptionist
@login_required
def update_patient_view(request, id, dentist_id = None):
    context = {}
    data = dict()
    user = request.user
    if dentist_id is not None:
        context['recep'] = True
        context['id'] = dentist_id
    patient = get_object_or_404(Patient, id = id)
    if not check_if_is_my_patient(request,id):
        data['break'] = True


    if request.method == 'POST':
        form = PatientForm(request.POST, instance = patient)
        if form.is_valid():
            form.save()
            if dentist_id is not None:
                return redirect('update_patient_list', dentist_id)
            else:
                return redirect('update_patient_list')
        else:
            data['form_is_fine'] = False 
    else:
        form = PatientForm(instance = patient)
    context['form'] = form
    data['html_form'] = render_to_string('account/patient_update.html',
        context,
        request=request,
    )
    return JsonResponse(data)


@is_ajax_dec
@user_is_fully_registered
@user_is_dentist_or_receptionist
@login_required
def delete_patient_view(request, id,  dentist_id = None):  
    patient = get_object_or_404(Patient, id=id)
    data = dict()
    user = request.user
    context = {}
    if dentist_id is not None:
        context['recep'] = True
        context['id'] = dentist_id
    patient = get_object_or_404(Patient, id = id)
    if not check_if_is_my_patient(request,id):
        data['break'] = True

    if request.method == 'POST':
        patient.delete()
        if dentist_id is not None:
            return redirect('update_patient_list', dentist_id)
        else:
            return redirect('update_patient_list')
    else:
        context['patient'] = patient
        data['html_form'] = render_to_string('account/patient_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)

@is_ajax_dec
@user_is_fully_registered
@user_is_dentist_or_receptionist
@login_required
def patient_invite_remove_view(request, id,  dentist_id = None):  
    patient = get_object_or_404(Patient, id=id)
    data = dict()
    user = request.user
    context = {}
    if dentist_id is not None:
        context['recep'] = True
        context['id'] = dentist_id
        dentist = get_object_or_404(Dentist, id = dentist_id)
        receptionist = get_object_or_404(Receptionist, account = user, dentist__in = dentist)
    else:
        dentist = get_object_or_404(Dentist,id = id)
    patient = get_object_or_404(Patient, id = id)
    if patient.dentist.filter(id = dentist.id).exists():
        context['remove'] = True
    else:
        context['invite'] = True

    if request.method == 'POST':
        if patient.dentist.filter(id = dentist.id).exists():
            patient.dentist.remove(dentist)
        else:
            patient.dentist.add(dentist)
        if dentist_id is not None:
            return redirect('update_patient_list', dentist_id)
        else:
            return redirect('update_patient_list')
    else:
        context['patient'] = patient
        data['html_form'] = render_to_string('account/patient_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)



def choose_dentist_ciew(request, type=""):
    user = request.user
    context = {}
    patient = None
    if user.is_receptionist:
        patient = get_object_or_404(Receptionist,account = user)
    elif user.is_dentist == False:
        if Patient.objects.filter(account = user).exists():
            patient = get_object_or_404(Patient,account = user)
            context['is_patient'] = True

    search_query = request.GET.get("q")



    if type=="mine":
        dentist = patient.dentist.all()
    else:
        dentist = Dentist.objects.all()
    if search_query:
        search_choice = search_query.split('/--/')[0]
        searched = search_query.split('/--/')[1]
        if search_choice == 'name':
            dentist = dentist.filter(First_Name__icontains = searched)
        elif search_choice == 'surname':
            dentist = dentist.filter(Surname__icontains = searched)
        elif search_choice == 'phone':
            dentist = dentist.filter(phone_number__icontains = searched)
        elif search_choice == 'city':
            dentist = dentist.filter(city__icontains = searched)
        print(dentist)
    a = []
    print(patient)
    if patient is not None:
        print("WHURA")
        for d in dentist:
            if d in patient.dentist.all():
                a.append(True)
            else:
                a.append(False)
        dentist = zip(dentist,a)

    elif user.is_authenticated:
        context['auth_only'] = True
    else:
        context['unregistered'] = True

    context['dentist'] = dentist
    if request.is_ajax():

        patients_html = render_to_string(
            "account/snippets/dentist_list.html",
            context,
            request = request,
            
        )

        datas = {"html_from_view": patients_html}

        return JsonResponse(data=datas, safe=False)
    return render(request,'account/choose_dentist.html', context)

@is_ajax_dec
@user_is_fully_registered
def join_as_receptionist_view(request, dentist_id):
    context = {}
    data = dict()
    user = request.user
    receptionist = get_object_or_404(Receptionist, account = user)
    dentist = get_object_or_404(Dentist, id = dentist_id)
    if request.POST:
        if dentist in receptionist.dentist.all():
            receptionist.dentist.remove(dentist)
        else:
            receptionist.dentist.add(dentist)
        receptionist.save()
        return redirect("update_all_dentist")
    if dentist in receptionist.dentist.all():
        context['form_type'] = 'leave_as_receptionist'
    else:
        context['form_type'] = 'join_as_receptionist'
    context['dentist'] = dentist       
    data['html_form'] = render_to_string('account/snippets/choose_dentist_ask.html', 
        context,
        request = request,
                )
    return JsonResponse(data)

def update_all_dentist_view(request):
    user = request.user
    context = {}
    data = dict()
    if user.is_receptionist:
        user = get_object_or_404(Receptionist,account = user)
    elif user.is_dentist == False:
        user = get_object_or_404(Patient,account = user)
        context['is_patient'] = True
        
    search_query = request.GET.get("q")
    data['form_is_fine'] = True
    dentist = Dentist.objects.all()
    a = []
    for d in dentist:
        if d in user.dentist.all():
            a.append(True)
        else:
            a.append(False)
    dentist = zip(dentist,a)
    context['dentist'] = dentist

    data['html_dentist_list'] = render_to_string('account/snippets/dentist_list.html', 
                    context,
            request=request,
            )
    return JsonResponse(data)


    
@is_ajax_dec
@user_is_patient
@user_is_fully_registered
def dentist_change_stat_view(request, dentist_id):
    context = {}
    data = dict()
    user = request.user
    patient = get_object_or_404(Patient,account = user)
    dentist = get_object_or_404(Dentist, id = dentist_id)
    if dentist in patient.dentist.all():
        patient.dentist.remove(dentist)
    else:
        patient.dentist.add(dentist)     
    patient.save()
    return redirect("update_all_dentist")









def dentist_profile_view(request, dentist_id=None):
    print("TEST")
    user = request.user
    context = {}
    if dentist_id == None:
        dentist = get_object_or_404(Dentist, account = user)
    else:
        dentist = get_object_or_404(Dentist, id = dentist_id)

    curr_comm = Comment.objects.filter(dentist = dentist, active = True).order_by('-created_on')[:6]

    if user.is_authenticated:
        if Patient.objects.filter(account = user).exists():
            context['is_patient'] = True    

    count_com = Comment.objects.filter(dentist = dentist, active = True).count()
    if count_com > 4:
        context['more_com'] = True
        more_curr_comm = Comment.objects.filter(dentist = dentist, active = True).order_by('-created_on')
        context['more_comments'] = more_curr_comm
        if count_com > 10:
            context['most_com'] = True
            
    context['comm_count'] = count_com
    context['curr_comm'] = curr_comm
    context['comments'] = curr_comm


    if Location.objects.filter(dentist = dentist).exists():
        loc = Location.objects.filter(dentist = dentist)
        a = []
        b = []
        for l in loc:
            a.append(l.location[0])
            b.append(l.location[1])

        print(loc)

        context['loc'] = zip(loc,a,b)
        context['locationa'] = a
        context['locationb'] = b
        context['location'] = loc
    images = Images_aboutme.objects.filter(dentist = dentist)
    if dentist.account == user:
        if request.method == 'POST':
            form = ImagesForm(request.POST, request.FILES, dentist = dentist)
            if form.is_valid():
                form.save()
                print(form.cleaned_data)
                return redirect('dentist_profile')
        else:
            form = ImagesForm(dentist = dentist)
            context['img_form'] = form
    a = []
    for i in range (images.count()):
        a.append(i)

    no_of_visits = Visit.objects.filter(Dentist = dentist).count()

    no_of_healing = Visit.objects.filter(Dentist = dentist, Type_of = 'leczenie').count()

    no_of_patients = Patient.objects.filter(dentist__in = [dentist]).count()

    achievements = Achievements.objects.filter(dentist = dentist).order_by('significance')

    specialisation = Specialisation.objects.filter(dentist  = dentist)
    if user.id == dentist.account.id:
        context['is_d'] = True

    context['specialisation'] = specialisation

    context['achievements'] = achievements
    context['no_of_patients'] = no_of_patients

    context['no_of_healing'] = no_of_healing
    context['no_of_visits'] = no_of_visits

    context['img_count'] = images.count()
    context['images'] = zip(images,a)
    context['dentist'] = dentist

    context['user'] = user
    return render(request,'account/dentist_profile.html',context)
            

def home_view(request):
    user= request.user
    context = {}
    today = datetime.today().date()
    time = datetime.now().time()
    if request.user.is_authenticated:
        if Patient.objects.filter(account = user).exists or Dentist.objects.filter(account = user).exists or Receptionist.objects.filter(account = user).exists():
            context['fully_reg'] = True
        else:
            context['fully_reg'] = False



    return render(request, 'home.html', context)

@login_required
@user_is_fully_registered
@user_is_dentist_or_receptionist
def location_add_view(request, location_id = None):
    user = request.user
    context = {}
    if not location_id == None :
        if request.user.is_dentist:
            loc = get_object_or_404(Location,id = location_id, dentist__account = user)
        else:
            loc = get_object_or_404(Location,id = location_id, receptionist__account = user)            
        if request.method == 'POST':
            form = LocationForm(request.POST, instance = loc)
            if form.is_valid():
                form.save()
                return redirect('clinic_location_info', form.instance.id)
            else:
                print(form.errors)
        form = LocationForm( instance = loc)       
    else:
        if request.method == 'POST':
            form = LocationForm(request.POST)
            if form.is_valid():
                form.save()
                if user.is_dentist:
                    dentist = get_object_or_404(Dentist,account = user)
                    location = form.instance
                    location.dentist.add(dentist)
                else:
                    receptionist = get_object_or_404(Receptionist, account = user)
                    location = form.instance
                    location.receptionist.add(receptionist)
                location.save()
                return redirect('clinic_location_info', form.instance.id)
        form = LocationForm()
    context['form'] = form
    return render(request, 'account/location_add.html', context)




def all_den_loc_view(request):
    context = {}
    user = request.user
    location = Location.objects.all()
    loca = []
    locb = []
    is_in = []
    for a in location:
        loca.append(a.location[0])
        locb.append(a.location[1])
        if a.dentist.filter(account = user).exists() or a.receptionist.filter(account = user).exists():
            is_in.append(True)
        else:
            is_in.append(False)

    locab = zip(loca,locb,location, is_in)
    context['locab'] = locab
    context['locb'] = locb
    context['loca'] = loca
    context['location'] = location
    if request.user.is_authenticated:
        if Dentist.objects.filter(account = user).exists():
            dentist = get_object_or_404(Dentist, account = user)
            context['city'] = dentist.city
            context['adress'] = dentist.clinic_adress
            context['may_join'] = True
        elif Patient.objects.filter(account = user).exists():
            patient = get_object_or_404(Patient, account = user)
            context['city'] = patient.city
            context['adress'] = patient.adress
        elif Receptionist.objects.filter(account = user).exists():
            context['may_join'] = True
            context['city'] = "Warsaw"
            context['adress'] = ""
        else:
            context['city'] = "Warsaw"
            context['adress'] = ""

    return render(request, 'account/all_den_loc.html', context)

@is_ajax_dec
def add_about_me_view(request):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    if request.method == 'POST':
        form = AboutMeForm(data = request.POST, instance=  dentist)
        if form.is_valid():
            form.save()
            return redirect('update_about_me')
        else:
            data['form_is_fine'] = False

    else:
        form = AboutMeForm(instance = dentist)
    context['form_type'] = "about_me"
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data)
@is_ajax_dec
def update_about_me_view(request):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    image = Images_aboutme.objects.filter(dentist = dentist)
    a = []
    for i in range (image.count()):
        a.append(i)

    context['is_d'] = True
    context['images'] = zip(image,a)
    context['dentist'] = dentist
    data['form_is_fine'] = True
    data['name_of_update'] = ".about_me_neue"
    data['html_form'] = render_to_string('account/snippets/profile/about_me.html',
        context,
        request=request,
    )
    return JsonResponse(data)


@is_ajax_dec
def delete_image_view(request, image_id):
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    image = get_object_or_404(Images_aboutme, id = image_id, dentist = dentist)
    image.delete()
    return redirect('dentist_profile')

@is_ajax_dec
def add_achievements_view(request):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    if request.method == 'POST':
        form = AchievementsForm(data = request.POST, dentist = dentist)
        if form.is_valid():
            form.save()
            return redirect('update_achievements_shown')
        else:
            data['form_is_fine'] = False
    else:
        form = AchievementsForm(dentist = dentist)
    context['form_type'] = "achievements"
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data)
@is_ajax_dec
def update_achievements_shown_view(request):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    achievements = Achievements.objects.filter(dentist = dentist)
    context['achievements'] = achievements
    data['form_is_fine'] = True
    data['name_of_update'] = ".achievements_div"
    data['html_form'] = render_to_string('account/snippets/profile/achievements.html',
        context,
        request=request,
    )
    return JsonResponse(data)
@is_ajax_dec
def edit_achievements_view(request,achievement_id):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    achievement = get_object_or_404(Achievements, id = achievement_id, dentist = dentist)
    if request.method == 'POST':
        form = AchievementsForm(data = request.POST, dentist = dentist ,instance = achievement)
        if form.is_valid():
            form.save()
            return redirect('update_achievements_shown')
        else:
            data['form_is_fine'] = False
    else:
        form = AchievementsForm(dentist = dentist, instance = achievement)
    context['form_type'] = "achievement_edit"
    context['id'] = achievement.id
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data)    
@is_ajax_dec
def delete_achievement_view(request,achievement_id):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    achievement = get_object_or_404(Achievements, id = achievement_id, dentist = dentist)
    if request.method == 'POST':
        achievement.delete()
        return redirect('update_achievements_shown')
    context['achievement'] = achievement
    context['form_type'] = "achievement"
    context['id'] = achievement.id
    data['html_form'] = render_to_string('account/snippets/profile/delete.html',
        context,
        request=request,
    )
    return JsonResponse(data)  

@is_ajax_dec
def update_specialisation_shown_view(request):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    specialisation = Specialisation.objects.filter(dentist = dentist)
    context['specialisation'] = specialisation
    data['form_is_fine'] = True
    data['name_of_update'] = ".specialisation_div"
    data['html_form'] = render_to_string('account/snippets/profile/specialisation.html',
        context,
        request=request,
    )
    return JsonResponse(data)

@is_ajax_dec
def add_specialisation_view(request):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    if request.method == 'POST':
        form = SpecialisationForm(data = request.POST, dentist = dentist)
        if form.is_valid():
            form.save()
            return redirect('update_specialisation_shown')
        else:
            data['form_is_fine'] = False
    else:
        form = SpecialisationForm(dentist = dentist)
    context['form_type'] = "specialisation"
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data) 
@is_ajax_dec
def edit_specialisation_view(request,specialisation_id):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    specialisation = get_object_or_404(Specialisation, id = specialisation_id, dentist = dentist)
    if request.method == 'POST':
        form = SpecialisationForm(data = request.POST, dentist = dentist ,instance = specialisation)
        if form.is_valid():
            form.save()
            return redirect('update_specialisation_shown')
        else:
            data['form_is_fine'] = False
    else:
        form = SpecialisationForm(dentist = dentist, instance = specialisation)
    context['form_type'] = "specialisation_edit"
    context['id'] = specialisation.id
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data)    
@is_ajax_dec
def delete_specialisation_view(request,specialisation_id):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    specialisation = get_object_or_404(Specialisation, id = specialisation_id, dentist = dentist)
    if request.method == 'POST':
        specialisation.delete()
        return redirect('update_specialisation_shown')
    context['specialisation'] = specialisation
    context['form_type'] = "specialisation"
    context['id'] = Specialisation.id
    data['html_form'] = render_to_string('account/snippets/profile/delete.html',
        context,
        request=request,
    )
    return JsonResponse(data)  
@is_ajax_dec
def update_comment_shown_view(request, dentist_id):
    context = {}
    data = dict()
    dentist = get_object_or_404(Dentist, id = dentist_id)
    curr_comm = Comment.objects.filter(dentist = dentist, active = True).order_by('-created_on')[:6]
    

    count_com = Comment.objects.filter(dentist = dentist, active = True).count()
    if count_com > 4:
        context['more_com'] = True
        more_curr_comm = Comment.objects.filter(dentist = dentist, active = True).order_by('-created_on')
        context['more_comments'] = more_curr_comm
        if count_com > 10:
            context['most_com'] = True
            
    context['comm_count'] = count_com
    context['curr_comm'] = curr_comm
    context['comments'] = curr_comm
    context['dentist'] = dentist
    data['form_is_fine'] = True
    data['name_of_update'] = ".comments_div"
    data['html_form'] = render_to_string('account/snippets/profile/comments.html',
        context,
        request=request,
    )
    return JsonResponse(data)

@is_ajax_dec
@login_required
def add_comment_view(request,dentist_id):
    user = request.user
    data = dict()
    dentist = get_object_or_404(Dentist, id = dentist_id)
    context = {}
    if request.method == 'POST':
        form = CommentForm(request.POST, dentist = dentist,account = user)
        if form.is_valid():
            form.save()
            return redirect('update_comment_shown', dentist.id)
    else:
        form = CommentForm(dentist = dentist,account = user)
    context['form_type'] = "comment"
    print(dentist.id)
    context['id'] = dentist.id
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data) 
@is_ajax_dec
@login_required
def edit_comment_view(request, comment_id):
    user = request.user
    data = dict()
    comment = get_object_or_404(Comment, id = comment_id, account = user)
    dentist = comment.dentist
    context = {}
    if request.method == 'POST':
        form = CommentForm(request.POST, account = user, dentist = dentist, instance = comment)
        if form.is_valid():
            form.save()
            return redirect('update_comment_shown', dentist.id)

    else:
        form = CommentForm(account = user, dentist = dentist,  instance = comment)
    context['form_type'] = "edit_comment"
    context['id'] = comment.id
    context['form'] = form
    data['html_form'] = render_to_string('account/snippets/profile/account_forms.html',
        context,
        request=request,
    )
    return JsonResponse(data) 

@is_ajax_dec    
@login_required
def delete_comment_view(request,comment_id):
    context = {}
    data = dict()
    user = request.user
    comment = get_object_or_404(Comment, id = comment_id, account = user)
    if request.method == 'POST':
        comment.delete()
        return redirect('update_comment_shown', comment.dentist.id)
    context['comment'] = comment
    context['form_type'] = "comment"
    context['id'] = comment.id
    data['html_form'] = render_to_string('account/snippets/profile/delete.html',
        context,
        request=request,
    )
    return JsonResponse(data) 

@is_ajax_dec
def hide_comment_view(request,comment_id):
    context = {}
    data = dict()
    user = request.user
    dentist = get_object_or_404(Dentist, account = user)
    comment = get_object_or_404(Comment, id = comment_id, dentist = dentist)
    if request.method == 'POST':
        comment.active = False
        comment.save()
        return redirect('update_comment_shown', dentist.id)
    context['comment'] = comment
    context['form_type'] = "comment_hide"
    context['id'] = comment.id
    data['html_form'] = render_to_string('account/snippets/profile/delete.html',
        context,
        request=request,
    )
    return JsonResponse(data) 

@login_required
def chat_view_information(request):
    context = {}
    user = request.user
    threads = Thread.objects.filter(Q(first = user) | Q(second = user)).order_by('-updated')
    message = []
    type_of = []
    author_name = []
    oth_acc = []

    for t in threads:
        if t.first == user:
            oth_user = t.second
        else:
            oth_user = t.first
        if oth_user.is_dentist:
            type_of.append("dentysta")
            if Dentist.objects.filter(account = oth_user).exists():
                dentist = get_object_or_404(Dentist, account = oth_user)
                author_name.append(dentist.First_Name + " " + dentist.Surname)
            else:
                author_name.append("Brak Danych")
        elif oth_user.is_receptionist:
            type_of.append("recepcjonista")
            if Receptionist.objects.filter(account = oth_user).exists():
                receptionist = get_object_or_404(Receptionist, account = oth_user)
                author_name.append(receptionist.First_Name + " " + receptionist.Surname)
            else:
                author_name.append("Brak Danych")      
        else:
            type_of.append("pacjent")
            if Patient.objects.filter(account = oth_user).exists():
                patient = get_object_or_404(Patient, account = oth_user)
                author_name.append(patient.First_Name + " " + patient.Surname)
            else:
                author_name.append("Brak Danych")                
        message.append(ChatMessage.objects.filter(thread = t).first())
        oth_acc.append(oth_user)
    lista = zip(threads, message, author_name, type_of, oth_acc)
    context['lista'] = lista
    return render(request, 'account/chat_information.html', context)

@login_required    
@user_is_fully_registered
@user_is_dentist_or_receptionist
def location_ask_for_invite(request, location_id):
    context = {}
    user = request.user
    location = get_object_or_404(Location, id = location_id)
    if not Invitation_to_location.objects.filter(user = user, location = location).exists():
        Invitation_to_location.objects.create(user = user, location = location, created_on = datetime.now())
    return redirect('clinic_location_info', location.id)




@login_required    
@user_is_fully_registered
@user_is_dentist_or_receptionist
def location_approve_view(request, invitation_id):
    context = {}
    user = request.user
    invitation = get_object_or_404(Invitation_to_location, id = invitation_id)
    location = invitation.location
    approved_user = invitation.user
    if approved_user.is_dentist:
        dentist = get_object_or_404(Dentist, account = approved_user)
        location.dentist.add(dentist)
        location.save()
        for receptionist in location.receptionist.all():
            receptionist.dentist.add(dentist)
            receptionist.save()
    else:
        receptionist = get_object_or_404(Receptionist, account = approved_user)
        location.receptionist.add(receptionist)
        location.save()
        for dentist in location.dentist.all():
            receptionist.dentist.add(dentist)
        receptionist.save()
    invitation.delete()

    return redirect('clinic_location_info', location.id)

@login_required    
@user_is_fully_registered
@user_is_dentist_or_receptionist
def location_reject_view(request, invitation_id):
    context = {}
    user = request.user
    invitation = get_object_or_404(Invitation_to_location, id = invitation_id)
    location = invitation.location
    invitation.delete()

    return redirect('clinic_location_info', location.id)


@login_required    
@user_is_fully_registered
@user_is_dentist_or_receptionist
def location_resign_view(request, location_id):
    context = {}
    user = request.user
    location = get_object_or_404(Location, id = location_id)
    if user.is_dentist:
        dentist = get_object_or_404(Dentist, account = user)

        location.dentist.remove(dentist)
        location.save()
        for receptionist in location.receptionist.all():
            receptionist.dentist.remove(dentist)
            receptionist.save()
    else:
        receptionist = get_object_or_404(Receptionist, account = user)
        location.receptionist.remove(receptionist)
        location.save()
        for dentist in location.dentist.all():
            receptionist.dentist.remove(dentist)
        receptionist.save()

    return redirect('clinic_location_info', location.id)



def clinic_location_info_view(request, location_id):
    context = {}
    user = request.user
    location = get_object_or_404(Location, id = location_id)
    dentists = location.dentist.all()
    a = []
    b = []
    c = []
    for dentist in dentists:
        a.append(Cennik.objects.get(dentist = dentist))
        week = WeekdayHoursOpen.objects.get(dentist = dentist)
        b.append(week)
        c.append(week.get_open_days_display())
    if location.dentist.filter(account = user).exists() or location.receptionist.filter(account = user).exists():
        context['main'] = True
    context['dentists'] = zip(dentists,a,b,c)
    invitations = Invitation_to_location.objects.filter(location = location)
    invitation_dentist = []
    invitations_dentist = invitations.filter(user__is_dentist = True)
    for dentist in invitations_dentist:
        invitation_dentist.append(get_object_or_404(Dentist,account = dentist.user))

    invitation_receptionist = []
    invitations_receptionist = invitations.filter(user__is_receptionist = True)
    for receptionist in invitations_receptionist:
        invitation_receptionist.append(get_object_or_404(Receptionist,account = receptionist.user))
        print(receptionist.user)
    context['invitations_dentist'] = invitation_dentist
    context['invitations_receptionist'] = invitation_receptionist
    context['loca'] = location.location[0]
    context['locb'] = location.location[1]
    context['location'] = location
    return render(request, 'account/clinic_location_info.html',context)



    

