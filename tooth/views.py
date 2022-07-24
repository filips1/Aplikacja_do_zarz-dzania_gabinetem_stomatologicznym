from datetime import date, datetime
from django.shortcuts import render,  get_object_or_404,redirect
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from django.utils.timezone import timedelta
import calendar
from django.urls import reverse
from django.contrib.auth import login, authenticate,logout
from visit.models import Visit, tooth_healing_destruction
from visit.forms import VisitForm, tooths_healing_form
from django.http import HttpResponse, HttpResponseRedirect
from account.models import Dentist, Account, Patient, Receptionist, Cennik
from tooth.models import Tooth, Tooth_destructions, Tooth_rentgen
from tooth.forms import  tooth_destroy_form, tooth_healing_form_new, tooth_rentgen_form
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from datetime import datetime, timedelta, time, date
from django.db.models import Q
from django.http import Http404
from account.decorators import *
# Create your views here.

@login_required
@user_is_dentist
@user_is_fully_registered
def ToothView(request,patient_id):
    user = request.user
    context = {}
    dentist = get_object_or_404(Dentist, account = user)
    patient = get_object_or_404(Patient, id = patient_id, dentist__in = [dentist])
    Toothsa = Tooth.objects.filter(patient = patient,side="lewy",level="górny", replaced = False).order_by('-level','side','-number')
    Toothsb= Tooth.objects.filter(patient = patient, side="prawy",level="górny", replaced = False).order_by('number')
    Toothsc= Tooth.objects.filter(patient = patient, side="lewy",level="dolny", replaced = False).order_by('-level','side','-number')
    Toothsd= Tooth.objects.filter(patient = patient, side="prawy",level="dolny", replaced = False).order_by('-level','side','number')
    a = []
    for t in Toothsa:
      a.append(t)
    for t in Toothsb:
      a.append(t)
    for t in Toothsc:
      a.append(t)
    for t in Toothsd:
      a.append(t)
    b = []
    for tooth in a:
      c = ''
      if tooth.exists == False:
        c = '0b'
      else:
        if Tooth_destructions.objects.filter(tooth = tooth).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
            if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
              c += '1'
            else:
              c += '1h'
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
            if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
              c+= '2'
            else:
              c+= '2h'
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
            if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
              c += '3'
            else:
              c += '3h'
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
            if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
              c+= '4'
            else:
              c += '4h'
        else:
          c = '0'
      toothimg ="8dl/"+c+".png"
      b.append(toothimg)
    lista = zip(a,b)
    context['info'] = lista
    context['patient'] = patient
    tooth = get_object_or_404(Tooth,patient = patient, side="lewy", level="dolny", number = 8)
    toothimg = str(tooth.number) + tooth.level[0] + tooth.side[0]+ "/0.png"
    context['tooth'] = tooth
    context['toothimg'] = toothimg
    return render(request,"tooth/view.html",context)

@login_required
@user_is_dentist
@user_is_fully_registered
def ToothAbout(request, tooth_id):
  user = request.user
  context = {}  
  tooth = get_object_or_404(Tooth, id =tooth_id)
  patient = tooth.patient
  if not patient.dentist.filter(account = user).exists():
    return redirect('/')
  data = dict()
  context['tooth'] = tooth
  a = ''
  b = ''
  destroyed = False
  if Tooth_destructions.objects.filter(tooth = tooth).exists():
    s =Tooth_destructions.objects.filter(tooth = tooth).order_by('-depth').first()
    f = s.depth
    g =Tooth_destructions.objects.filter(tooth = tooth).order_by('-depth').count()
    destroyed = True
    if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
        a += '1'
        b += 'lewa strona zęba '
      else:
        a += '1h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
          b += 'z korzeniem'
          a += '2'
        else:
          a += '2h'
      b+= ', '
    if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
        b+= 'prawa strona zęba '
        a += '3'
      else:
        a += '3h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
          b+= 'z korzeniem '
          a+= '4'
        else:
          a += '4h'

  else:
    f = '0'
    a = '0'
    g = 0
    b = "brak"
  toothimg = "8dl/"+a+".png"
  context['toothimg'] = toothimg
  data['html_form'] = render_to_string('tooth/special_see_only.html',
            context,
            request=request,
        )
  return JsonResponse(data)


