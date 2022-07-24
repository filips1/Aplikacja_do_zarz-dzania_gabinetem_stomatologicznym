from django.db import models
from  account.models import Account, Dentist, Patient
# Create your models here.
from django.core.exceptions import ValidationError
from tooth.models import Tooth, Tooth_destructions
from datetime import datetime, date, time, timedelta

from django.conf import settings

class Visit(models.Model):
    PLANNED = 'zaplanowana'
    FINISHED = 'odbyła sie'
    CHANGE_DATE = ' zmiana daty'
    CANCELLED = 'odwołana'
    UNAPROVED = 'nie potwierdzona'
    UNAPROVED_BY_PATIENT = 'do zatwierdzenia przez pacjenta'
    CANCELLED_BY_PATIENT = 'odwołana przez pacjenta'
    CHANGE_DATE_BY_PATIENT = 'zmiana daty przez pacjenta'
    KONTROLNA = "wizyta kontrolna"
    LECZENIE = "leczenie"
    WYRYWANIE = "wyrywanie"

    STATUS = [
        (PLANNED, ('Wizyta jest zaplanowana')),
        (FINISHED, ('Wizyta się odbyła')),
        (CHANGE_DATE, ('Data wizyty musi zostać zmieniona')),
        (UNAPROVED, ('Wizyta nie jest zatwierdzona')),
        (CANCELLED, ('odwołana')),
        (CANCELLED_BY_PATIENT, ('odwołane przez pacjenta')),
        (UNAPROVED_BY_PATIENT, ('do zatwierdzenia przez pacjenta')),
        (CHANGE_DATE_BY_PATIENT, ('zmiana daty przez pacjenta')),
    ]

    TYPE_OF = [
        (KONTROLNA, ('wizyta kontrolna')),
        (LECZENIE, ('leczenie')),
        (WYRYWANIE, ("wyrywanie")),
    ]

    day_of_visit = models.DateField(verbose_name='Dzień zaplanowanej wizyty', blank=False)
    time_of_the_visit = models.TimeField(verbose_name='Godzina zaplanowanej wizyty', blank=False)
    time_end_visit = models.TimeField(verbose_name="Godzina końca wizyty", blank=False)
    status = models.CharField(max_length = 50,choices=STATUS,default=PLANNED, blank=False)
    Type_of = models.CharField(max_length=20, choices=TYPE_OF, default=LECZENIE, blank=False)
    Dentist = models.ForeignKey(Dentist, on_delete = models.CASCADE)
    Patient = models.ForeignKey(Patient, on_delete = models.CASCADE)
    Tooth_Repaired = models.ManyToManyField(Tooth, verbose_name='Zęby naprawiane lub wyleczone ', blank = True)
    desc = models.TextField(verbose_name = 'opis przebiegu wizyty', blank=True, null= True)
    cost = models.FloatField(verbose_name = 'zapłata za wizytę', blank = True, null = True)


    def __str__(self):
        return '%s - %s - %s' % (self.time_of_the_visit, self.time_end_visit,self.Patient)

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:    
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (new_end >= fixed_start and new_end <= fixed_end): 
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:
            overlap = True
 
        return overlap

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a href="%s">%s</a>' % (url, str(self.time_of_the_visit))
 
    def clean(self):
        if self.time_end_visit <= self.time_of_the_visit:
            raise ValidationError('Godzina zakończenia nie może być ustawiona przed wizytą')
 
        today = datetime.today().date()
        time = datetime.now().time()
        print(self.day_of_visit)
        if ((self.day_of_visit < today) or (self.day_of_visit == today and self.time_end_visit < time)) and self.status!= "odbyła sie":
            print(self.status)
            raise ValidationError('Wizyta nie może być zaplanowana po czasie')

        if ((self.day_of_visit > today) or (self.day_of_visit == today and self.time_end_visit > time)) and self.status == "odbyła sie":
            raise ValidationError('Żeby wizyta już się odbyła czas wizyty musi być wcześniejszy')



        visits = Visit.objects.filter(day_of_visit=self.day_of_visit)
        
        if visits.exists():
            for visit in visits:
                if self.Dentist == visit.Dentist:
                    if self!= visit:
                        if visit.status!='nie potwierdzona' and visit.status!='do zatwierdzenia przez pacjenta':
                            if self.check_overlap(visit.time_of_the_visit, visit.time_end_visit, self.time_of_the_visit, self.time_end_visit):
                                raise ValidationError(
                                'Zaplanowane wizyty nakładają się na sobie: ' + str(visit.day_of_visit) + ', ' + str(
                                visit.time_of_the_visit) + '-' + str(visit.time_end_visit))






class tooth_healing_destruction(models.Model):
    class Type_of(models.TextChoices):
        KANAŁOWE = "kanałowe"
        PLOMBA = "plomba"
        CZYSZCZENIE = "czyszczenie"
        INNE = "inne"
        LECZENIE_DŁUGOTRWAŁE = "leczenie długotrwałe"
        LEKARSTWO = "lekarstwo"
        OPERACJA = "operacja"
    tooth_destructions = models.ForeignKey(Tooth_destructions, on_delete = models.CASCADE)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null = True, blank = True)
    type_of = models.TextField(choices = Type_of.choices, blank = True, null = True )
    about_healing = models.TextField(blank = True, null = True)
    date_of_fixing = models.DateTimeField(blank = True, null = True)
    dentist = models.ForeignKey(Dentist, null = True, blank = True, on_delete = models.CASCADE)

    def clean(self):
        today = datetime.today().date()
        time = datetime.now().time()
        if self.date_of_fixing!= None:
            if (self.date_of_fixing.date() > today):
                raise ValidationError('Żeby leczenie było wykonane musiało sie ono już odbyć')
    # Create your models here.