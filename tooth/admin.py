from django.contrib import admin
from tooth.models import Tooth, Tooth_destructions, Tooth_rentgen
from visit.models import tooth_healing_destruction

class Tooth_destructionsAdmin(admin.ModelAdmin):          # co ma być wyświetlone w panelu admina
    list_display = ('id','tooth','status','depth','side','front')


    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class View_tooth_healing_destructions_Admin(admin.ModelAdmin):          # co ma być wyświetlone w panelu admina
    list_display = ( 'id','tooth_destructions','type_of', 'about_healing', 'date_of_fixing', 'visit')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Tooth)
admin.site.register(Tooth_rentgen)

admin.site.register(Tooth_destructions, Tooth_destructionsAdmin)
admin.site.register(tooth_healing_destruction, View_tooth_healing_destructions_Admin)

# Register your models here.