@login_required
@user_is_dentist
@user_is_fully_registered
def ToothInfo(request, tooth_id):
  user = request.user
  context = {}
  tooth = get_object_or_404(Tooth, id =tooth_id)
  patient = tooth.patient
  if not patient.dentist.filter(account = user).exists():
    return redirect('/')
  context['tooth'] = tooth
  a = ''
  b = ''
  destroyed = False
  if tooth.exists:
    if Tooth_destructions.objects.filter(tooth = tooth).exists():
      s =Tooth_destructions.objects.filter(tooth = tooth).order_by('-depth').first()
      f = s.depth
      g =Tooth_destructions.objects.filter(tooth = tooth).order_by('-depth').count()
      destroyed = True
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
          a += '1'
          b += 'lewa strona zęba '
        else:
          a += '1h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
            b += 'z korzeniem'
            a += '2'
          else:
            a += '2h'
        b+= ', '
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
          b+= 'prawa strona zęba '
          a += '3'
        else:
          a += '3h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
            b+= 'z korzeniem '
            a+= '4'
          else:
            a += '4h'
    else:
      f = '0'
      a = '0'
      g = 0
      b = "brak"
  else:
    a = '0b'

  if tooth.exists == False:
    context['status'] = "Brak"
  elif Tooth_destructions.objects.filter(tooth = tooth, healed = False).exists():

    context['status'] = "Uszkodzony"
  elif Tooth_destructions.objects.filter(tooth = tooth).exists():
    context['status'] = "Wyleczony"
  else:
    context['status'] = "Zdrowy"
  context['destroyed'] = Tooth_destructions.objects.filter(tooth = tooth, healed = False).count()
  context['fixed'] = Tooth_destructions.objects.filter(tooth = tooth, healed = True).count()

  if request.POST:
    form = tooth_rentgen_form(request.POST, request.FILES, tooth_id = tooth_id)
    if form.is_valid():
      form.save()
    return redirect('tooth_info', tooth_id)
  else:
    form = tooth_rentgen_form(tooth_id = tooth_id)  
  images = Tooth_rentgen.objects.filter(tooth = tooth)
  context['patient'] = tooth.patient
  context['images'] = images
  context['form'] = form  
  context['tooth_id'] = tooth_id


 # toothimg = str(tooth.number) + tooth.level[0] + tooth.side[0]+ "/"+a+".png"
  toothimg = "8dl/"+a+".png"
  context['toothimg'] = toothimg


  return render(request,"tooth/info_about.html",context)

@login_required
@user_is_dentist
@user_is_fully_registered
def tooth_all_heal_view(request, side, tooth_id):
  user = request.user
  context = {}
  tooth = get_object_or_404(Tooth, id = tooth_id)
  dentist = get_object_or_404(Dentist, account = user)
  if not tooth.patient.dentist.filter(id = dentist.id).exists():
    return redirect('/')
  if side == "all":
    td = Tooth_destructions.objects.filter(tooth = tooth, healed = False)
  elif side == "left":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "left", healed = False)
  elif side == "leftkorz":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "left", healed = False, status = 4)
    if Tooth_destructions.objects.filter(tooth = tooth, side = "left", healed = False, status = 4).exists():
      td += Tooth_destructions.objects.filter(tooth = tooth, side = "left", healed = False, status = 5)
    else:
      td = Tooth_destructions.objects.filter(tooth = tooth, side = "left", healed = False, status = 5)
  elif side == "right":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "right", healed = False)
  elif side == "rightkorz":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "right", healed = False, status = 4)
    if Tooth_destructions.objects.filter(tooth = tooth, side = "right", healed = False, status = 4).exists():
      td += Tooth_destructions.objects.filter(tooth = tooth, side = "right", healed = False, status = 5)
    else:
      td = Tooth_destructions.objects.filter(tooth = tooth, side = "right", healed = False, status = 5)
  else:
    return redirect('/')
  for t in td:
    t.healed = True
    t.save()
  if not Tooth_destructions.objects.filter(tooth = tooth, healed = False).exists():
    if tooth.status == "chory":
      tooth.status = "wyleczony"
      tooth.save()
  return redirect('update_data', tooth_id)

@is_ajax_dec
@login_required
@user_is_dentist
@user_is_fully_registered
def tooth_side_destructions(request, side, tooth_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth, id = tooth_id)
  if not tooth.patient.dentist.filter(id = dentist.id).exists():
    return redirect('/')
  dentist = get_object_or_404(Dentist, account = user)
  today = datetime.today().date()
  time = datetime.now().time()
  if side == "left":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "left")
  elif side == "leftkorz":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "left", status = 4)
    if Tooth_destructions.objects.filter(tooth = tooth, side = "left", status = 4).exists():
      td += Tooth_destructions.objects.filter(tooth = tooth, side = "left", status = 5)
    else:
      td = Tooth_destructions.objects.filter(tooth = tooth, side = "left", status = 5)
  elif side == "right":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "right",)
  elif side == "rightkorz":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "right", status = 4)
    if Tooth_destructions.objects.filter(tooth = tooth, side = "right", status = 4).exists():
      td += Tooth_destructions.objects.filter(tooth = tooth, side = "right", status = 5)
    else:
      td = Tooth_destructions.objects.filter(tooth = tooth, side = "right", status = 5)
  elif side == "rightkorzlow":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "right", status = 5)
  elif side == "leftkorzlow":
    td = Tooth_destructions.objects.filter(tooth = tooth, side = "left", status = 5)
  else:
    return redirect('/')
  a = []
  for t in td:
    if tooth_healing_destruction.objects.filter(Q(tooth_destructions = t, visit__day_of_visit__gt = today )|Q(tooth_destructions = t, visit__day_of_visit = today, visit__time_end_visit__gt = time)).exists():
      a.append(True)
    else:
      a.append(False)
  lista = zip(td,a)
  data['form_is_fine'] = True
  context['tooth_destructions'] = lista
  context['tooth_id'] = tooth_id
  data['tooth'] = tooth.id 
  context['in_tooth_view'] = True
  data['html_form'] = render_to_string('tooth/all_tooth_destructions.html',
        context,
        request=request,
    )
  return JsonResponse(data)

