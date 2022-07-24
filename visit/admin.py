from django.contrib import admin
from visit.models import Visit
# Register your models here.

class ViewstAdmin(admin.ModelAdmin):          # co ma być wyświetlone w panelu admina
    list_display = ( 'id','Dentist','Patient', 'status', 'Type_of', 'day_of_visit', 'time_of_the_visit', 'time_end_visit')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()



admin.site.register(Visit, ViewstAdmin)

