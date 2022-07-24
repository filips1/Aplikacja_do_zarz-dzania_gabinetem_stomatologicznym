from django.db import models
from account.models import Patient, Dentist




class Tooth(models.Model):
    class Number(models.IntegerChoices):
        JEDYNKA = 1
        DWÓJKA = 2
        TRÓJKA = 3
        CZWÓRKA = 4
        PIĄTKA = 5
        SZÓSTKA = 6
        SIÓDEMKA = 7
        ÓSEMKA = 8
    class Level(models.TextChoices):
        GÓRNA = 'górny'
        DOLNA = 'dolny'
    class Side(models.TextChoices):
        LEWA = 'lewy'
        PRAWA = 'prawy'
    class Type(models.TextChoices):
        STAŁY = "stały"
        MLECZNY = "mleczny"
    class Status(models.TextChoices):
        ZDROWY = "zdrowy"
        CHORY = "chory"
        WYLECZONY = "wyleczony"
    number = models.IntegerField(choices = Number.choices)
    level = models.TextField(choices = Level.choices)
    side = models.TextField(choices = Side.choices)
    patient = models.ForeignKey(Patient, on_delete = models.CASCADE,)
    tooth_type = models.TextField(choices = Type.choices)
    exists = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    replaced = models.BooleanField(default=False)
    status = models.TextField(choices = Status.choices, default = "zdrowy")

    def __str__(self):
        return '%s - %s - %s' % (self.number, self.level,self.side)



class Tooth_destructions(models.Model):
    class Status(models.TextChoices):
        BARDZO_MAŁE = 1
        MAŁE = 2
        ŚREDNIE = 3
        DUŻE = 4
        BARDZO_DUŻE = 5

    class Side(models.TextChoices):
        LEWA = "left"
        PRAWA = "right"

    class Frontor(models.TextChoices):
        PRZÓD = "front"
        TYŁ = "back"
    class Type_of(models.TextChoices):
        KANAŁOWE = "kanałowe"
        PLOMBA = "plomba"
        CZYSZCZENIE = "czyszczenie"
        INNE = "inne"
        LECZENIE_DŁUGOTRWAŁE = "leczenie długotrwałe"
        LEKARSTWO = "lekarstwo"
        OPERACJA = "operacja"


    tooth = models.ForeignKey(Tooth, on_delete = models.CASCADE)
    status = models.TextField(choices = Status.choices)
    depth = models.IntegerField()
    side = models.TextField(choices = Side.choices)
    front = models.TextField(choices = Frontor.choices)
    date_of_finding = models.DateTimeField(auto_now_add = True)
    healed = models.BooleanField(default=False)
    planned_healing = models.BooleanField(default = False)



def all_tooth_rentgen_images(instance, filename):
    return "%s/%s/%s" %(instance.tooth.patient, instance.tooth, filename)

class Tooth_rentgen(models.Model):
    tooth = models.ForeignKey(Tooth, on_delete= models.CASCADE)
    Image = models.ImageField(upload_to =all_tooth_rentgen_images, blank=True, null=True)






