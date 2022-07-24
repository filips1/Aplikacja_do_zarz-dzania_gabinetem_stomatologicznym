from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task
from visit.models import Visit, tooth_healing_destruction
from account.models import *
from datetime import datetime, timedelta, time, date
from django.db.models import Q





@task(name="check-if-new-visit")
def check():
    today = datetime.now().date()
    tomorrow = today + timedelta(1)

    if Visit.objects.filter(Q(day_of_visit = tomorrow,status="zaplanowana")|Q(day_of_visit = tomorrow,status=' zmiana daty')).exists():
        visits =  Visit.objects.filter(Q(day_of_visit = tomorrow,status="zaplanowana")|Q(day_of_visit = tomorrow,status=' zmiana daty'))
        for visit in visits:
            if visit.Patient.account:
                new_info = Wiadomosc(date_of_change = datetime.now(), type_of = "przypomnienie", desc = "Przypominam o jutrzejszej wizycie o godz "+str(visit.time_of_the_visit), target = visit.Patient.account.id )
                new_info.save()
        return 0

    return 0



@task(name="check-if-visit_finished")
def check_finish():
    today = datetime.today().date()
    time = datetime.now().time()
    if Visit.objects.filter(Q(day_of_visit__lt = today) | Q(day_of_visit = today, time_end_visit__lt = time  )).exclude(status = 'odbyła sie').exists():
        visits = Visit.objects.filter(Q(day_of_visit__lt = today) | Q(day_of_visit = today, time_end_visit__lt = time  ))
        for visit in visits:
            if visit.status == "zaplanowana" or visit.status == ' zmiana daty':
                visit.status = 'odbyła sie'
                visit.save()
                if tooth_healing_destruction.objects.filter(visit = visit).exists():
                    th = tooth_healing_destruction.objects.filter(visit = visit)
                    for t in th:
                        if t.tooth_destructions.healed == False:
                            td = t.tooth_destructions
                            td.healed = True
                            td.save()
            else:
                visit.delete()
    return 0
