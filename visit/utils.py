from datetime import datetime, timedelta, time,date
from calendar import HTMLCalendar
from .models import Visit
from  account.models import Patient,Dentist,Account
from django.shortcuts import render,  get_object_or_404,redirect
from django.db.models import Q

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None,user=None):
        self.year = year
        self.month = month

        super(Calendar, self).__init__()

    # formatuje dzień jako td
    def formatday(self, day, visits,a,b):
        visit_per_day = visits.filter(day_of_visit__day=day).order_by('time_end_visit')

        d = ''
        for visit in visit_per_day:
            if visit.status == 'nie potwierdzona' or visit.status == 'do zatwierdzenia przez pacjenta':
                None
            else:

                d += f"<a   data-toggle='modal' data-target='#basicExampleModal{visit.id}'><div class='event'"
                if visit.status =='odbyła sie':
                    d +=f"style=' background-color:#f2f2f2'"  
                elif visit.status =='odwołana':
                    d +=f"style=' background-color:#ffccff'"

                elif visit.status =='odwołana przez pacjenta':
                    d +=f"style=' background-color:#ffcccc'"

                elif visit.status =='zaplanowana':
                    d +=f"style=' background-color: #e6ffff'"    
                elif visit.status ==' zmiana daty':
                    d +=f"style=' background-color:#ffdb99'"  
                elif visit.status =='zmiana daty przez pacjenta':
                    d +=f"style=' background-color:#ffff99'"  
                if a!=None:
                    d +=f"><div class='event-desc'>Rodzaj wizyty: {visit.Type_of} <br> Pacjent: {visit.Patient}<br> Stan wizyty: {visit.status}</div><div class='event-time'>{visit.time_of_the_visit} - {visit.time_end_visit}</div></div>   </a>"

                elif b!=None:
                    d += f"><div class='event-desc'>Rodzaj wizyty: {visit.Type_of} <br> Dentysta: {visit.Dentist}<br> Stan wizyty: {visit.status}</div><div class='event-time'>{visit.time_of_the_visit} - {visit.time_end_visit}</div></div>   </a>"
                d+=f"<div class='modal fade' id='basicExampleModal{visit.id}' name='special' tabindex='-1' role='dialog' aria-labelledby='exampleModalLabel'  aria-hidden='true'>"
                d+=f"  <div class='modal-dialog' role='document'>"
                d+=f"    <div class='modal-content'>"
                d+=f"      <div class='modal-header'>"
                d+=f"        <h5 class='modal-title' id='exampleModalLabel'>Szczegóły wizyty</h5>"
                d+=f"        <button type='button' class='close' data-dismiss='modal' aria-label='Close'>"
                d+=f"          <span aria-hidden='true'>&times;</span>"
                d+=f"        </button>"
                d+=f"      </div>"
                d+=f"      <div class='modal-body'><center>"
                d+=f"<p><b>Pacjent: </b>{visit.Patient.First_Name} {visit.Patient.Surname}</p>"
                d+=f"  <p><b>Dentysta: </b>{visit.Dentist.First_Name}  {visit.Dentist.Surname}</p>"
                d+=f"  <p><b>Status Wizyty: </b>{visit.status}</p>"
                d+=f"  <p><b>Rodzaj Wizyty: </b>{visit.Type_of}</p>"
                d+=f"  <p><b>Dzień wizyty:</b>{visit.day_of_visit}</p>"
                d+=f"  <p><b>Czas wizyty:</b>{visit.time_of_the_visit}</p>"
                d+=f"  <p><b>Czas zakończenia wizyty: </b>{visit.time_end_visit}</p>"
                if visit.Type_of!="wizyta kontrolna":
                    toot = visit.Tooth_Repaired.all()
                    d+=f"<p><b>Leczone zęby:  </b>"
                    for t in toot:
                        d+=f"{t}, "
                    d+=f"</p>"
                d+=f"<p><b>Szczegóły: </b>{visit.desc}</p>"
                d+=f"<p><b>Opłata za wizytę: </b>{visit.cost}</p></center>"
                d+=f"      </div>"
                d+=f"      <div class='modal-footer'><center>"
                d+=f"        <a class='btn btn-secondary' data-dismiss='modal'>Zamknij</a>"
                if a!= None:
                    d+=f"        <a class='btn btn-primary change_date' id='{visit.id}' data-url='{'/visit/date_change/'}{visit.id}'>przesuń </a>"
                if visit.status != 'odwołana' and visit.status!='odwołana przez pacjenta' and visit.status!='odbyła sie':
                    d+=f"        <a class='btn btn-primary cancel' id='{visit.id}' data-url='{'/visit/cancel/'}{visit.id}'>Odwołaj</a><br/>"
                elif (visit.status == 'odwołana' and a!=None) or(visit.status =='odwołana przez pacjenta' and b!=None):
                    d+=f"        <a class='btn btn-primary revive' id='{visit.id}' data-url='{'/visit/revive/'}{visit.id}'>Przywróć</a><br/>"                    
                if a!=None:
                    d+=f"      <a class='btn btn-primary specjalne' id='{visit.id}' data-url='{'/visit/editing/'}{visit.id}'>Edytuj</a>"
                    if visit.Type_of == 'leczenie':
                        d+=f"      <a class='btn btn-primary advanced_visit_edit' id='{visit.id}' data-url='/tooth/check_visit_tooth/'{visit.id}'>Edytuj Szczegóły</a>"
                    elif visit.Type_of == 'wyrywanie':
                        d+=f"      <a class='btn btn-primary edit_removing_tooth' id='{visit.id}' data-url='/tooth/check_visit_tooth/'{visit.id}'>Zmień zęby </a>"
                    if visit.status == 'odbyła sie':
                        d+=f"        <a class='btn btn-primary delete_visit' id='{visit.id}' data-url='{'/visit/delete/'}{visit.id}'>wizyta się nie odbyła</a> " 
                    else:                       
                        d+=f"        <a class='btn btn-primary delete_visit' id='{visit.id}' data-url='{'/visit/delete/'}{visit.id}'>Usuń</a> "
                if (visit.status == ' zmiana daty' and b!=None) or (visit.status == 'zmiana daty przez pacjenta' and a!=None):
                    d+=f"        <a class='btn btn-primary revive' id='{visit.id}' data-url='{'/visit/cancel/'}{visit.id}'>Zaakceptuj zmianę</a>"
                d+=f"</center></div>  </div>"
                d+=f"</div>"
                d+=f"</div>"
        if day != 0:

            if (datetime.today().year > self.year) or (datetime.today().year == self.year and datetime.today().month > self.month ) or (datetime.today().year == self.year and datetime.today().month == self.month and datetime.today().day > day):
                return f"<td class = 'past'><ul><span class='date'>{day}</span> {d} </ul></td>"
            elif (datetime.today().year < self.year) or (datetime.today().year == self.year and datetime.today().month < self.month ) or (datetime.today().year == self.year and datetime.today().month == self.month and datetime.today().day < day):
                return f"<td class = 'future'><ul><span class='date'>{day}</span> {d} </ul></td>"    
            else:
                return f"<td class = 'now'><ul><span class='date'>{day}</span> {d} </ul></td>"
        return '<td></td>'

    # formatuje tydzień jako tr 
    def formatweek(self, theweek, visits,a,b):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, visits,a,b)
        return f'<tr> {week} </tr>'

    # formatuje miesiąc jako tabelę
    def formatmonth(self,a,b, withyear=True):
        print("yes")
        if a!=None:
            visits = Visit.objects.filter(day_of_visit__year=self.year, day_of_visit__month=self.month,Dentist=a)
        elif b!=None:
            visits = Visit.objects.filter(day_of_visit__year=self.year, day_of_visit__month=self.month,Patient=b)
        else:
            visits = Visit.objects.filter(day_of_visit__year=self.year, day_of_visit__month=self.month,Dentist=a)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, visits,a,b)}\n'
        return cal