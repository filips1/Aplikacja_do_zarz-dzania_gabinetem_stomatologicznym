from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import *
from mapbox_location_field.admin import MapAdmin

admin.site.register(Location, MapAdmin)
# Register your models here.


class AccountAdmin(UserAdmin):          # co ma być wyświetlone w panelu admina
    list_display = ('id', 'username','email', 'date_joined', 'last_login', 'is_admin', 'is_dentist')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class PatientAdmin(admin.ModelAdmin):          # co ma być wyświetlone w panelu admina
    list_display = ('id','account','First_Name')


    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Comment)
admin.site.register(Specialisation)
admin.site.register(Achievements)
admin.site.register(Account, AccountAdmin)
admin.site.register(Dentist)
admin.site.register(Receptionist)
admin.site.register(Images_aboutme)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Wiadomosc)
admin.site.register(WeekdayHoursOpen)
admin.site.register(Cennik)

