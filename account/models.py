from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from mapbox_location_field.models import LocationField
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectField

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Użytkownik musi posiadać email")
        if not username:
            raise ValueError("Użytkownik musi posiadać login")

        user = self.model(
                email=self.normalize_email(email),
                username=username,
            )

        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, username, password=None):
        user = self.create_user(
                email=self.normalize_email(email),
                username=username,
                password=password,
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

def get_user_image_folder(instance, filename):
    return "%s/%s" %(instance.dentist.account.username, filename)

class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email', max_length=60, unique=True)
    username = models.CharField(verbose_name='Login',max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='data dołączenia', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='data ostatniego zalogowania', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_dentist = models.BooleanField(default=False)
    is_receptionist = models.BooleanField(default = False)
    profile_pic = models.ImageField(upload_to='profile_pic', default='default_profile.jpg')

    def clean(self):
        if self.is_dentist and self.is_receptionist:
            raise ValidationError('Nie możesz być na raz recepcjonistą i dentystą')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):             #uprawniena do admina
        return self.is_admin

    def has_module_perms(self, app_label):          # zawsze będzie miało uprawneinia modułó
        return True


class Dentist(models.Model):
    account = models.OneToOneField(
        Account,on_delete=models.CASCADE, limit_choices_to={'is_dentist': True},unique=True)
    First_Name = models.CharField(verbose_name='Imię',max_length=20, blank=False)
    Surname = models.CharField(verbose_name='nazwisko',max_length=30, blank=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Numer telefonu musi zawierać od 9-15 znaków i pierwszym znakiem może być +")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False) # validators should be a list
    city = models.CharField(verbose_name='Miejscowość',max_length=30,blank=False)
    clinic_adress =  models.CharField(verbose_name='Adres Kliniki',max_length=50,blank=False)
    about_me = models.TextField(max_length=1000, blank = True, null=True)
    def __str__(self):
        return "%s %s" %(self.First_Name, self.Surname)

class Receptionist(models.Model):
    account = models.OneToOneField(
        Account,on_delete=models.CASCADE, limit_choices_to={'is_receptionist': True})
    First_Name = models.CharField(verbose_name='Imię',max_length=20, blank=False)
    Surname = models.CharField(verbose_name='nazwisko',max_length=30, blank=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Numer telefonu musi zawierać od 9-15 znaków i pierwszym znakiem może być +")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False) # validators should be a list
    dentist = models.ManyToManyField(Dentist)    

    def __str__(self):
        return "%s %s" %(self.First_Name, self.Surname)



class Patient(models.Model):
    account = models.OneToOneField(
        Account,on_delete=models.SET_NULL, limit_choices_to={'is_dentist': False}, blank=True, unique=True, null=True)
    First_Name = models.CharField(verbose_name='Imię',max_length=20, blank=False)
    Surname = models.CharField(verbose_name='nazwisko',max_length=30, blank=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Numer telefonu musi zawierać od 9-15 znaków i pierwszym znakiem może być +")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False) # validators should be a list
    city = models.CharField(verbose_name='Miejscowość',max_length=30,blank=True)
    adress =  models.CharField(verbose_name='Adres zamieszkania',max_length=50,blank=True)
    email_conversation = models.EmailField(verbose_name='Skrzynka na emaile od dentysty', max_length=30, blank=True)
    dentist = models.ManyToManyField(Dentist)    
    age = models.IntegerField(verbose_name='wiek',validators=[MinValueValidator(1), MaxValueValidator(100)], default = 20)
    private = models.BooleanField(default= True)

    def __str__(self):
        return "%s %s" %(self.First_Name, self.Surname)

    def save(self, *args, **kwargs):
        if not self.account:
            self.account = None
        super().save(*args, **kwargs)


class Comment(models.Model):
    dentist = models.ForeignKey(Dentist, on_delete = models.CASCADE)
    account = models.ForeignKey(Account, on_delete = models.CASCADE)
    body = models.TextField("opis")
    created_on = models.DateTimeField(auto_now_add=True, verbose_name='stworzone')
    active = models.BooleanField(default=True, verbose_name='aktywne')


    class Meta:
        verbose_name='Komentarz'
        verbose_name_plural = 'Komentarze'
        ordering = ['created_on']

    def __str__(self):
        return 'komentarz o tytule {} zrobiony przez {}'.format(self.body, self.account.username)



class Images_aboutme(models.Model):
    dentist = models.ForeignKey(Dentist,on_delete= models.CASCADE)
    Image = models.ImageField(upload_to =get_user_image_folder)
    about = models.CharField(verbose_name='opis', max_length=30)
    def __str__(self):
        return self.about



class Location(models.Model):
    name = models.CharField(max_length= 50)
    dentist = models.ManyToManyField(Dentist)
    receptionist = models.ManyToManyField(Receptionist)
    about = models.TextField(blank = True, null = True)
    location = LocationField()


class Specialisation(models.Model):
    dentist = models.ForeignKey(Dentist, on_delete = models.CASCADE)
    Specialisation = models.CharField(max_length=50)

class Achievements(models.Model):
    class Significance(models.TextChoices):
        DUŻA = 1
        ŚREDNIA = 2
        MAŁA = 3
    dentist = models.ForeignKey(Dentist, on_delete = models.CASCADE)
    award = models.CharField(max_length=50)
    significance = models.TextField(choices = Significance.choices)





class Wiadomosc(models.Model):
    class Type_of(models.TextChoices):
        ZATWIERDZONE = "zatwierdzenie"
        ODWOŁANIE = "odwołanie"
        ZMIENIONA = "zmiana daty"
        USUNIĘTA = "usunięta"
        PRZYPOMNIENIE = "przypomnienie"
        CZAT = "czat"
        ZAPROSZENIE = "zaproszenie"
        OGÓLNE = "ogólne"



    date_of_change = models.DateTimeField()
    type_of = models.TextField(choices = Type_of.choices)
    czytano = models.BooleanField(default = False)
    desc = models.TextField()
    special_data = models.CharField(max_length=40, blank= True, null=True)
    target = models.ForeignKey(Account, on_delete=models.CASCADE)




class Invitation_to_location(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete = models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, verbose_name='wysłane o godzinie')


class WeekdayHoursOpen(models.Model):
    class open_days_choices(models.TextChoices):
        PONIEDZIAŁEK = 1
        WTOREK = 2
        ŚRODA = 3
        CZWARTEK = 4
        PIĄTEK = 5
        SOBOTA = 6
        NIEDZIELA = 7
    dentist = models.OneToOneField(Dentist, on_delete= models.CASCADE)
    start_hour = models.TimeField(verbose_name='godzina otwarcia')
    end_hour = models.TimeField(verbose_name='godzina zamknięcia')
    open_days = MultiSelectField(choices = open_days_choices.choices)

class Cennik(models.Model):
    dentist = models.OneToOneField(Dentist,on_delete=models.CASCADE)
    wizyta_kontrolna = models.IntegerField()
    wyrywanie = models.IntegerField()
    kanałowe = models.IntegerField()
    plomba = models.IntegerField()
    czyszczenie = models.IntegerField()
    leczenie_długotrwałe = models.IntegerField()
    lekarstwo = models.IntegerField()
    operacja = models.IntegerField()
    inne = models.IntegerField()