@is_ajax_dec
def add_rentgen_view(request, tooth_id=""):
  user = request.user
  context = {}
  data = dict()
  if request.POST:
    form = tooth_rentgen_form(request.POST, request.FILES, tooth_id = None)
    print(form.instance)
    if form.is_valid():
      form.save()
      data['form_is_fine'] = True
      return redirect('tooth_info', tooth_id)
    else:
      print("impossible")
      print(form.errors)
      data['form_is_fine'] = False
  else:
    form = tooth_rentgen_form(tooth_id = tooth_id)  
  context['form'] = form  
  context['tooth_id'] = tooth_id
  data['html_form'] = render_to_string('tooth/add_rentgen.html',
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
def CheckToothStatusView(request, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  curr_visit = get_object_or_404(Visit, id = visit_id)
  Tooth = curr_visit.Tooth_Repaired.all()
  if Tooth.count() == 0:
    context['no_tooth'] = True
  data['form_is_fine'] = True
  context['Tooth'] = Tooth
  b = []
  d = []
  for tooth in Tooth:

    c = ''
    if tooth.exists == False:
      c = '0b'
    else:
      if Tooth_destructions.objects.filter(tooth = tooth).exists():

        d +=  tooth_healing_destruction.objects.filter(tooth_destructions__tooth = tooth, visit = curr_visit)
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
            c += '1'
          else:
            c += '1h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
            c+= '2'
          else:
            c+= '2h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
            c += '3'
          else:
            c += '3h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
            c+= '4'
          else:
            c += '4h'
      else:
        c = '0'


    toothimg ="8dl/"+c+".png"
    b.append(toothimg)
  for th in d:
    form  = tooths_healing_form(instance = th)
  lista = zip(Tooth,b)
  context['visit_id'] = visit_id
  context['tooth_destructions'] = d
  context['lista'] = lista
  data['visit_creation'] = True
  data['modal'] = '#visit_tooth_modal'
  data['html_form'] = render_to_string('tooth/check_visit_tooth.html',
        context,
        request=request,
    )
  return JsonResponse(data)

@is_ajax_dec
def ToothUpdateDestructionsStatusView(request,th_id):
  user = request.user
  context = {}
  data = dict()
  print(th_id)
  tooth_healing = get_object_or_404(tooth_healing_destruction, id = th_id)
  if request.POST:
    form = tooths_healing_form(request.POST, instance = tooth_healing)
    if form.is_valid():
      form.save()
      return redirect('check_updated_tooth_status', tooth_healing.tooth_destructions.tooth.id, tooth_healing.visit.id)
    else:
      print(form.errors)
      context['form_is_fine'] = False
  return JsonResponse(data)

@login_required
@user_is_dentist
@user_is_fully_registered
def ChangeToothActive(request,tooth_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth,id  = tooth_id)
  if not tooth.patient.dentist.filter(id = dentist.id).exists():
    return redirect('/')
  if tooth.active == False:
    tooth.active = True
  else:
    tooth.active = False
  tooth.save()
  return redirect('tooth_info', tooth_id)

@login_required
@user_is_dentist
@user_is_fully_registered
def ReturnMlecznyTooth(request,tooth_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth,id  = tooth_id)
  if not tooth.patient.dentist.filter(id = dentist.id).exists():
    return redirect('/')
  if Tooth.objects.filter(side = tooth.side,level = tooth.level, number = tooth.number,tooth_type = "mleczny",replaced = True).exists():
    toothold = get_object_or_404(Tooth,side = tooth.side,level = tooth.level, number = tooth.number,tooth_type = "mleczny",replaced = True)
    toothold.replaced = False
    toothold.save()
  else:
    toothold = Tooth.objects.create(side = tooth.side,patient = tooth.patient,level = tooth.level, number = tooth.number,tooth_type = "mleczny",replaced = False)
  tooth.delete()
  return redirect('tooth_info', toothold.id)

@is_ajax_dec
def CheckUpdatedStatusView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  tooth = get_object_or_404(Tooth, id = tooth_id)
  visit = get_object_or_404(Visit, id = visit_id)
  th = tooth_healing_destruction.objects.filter(tooth_destructions__tooth = tooth, visit = visit)
  data['form_is_fine'] = True
  context['tooth_destructions'] = th
  data['tooth'] = tooth.id
  context['a'] = tooth
  data['html_form'] = render_to_string('tooth/snippets/check_visit_tooth_snippet.html',
        context,
        request=request,
    )
  return JsonResponse(data)


@is_ajax_dec
def CheckUpdatedStatusImgView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  tooth = get_object_or_404(Tooth, id = tooth_id)
  visit = get_object_or_404(Visit, id = visit_id)
  th = tooth_healing_destruction.objects.filter(tooth_destructions__tooth = tooth, visit = visit)
  data['form_is_fine'] = True
  context['tooth_destructions'] = th
  data['tooth'] = tooth.id
  context['a'] = tooth
  c = ''
  if tooth.exists == False:
    c = '0b'
  else:
    if Tooth_destructions.objects.filter(tooth = tooth).exists():
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
          c += '1'
        else:
          c += '1h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
          c+= '2'
        else:
          c+= '2h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
          c += '3'
        else:
          c += '3h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
          c+= '4'
        else:
          c += '4h'
    else:
      c = '0'


  toothimg ="8dl/"+c+".png"
  data['toothimg'] = toothimg
  print("possible")
  data['html_form'] = render_to_string('tooth/snippets/check_visit_tooth_snippet.html',
        context,
        request=request,
    )
  return JsonResponse(data)  


def ClearHealingView(request, th_id):
  user = request.user
  th = get_object_or_404(tooth_healing_destruction, id = th_id)
  visit = th.visit
  tooth = th.tooth_destructions.tooth
  th.delete()
  return redirect('check_updated_tooth_status', tooth.id, visit.id)

def ClearHealingNiView(request, td_id, visit_id):
  user = request.user
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  td = get_object_or_404(Tooth_destructions, id = td_id)
  th = get_object_or_404(tooth_healing_destruction, tooth_destructions = td, visit = visit)
  visit = th.visit
  tooth = th.tooth_destructions.tooth
  th.delete()
  return redirect('check_updated_tooth_status', tooth.id, visit.id)

@is_ajax_dec
def EditVisitToothDestructionsView(request, td_id ,visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  td = get_object_or_404(Tooth_destructions, id = td_id)
  if request.POST:
    form = tooth_destroy_form(request.POST, instance = td, tooth = td.tooth)
    if form.is_valid:
      form.save()
      return redirect('check_updated_tooth_img_status', td.tooth.id, visit.id)
  else:
    form = tooth_destroy_form(instance = td, tooth = td.tooth)
  context['visit_id'] = visit_id  
  context['form'] = form
  data['html_form'] = render_to_string('tooth/visit_tooth_destruction_edit.html',
      context,
      request = request,
    )
  return JsonResponse(data)

@is_ajax_dec
def EditToothDestructionsView(request, td_id):
  user = request.user
  context = {}
  data = dict()
  td = get_object_or_404(Tooth_destructions, id = td_id)
  if request.POST:
    form = tooth_destroy_form(request.POST, instance = td, tooth = td.tooth)
    if form.is_valid:
      form.save()
      return redirect("update_data", td.tooth.id)
  else:
    form = tooth_destroy_form(instance = td, tooth = td.tooth)
  context['on_tooth_url'] = True
  context['form'] = form
  data['html_form'] = render_to_string('tooth/visit_tooth_destruction_edit.html',
      context,
      request = request,
    )
  return JsonResponse(data)

@is_ajax_dec
def NewVisitToothDestructionView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  tooth = get_object_or_404(Tooth, id = tooth_id)
  visit = get_object_or_404(Visit, id = visit_id)
  if request.POST:
    form = tooth_destroy_form(request.POST, tooth = tooth)
    if form.is_valid:
      if tooth.status != "chory":
        tooth.status = "chory"
        tooth.save()
      form.save()
      b = tooth_healing_destruction(visit = visit, tooth_destructions = form.instance)
      b.save()
      return redirect('check_updated_tooth_img_status', tooth.id, visit.id)
  else:
    form = tooth_destroy_form(tooth = tooth)
  context['form'] = form
  context['new_td'] = True
  context['tooth_id'] = tooth_id
  context['visit_id'] = visit_id
  data['html_form'] = render_to_string('tooth/visit_tooth_destruction_edit.html',
      context,
      request = request,
    )
  return JsonResponse(data)

@is_ajax_dec
def CheckAllDesStatusView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  tooth = get_object_or_404(Tooth, id = tooth_id)
  td = Tooth_destructions.objects.filter(tooth = tooth)
  visit = get_object_or_404(Visit, id = visit_id)
  a = []
  for d in td:
    if tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
      a += "t"
    else:
      a += "n"
  lista = zip(td,a)
  data['form_is_fine'] = True
  context['tooth_destructions'] = lista
  context['visit_id'] = visit_id
  context['tooth_id'] = tooth_id
  context['show_all_destructions'] = True
  data['tooth'] = tooth.id

  data['html_form'] = render_to_string('tooth/all_tooth_destructions.html',
        context,
        request=request,
    )
  return JsonResponse(data)

@is_ajax_dec
def CheckAllTotthDesStatusView(request, tooth_id):
  user = request.user
  context = {}
  data = dict()
  today = datetime.today().date()
  time = datetime.now().time()
  tooth = get_object_or_404(Tooth, id = tooth_id)
  td = Tooth_destructions.objects.filter(tooth = tooth)
  a = []
  for t in td:
    if tooth_healing_destruction.objects.filter(Q(tooth_destructions = t, visit__day_of_visit__gt = today )|Q(tooth_destructions = t, visit__day_of_visit = today, visit__time_end_visit__gt = time)).exists():
      a.append(True)
    else:
      a.append(False)
  lista = zip(td,a)
  data['form_is_fine'] = True
  context['tooth_destructions'] = lista
  context['tooth_id'] = tooth_id
  data['tooth'] = tooth.id 
  context['in_tooth_view'] = True
  data['html_form'] = render_to_string('tooth/all_tooth_destructions.html',
        context,
        request=request,
    )
  return JsonResponse(data)

@is_ajax_dec
def HealDestructionView(request, td_id):
  user = request.user
  context = {}
  data = dict()
  dentist = get_object_or_404(Dentist, account = user)
  td = get_object_or_404(Tooth_destructions, id = td_id)
  if request.POST:
    form = tooth_healing_form_new(request.POST, td_id = td_id)
    if form.is_valid():
      form.tooth_destructions = td
      form.save()
      th = get_object_or_404(tooth_healing_destruction, id = form.instance.id)
      th.dentist = dentist
      th.save()
      context['form_is_fine'] = True
      td.healed = True
      td.save()
      tooth = td.tooth
      if not Tooth_destructions.objects.filter(tooth = tooth, healed = False).exists():
        if tooth.status == "chory":
          tooth.status = "wyleczony"
          tooth.save()
      return redirect('update_data', td.tooth.id)
    else:
      context['form_is_fine'] = False
      print(form.errors)
  else:
    form = tooth_healing_form_new(td_id = td_id)
  context['form'] = form
  context['td_id'] = td_id
  data['html_form'] = render_to_string('tooth/new_healing.html',
        context,
        request=request,
  )
  return JsonResponse(data)

@is_ajax_dec
def HealDestructionEditView(request, th_id):
  user = request.user
  context = {}
  data = dict()
  dentist = get_object_or_404(Dentist, account = user)
  th =get_object_or_404(tooth_healing_destruction, id = th_id)
  td =  th.tooth_destructions
  if request.POST:
    form = tooth_healing_form_new(request.POST, instance = th, td_id = td.id)
    if form.is_valid():
      form.save()
      return redirect('healing_history', td.id)
    else:
      context['form_is_fine'] = False
      print(form.errors)
  else:
    form = tooth_healing_form_new( instance = th, td_id = td.id)
  context['form'] = form
  context['edit'] = True
  data['html_form'] = render_to_string('tooth/new_healing.html',
        context,
        request=request,
  )
  return JsonResponse(data)


def HealDestructionRemoveView(request, th_id):
  user = request.user
  context = {}
  data = dict()
  dentist = get_object_or_404(Dentist, account = user)
  th =get_object_or_404(tooth_healing_destruction, id = th_id)
  td = th.tooth_destructions 
  tooth = td.tooth
  th.delete()
  if not tooth_healing_destruction.objects.filter(tooth_destructions = td).exists():
    td.healed = False
    if tooth.status != "chory":
      tooth.status = "chory"
      tooth.save()
    td.save()
  return redirect('healing_history', td.id)


def SetAsHealedOrDestroyedView(request, td_id):
  user = request.user
  context = {}

  td = get_object_or_404(Tooth_destructions, id = td_id)
  if td.healed == True:
    td.healed = False
    tooth = td.tooth
    if tooth.status != "chory":
      tooth.status = "chory"
      tooth.save

  else:
    td.healed = True
    tooth = td.tooth
    if not Tooth_destructions.objects.filter(tooth = tooth, healed = False).exists():
      if tooth.status == "chory":
        tooth.status = "wyleczony"
        tooth.save()
  td.save()
  return redirect('update_data', td.tooth.id)

def DeleteRentgenView(request, ren_id):
  rentgen = get_object_or_404(Tooth_rentgen,id = ren_id)
  tooth = rentgen.tooth
  rentgen.delete()
  return redirect('tooth_info', tooth.id)



@is_ajax_dec
def UpdataDataView(request, tooth_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth, id = tooth_id)
  c = ''
  if tooth.exists == False:
    c = '0b'
  else:
    if Tooth_destructions.objects.filter(tooth = tooth).exists():
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
          c += '1'
        else:
          c += '1h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
          c+= '2'
        else:
          c+= '2h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
          c += '3'
        else:
          c += '3h'
      if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
          c+= '4'
        else:
          c += '4h'
    else:
      c = '0'
  toothimg ="8dl/"+c+".png"
  data['form_is_fine'] = True
  data['toothimg'] = toothimg
  return JsonResponse(data)

@is_ajax_dec
def AddToothDestruction(request,tooth_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth, id = tooth_id)
  if request.POST:
    form = tooth_destroy_form(request.POST, tooth = tooth)
    if form.is_valid:
      if tooth.status!="chory":
        tooth.status = "chory"
        tooth.save()
      form.save()
      return redirect('update_data', tooth.id)
  else:
    form = tooth_destroy_form(tooth = tooth)
  context['form'] = form
  context['new_td_from_t'] = True
  context['tooth_id'] = tooth_id
  data['html_form'] = render_to_string('tooth/visit_tooth_destruction_edit.html',
      context,
      request = request,
    )
  return JsonResponse(data)

@is_ajax_dec
def DeleteTooth(request,tooth_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth, id = tooth_id)
  if tooth.exists == False:
    tooth.exists = True
    tooth.save()
    return redirect('update_data', tooth_id)
  elif tooth.tooth_type == "mleczny":
    toot = Tooth(number = tooth.number, level = tooth.level, side = tooth.side, patient = tooth.patient, tooth_type = "stały", exists = True)
    toot.save()
    tooth.replaced = True
    tooth.save()
    return redirect('update_data', tooth_id)
  else:
    tooth.exists = False
    tooth.save()
    return redirect('update_data', tooth_id)


@is_ajax_dec
def DeleteToothDestructions(request,td_id):
  user = request.user
  context = {}
  td = get_object_or_404(Tooth_destructions, id = td_id)
  tooth = td.tooth
  td.delete()
  tooth = td.tooth
  if tooth.status == "chory":
    tooth.status = "wyleczony"
    tooth.save()
  return redirect('update_data',tooth.id ) 




def AddTotthDestructiontoVisitView(request, td_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  td = get_object_or_404(Tooth_destructions, id = td_id)
  visit = get_object_or_404(Visit, id = visit_id)
  th = tooth_healing_destruction(visit = visit, tooth_destructions = td)
  th.save()
  return redirect('check_updated_tooth_status', td.tooth.id, visit.id)

def AddAllTotthDestructiontoVisitView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  tooth = get_object_or_404(Tooth, id = tooth_id)

  td = Tooth_destructions.objects.filter(tooth = tooth)
  th = []
  for d in td:
    if not tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
      th.append(tooth_healing_destruction(visit = visit, tooth_destructions = d))
  tooth_healing_destruction.objects.bulk_create(th)

  return redirect('check_updated_tooth_status', tooth.id, visit.id)

def AddAlNotHealedTotthDestructiontoVisitView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  tooth = get_object_or_404(Tooth, id = tooth_id)

  td = Tooth_destructions.objects.filter(tooth = tooth, healed = False)
  th = []
  for d in td:
    if not tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
      th.append(tooth_healing_destruction(visit = visit, tooth_destructions = d))
  tooth_healing_destruction.objects.bulk_create(th)

  return redirect('check_updated_tooth_status', tooth.id, visit.id)

def AddAlNotHealedandNotPlannedHealingTotthDestructiontoVisitView(request, tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  tooth = get_object_or_404(Tooth, id = tooth_id)

  td = Tooth_destructions.objects.filter(tooth = tooth, healed = False, planned_healing = False)
  th = []
  for d in td:
    if not tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
      th.append(tooth_healing_destruction(visit = visit, tooth_destructions = d))
  tooth_healing_destruction.objects.bulk_create(th)
  return redirect('check_updated_tooth_status', tooth.id, visit.id)




def AddAllVisitToothAllTotthDestructiontoVisitView(request, visit_id):
  user = request.user
  context = {}
  data = dict()
  visit = get_object_or_404(Visit, id = visit_id)
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  tooths = visit.Tooth_Repaired.all()
  th = []
  for tooth in tooths:
    td = Tooth_destructions.objects.filter(tooth = tooth)

    for d in td:
      if not tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
        th.append(tooth_healing_destruction(visit = visit, tooth_destructions = d))
  tooth_healing_destruction.objects.bulk_create(th)

  return redirect('check_tooth_status', visit.id)

def AddAllVisitToothNotHealedAllTotthDestructiontoVisitView(request, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  tooths = visit.Tooth_Repaired.all()
  th = []
  for tooth in tooths:
    td = Tooth_destructions.objects.filter(tooth = tooth, healed = False)

    for d in td:
      if not tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
        th.append(tooth_healing_destruction(visit = visit, tooth_destructions = d))
  tooth_healing_destruction.objects.bulk_create(th)

  return redirect('check_tooth_status', visit.id)

def AddAllVisitToothNotHealedAndNotPlannedHealingAllTotthDestructiontoVisitView(request, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  tooths = visit.Tooth_Repaired.all()
  th = []
  for tooth in tooths:
    td = Tooth_destructions.objects.filter(tooth = tooth, healed = False, planned_healing = False)

    for d in td:
      if not tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions = d).exists():
        th.append(tooth_healing_destruction(visit = visit, tooth_destructions = d))
  tooth_healing_destruction.objects.bulk_create(th)

  return redirect('check_tooth_status', visit.id)

@is_ajax_dec
def HealingHistoryView(request, td_id):
  user = request.user
  context = {}
  data = dict()
  td = get_object_or_404(Tooth_destructions, id = td_id)
  today_data = datetime.today()
  today = datetime.today().date()
  time = datetime.now().time()
  dentist = get_object_or_404(Dentist, account = user)
  context['dentist'] = dentist 

  th = tooth_healing_destruction.objects.filter(Q(tooth_destructions = td, visit__day_of_visit__lt = today )|Q(tooth_destructions = td, visit__day_of_visit = today, visit__time_end_visit__lt = time)|Q(tooth_destructions = td, date_of_fixing__lt = today_data)).order_by('visit__day_of_visit','visit__time_end_visit')
  data['tooth'] = td.tooth.id
  context['th'] = th
  context['tooth_url'] = True 
  data['form_is_fine'] = True
  data['html_form'] = render_to_string('tooth/healing_history.html',
        context,
        request=request,
    )
  return JsonResponse(data)

@is_ajax_dec
def AddToothToVisitView(request, visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUserWithPatient(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)
  patient = visit.Patient
  Toothsa = Tooth.objects.filter(patient = patient,side="lewy",level="górny" , replaced = False).order_by('-level','side','-number')
  Toothsb= Tooth.objects.filter(patient = patient, side="prawy",level="górny" , replaced = False).order_by('number')
  Toothsc= Tooth.objects.filter(patient = patient, side="lewy",level="dolny" , replaced = False).order_by('-level','side','-number')
  Toothsd= Tooth.objects.filter(patient = patient, side="prawy",level="dolny" , replaced = False).order_by('-level','side','number')
  a = []
  for t in Toothsa:
    a.append(t)
  for t in Toothsb:
    a.append(t)
  for t in Toothsc:
    a.append(t)
  for t in Toothsd:
    a.append(t)
  b = []
  f = []
  for tooth in a:
    c = ''
    if tooth.exists == False:
      c = '0b'
    else:
      if tooth in visit.Tooth_Repaired.all():
        f +="t"
      else:
        f +="n"
      if Tooth_destructions.objects.filter(tooth = tooth).exists():
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left').exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', healed = False).exists():
            c += '1'
          else:
            c += '1h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'left', status = 5, healed = False).exists():
            c+= '2'
          else:
            c+= '2h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right').exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', healed = False).exists():
            c += '3'
          else:
            c += '3h'
        if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4 ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5).exists():
          if Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 4, healed = False ).exists() or Tooth_destructions.objects.filter(tooth = tooth, side = 'right', status = 5, healed = False).exists():
            c+= '4'
          else:
            c += '4h'
      else:
        c = '0'
    toothimg ="8dl/"+c+".png"
    b.append(toothimg)
  lista = zip(a,b,f)
  if request.user.is_dentist == False and request.user.is_receptionist == False:
    context['addtoottovisit'] = True
  elif visit.Type_of =="wyrywanie":
    context['remove'] = True
  data['form_is_fine'] = True
  data['visit_creation'] = True
  data['modal'] = '#visit_add_tooth_to_visit_modal'
  context['info'] = lista
  context['patient'] = patient
  context['visit'] = visit_id

  data['html_form'] = render_to_string('tooth/add_view.html',
        context,
        request=request,
    )
  return JsonResponse(data)

@is_ajax_dec
def AddChosenToothToVisitView(request,tooth_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  tooth = get_object_or_404(Tooth, id = tooth_id)
  if not CheckifVisitUserWithPatient(visit_id = visit_id, user_id= user.id):
    raise Http404
  visit = get_object_or_404(Visit, id = visit_id)

  if tooth in visit.Tooth_Repaired.all():
    data['add'] = 'False'
    visit.Tooth_Repaired.remove(tooth)
    tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions__tooth = tooth).delete()
  else:
    data['add'] = 'True' 
    visit.Tooth_Repaired.add(tooth)
  visit.save()
  data['tooth'] = tooth.id
  return JsonResponse(data)


@is_ajax_dec
def RemoveToothFromVisitView(request,tooth_id,visit_id):
  user = request.user
  context = {}
  data = dict()
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  tooth = get_object_or_404(Tooth, id = tooth_id)
  visit = get_object_or_404(Visit, id = visit_id)
  visit.Tooth_Repaired.remove(tooth)
  tooth_healing_destruction.objects.filter(visit = visit, tooth_destructions__tooth = tooth).delete()
  return redirect('check_tooth_status', visit.id)


def PropositionOfHealinTypeView(request, td_id, visit_id):
  user = request.user
  context = {}
  data = dict()
  td = get_object_or_404(Tooth_destructions, id = td_id )
  visit = get_object_or_404(Visit, id = visit_id)
  th = tooth_healing_destruction.objects.filter(tooth_destructions = td)
  a = []
  b = []
  c = []
  d = []
  e = [None] * 3
  h = []
  i = []
  thist = []
  alltooths = []

  a.append("kanałowe")
  b.append(th.filter(type_of = "kanałowe").count())
  a.append("plomba")
  b.append(th.filter(type_of = "plomba").count())
  a.append("czyszczenie")
  b.append(th.filter(type_of = "czyszczenie").count())
  a.append("leczenie długotrwałe")
  b.append(th.filter(type_of = "leczenie długotrwałe").count())
  a.append("lekarstwo")
  b.append(th.filter(type_of = "lekarstwo").count())
  a.append("operacja")
  b.append(th.filter(type_of = "operacja").count())
  a.append("inne")
  b.append(th.filter(type_of = "inne").count())


  tooth = td.tooth
  th = tooth_healing_destruction.objects.filter(tooth_destructions__tooth = tooth, tooth_destructions__status = td.status)
  c.append(th.filter(type_of = "kanałowe").count())
  c.append(th.filter(type_of = "plomba").count())
  c.append(th.filter(type_of = "czyszczenie").count())
  c.append(th.filter(type_of = "leczenie długotrwałe").count())
  c.append(th.filter(type_of = "lekarstwo").count())
  c.append(th.filter(type_of = "operacja").count())
  c.append(th.filter(type_of = "inne").count())
  th = tooth_healing_destruction.objects.filter(tooth_destructions__tooth__number = tooth.number, tooth_destructions__status = td.status)  
  d.append(th.filter(type_of = "kanałowe").count())
  d.append(th.filter(type_of = "plomba").count())
  d.append(th.filter(type_of = "czyszczenie").count())
  d.append(th.filter(type_of = "leczenie długotrwałe").count())
  d.append(th.filter(type_of = "lekarstwo").count())
  d.append(th.filter(type_of = "operacja").count())
  d.append(th.filter(type_of = "inne").count())
  listab = zip(a,b)
  listac = zip(a,c)
  listad = zip(a,d)

  f = 0
  for  name in listab:
    if name[1]>f:
      e[0] = name[0]
      f = name[1]
    h.append(name)

  if f == 0:
    i.append(False)
  else:
    i.append(True)
  f = 0
  for  name in listac:
    if name[1]>f:

      e[1] = name[0]
      f = name[1]
    thist.append(name)
  if f == 0:
    i.append(False)
  else:
    i.append(True)
  print(f)
  f = 0
  for  name in listad:
    if name[1]>f:
      e[2] = name[0]
      f = name[1]
    alltooths.append(name)
  if f == 0:
    i.append(False)
  else:
    i.append(True)
  context['this_td_prop'] = e[0]
  context['this_tooth_prop'] = e[1]
  context['all_tooth_with_this_number_prop'] = e[2]

  context['this_td_has_proposition'] = i[0]
  context['this_tooth_has_proposition'] = i[1]
  context['all_this_tooth_number_has_proposition'] = i[2]

  context['only_this_destruction'] = h
  context['all_tooth_destructions'] = thist 
  context['all_tooth_numbers'] = alltooths
  context['is_able_to_find'] = i
  context['td'] = td
  context['visit'] = visit

  data['html_form'] = render_to_string('tooth/proposition_of_healing.html',
        context,
        request=request,
    )
  return JsonResponse(data)


def UpdateHealingTypeView(request,td_id, type_of, visit_id):
  user = request.user
  td = get_object_or_404(Tooth_destructions, id = td_id)
  visit = get_object_or_404(Visit, id = visit_id)
  if not CheckifVisitUser(visit_id = visit_id, user_id= user.id):
    raise Http404
  th = get_object_or_404(tooth_healing_destruction, tooth_destructions = td, visit = visit)
  th.type_of = type_of
  th.save()
  return redirect('check_updated_tooth_status', td.tooth.id, visit.id)


@is_ajax_dec
def AddVisitCost(request,visit_id):
  data = dict()
  visit = get_object_or_404(Visit, id = visit_id)
  cennik = get_object_or_404(Cennik, dentist = visit.Dentist)
  if visit.Type_of == "wyrywanie":
    a = visit.Tooth_Repaired.count()

    visit.cost = a * cennik.wyrywanie
    visit.save()
  elif visit.Type_of == "leczenie":
    a = 0
    for tooth in visit.Tooth_Repaired.all():
      th = tooth_healing_destruction.objects.filter(tooth_destructions__tooth = tooth, visit = visit)
      if th.filter(type_of = "operacja").exists():
        a += cennik.operacja
      elif th.filter(type_of = "kanałowe").exists():
        a += cennik.kanałowe
      elif th.filter(type_of = "plomba").exists():
        a += cennik.plomba
      elif th.filter(type_of = "lekarstwo").exists():
        a += cennik.lekarstwo
      elif th.filter(type_of = "leczenie_długotrwałe").exists():
        a += cennik.leczenie_długotrwałe
      elif th.filter(type_of = "czyszczenie").exists():
        a += cennik.czyszczenie
      else:
        a += cennik.inne
    visit.cost = a
    visit.save()

  return JsonResponse(data)





