from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from tooth.views import *
from django.conf.urls.static import static 
from visit.views import *
from django.conf import settings
from django.conf.urls import include, url
from account.views import *
from tooth.views import *
from chat.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home_view, name='app'),
    path('register/', registration_view, name="register"),
    path('regmoinfo/',more_info_view, name="registermore"),
    path('regmoinfo/receptionist',more_reg_receptionist_view, name="registermore_receptionist"),


    path('choose_dentist/', choose_dentist_ciew, name='choose_dentist'),
    path('choose_dentist/only/<type>', choose_dentist_ciew, name='choose_dentist_only_mine'),
    path('choose_dentist/update', update_all_dentist_view, name='update_all_dentist'),
    path('choose_dentist/receptionist/join/<dentist_id>', join_as_receptionist_view, name='join_as_receptionist'),

    path('patients/only/<type>/',patients_view, name='patients_only'), 
    path('patients/only/receptionist/<dentist_id>/<type>/',patients_view, name='patients_only_receptionist_dentist'), 
    path('patients/only/receptionist/<dentist_id>/',patients_view, name='patients_only_receptionist_dentist'), 

    path("chat_list", chat_view_information, name="chat_info"),



    url(r'^patients/$', patients_view, name = 'patients'),
    path('patients/update',update_patient_list_view, name = "update_patient_list"),
    path('patients/update/<dentist_id>',update_patient_list_view, name = "update_patient_list"),
    url(r'^patients/create/$',create_new_patient_view, name='create_new_patient'),
    path('patients/create/<dentist_id>/',create_new_patient_view, name='create_new_patient_oth'),
    path('patients/<id>/update', update_patient_view, name='patient_update'),
    path('patients/<id>/update/<dentist_id>', update_patient_view, name='patient_update'),
    path('patients/<id>/delete/', delete_patient_view, name='patient_delete'),
    path('patients/<id>/delete/<dentist_id>', delete_patient_view, name='patient_delete'),
    path('patients/<id>/inv_or_rem/<dentist_id>', patient_invite_remove_view, name='patient_invite_remove'),
    path('patients/<id>/inv_or_rem/', patient_invite_remove_view, name='patient_invite_remove'),
    url(r'^dentist/(?P<dentist_id>\d+)/change_stat/$', dentist_change_stat_view, name='dentist_change_stat'),
    path('visit/create/', new_visit_view, name='new_visit'),
    path('visit/create/receptionist/<dentist_id>', new_visit_receptionist_view, name='new_visit_receptionist'),
    path('visit/create/receptionist/<dentist_id>/<patient_id>', new_visit_receptionist_view, name='new_visit_receptionist'),
    path('visit/create/<id>', new_visit_view, name='new_visit'),
    path('visit/<id>/create_dentist_chosen/', new_visit_dentist_chosen_view, name='new_visit_heh'),
    path('visit/new_by_patient',new_visit_by_patient_view, name = "new_by_patient"),
    path('visit/delete/<visit_id>',VisitDeleteView, name = "visit_delete"),
    path('visit/cancel/<visit_id>',VisitCancelView, name = "visit_cancel"),
    path('visit/revive/<visit_id>',VisitReviveView, name = "visit_revive"),
    path('visit/date_change/<visit_id>',VisitDateChangeView, name = "visit_date_change"),

    path('tooth/update_visit/<th_id>', ToothUpdateDestructionsStatusView, name = "tooth_update_destructions_status"),
    path('tooth/infos_about/<tooth_id>', ToothInfo, name = "tooth_info"),




    path('dentist/profile/<dentist_id>', dentist_profile_view, name = 'dentist_profile'),
    path('dentist/profile', dentist_profile_view, name = 'dentist_profile'),
    path('dentist/profile/add_about_me/', add_about_me_view, name = 'add_about_me'),
    path('dentist/profile/add_achievements/', add_achievements_view, name = 'add_achievements'),
    path('dentist/profile/edit_achievements/<achievement_id>', edit_achievements_view, name = 'edit_achievements'),
    path('dentist/profile/delete_achievement/<achievement_id>', delete_achievement_view, name = 'delete_achievement'),
    path('dentist/profile/update_achievements_shown/', update_achievements_shown_view, name = 'update_achievements_shown'),
    path('dentist/profile/add_specialisation/', add_specialisation_view, name = 'add_specialisation'),
    path('dentist/profile/edit_specialisation/<specialisation_id>', edit_specialisation_view, name = 'edit_specialisation'),
    path('dentist/profile/delete_specialisation/<specialisation_id>', delete_specialisation_view, name = 'delete_specialisation'),
    path('dentist/profile/update_specialisation_shown/', update_specialisation_shown_view, name = 'update_specialisation_shown'),
    path('dentist/profile/delete_image/<image_id>', delete_image_view, name = 'delete_image'),
    path('dentist/profile/update_about_me/', update_about_me_view, name = 'update_about_me'),
    path('location_add',location_add_view, name = 'location_add'),
    path('location_add/<location_id>',location_add_view, name = 'location_add'),
    path('dentist/comment/add/<dentist_id>', add_comment_view, name = 'add_comment'),
    path('dentist/comment/edit/<comment_id>', edit_comment_view, name = 'edit_comment'),
    path('dentist/comment/delete/<comment_id>', delete_comment_view, name = 'delete_comment'),
    path('dentist/comment/hide/<comment_id>', hide_comment_view, name = 'hide_comment'),
    path('dentist/comment/update_list/<dentist_id>', update_comment_shown_view, name = 'update_comment_shown'),
    path('dentist/locations', all_den_loc_view, name = 'locations'),
    path('location/ask/<location_id>', all_den_loc_view, name = 'locations_ask'),

    path('calendar/', CalendarView.as_view(), name='calendar'), 
    path('calendar/<dentist_id>', CalendarView.as_view(), name='calendar'), 
    path('visit/editing/<visit_id>/', VisitEditNew, name='visit_edit_new'),
    path('visit/approve/<visit_id>/<dentist_id>', VisitApprove, name='visit_approve'),
    path('visit/approve/<visit_id>/', VisitApprove, name='visit_approve'),
    path('visit/reject/<visit_id>/', VisitReject, name='visit_reject'),
    path('visit/reject/<visit_id>/<dentist_id>', VisitReject, name='visit_reject'),
    path('visit/unaproved',VisitUnaprovedShowView, name = 'unaproved'),
    path('visit/unaproved/<dentist_id>',VisitUnaprovedShowView, name = 'unaproved'),
    path('visit/info',InfoView, name = 'info'),
    path('visit/info/<info_id>',InfoSeenView, name = 'info_seen'),
    path('visit/info/delete/<info_id>',InfoDeleteView, name = 'info_delete'),
    path('visit/possible_hours/<dates>/<dentist_id>/<length>',get_possible_hours, name = 'get_possible_hours'),
    path('visit/update_fin_hour/<times>/<length>',update_fin_hour, name = 'update_fin_hour'),
    path('visit/safe_days/<year>/<month>/<dentist_id>/<length>/<typesy>',safe_days, name = 'safe_days'),
    path('visit/visit_length_change_update/<dentist_id>/<length>',visit_length_change_update, name = 'visit_length_change_update'),


    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('account/', account_view, name="account"),
    path('must_authenticate/',must_authenticate_view, name="must_authenticate"),
    path('must_finish_registration/',must_fully_register_view, name="must_finish_registration"),

    path('tooth/check_visit_tooth/<visit_id>',CheckToothStatusView, name = "check_tooth_status" ),
    path('tooth/check_updated_visit_tooth/<tooth_id>/<visit_id>',CheckUpdatedStatusView, name = "check_updated_tooth_status" ),
    path('tooth/check_updated_visit_tooth_img/<tooth_id>/<visit_id>',CheckUpdatedStatusImgView, name = "check_updated_tooth_img_status" ),
    path('tooth/remove_td_from_visit/<th_id>',ClearHealingView, name = "clear_healing" ),
    path('tooth/remove_td_from_visit_ni/<td_id>/<visit_id>',ClearHealingNiView, name = "clear_healingni" ),
    path('tooth/edit_visit_td/<td_id>/<visit_id>',EditVisitToothDestructionsView, name = "edit_visit_td" ),
    path('tooth/edit_td/<td_id>',EditToothDestructionsView, name = "edit_td" ),
    path('tooth/new_visit_td/<tooth_id>/<visit_id>',NewVisitToothDestructionView, name = "new_visit_td" ),
    path('tooth/check_all_td/<tooth_id>/<visit_id>',CheckAllDesStatusView, name = "check_all_td" ),
    path('tooth/check_all_td/<tooth_id>/',CheckAllTotthDesStatusView, name = "check_all_tooth_td" ),
    path('tooth/add_td_to_visit/<td_id>/<visit_id>',AddTotthDestructiontoVisitView, name = "add_td_to_visit" ),
    path('tooth/proposition_of_healing/<td_id>/<visit_id>',PropositionOfHealinTypeView, name = "proposition_of_healing" ),
    path('tooth/update_healing_type/<td_id>/<type_of>/<visit_id>',UpdateHealingTypeView, name = "update_healing_type" ),
    path('tooth/add_all_td_to_visit/<tooth_id>/<visit_id>',AddAllTotthDestructiontoVisitView, name = "add_all_td_to_visit" ),
    path('tooth/add_all_nh_td_to_visit/<tooth_id>/<visit_id>',AddAlNotHealedTotthDestructiontoVisitView, name = "add_all_nh_td_to_visit" ),
    path('tooth/add_all_nh_np_td_to_visit/<tooth_id>/<visit_id>',AddAlNotHealedandNotPlannedHealingTotthDestructiontoVisitView, name = "add_all_nh_np_td_to_visit" ),
    path('tooth/add_all_td_to_visit/<visit_id>',AddAllVisitToothAllTotthDestructiontoVisitView, name = "add_all_visit_tooth_all_td_to_visit" ),
    path('tooth/add_all_nh_td_to_visit/<visit_id>',AddAllVisitToothNotHealedAllTotthDestructiontoVisitView, name = "add_all_visit_tooth_all_nh_td_to_visit" ),
    path('tooth/add_all_nh_np_td_to_visit/<visit_id>',AddAllVisitToothNotHealedAndNotPlannedHealingAllTotthDestructiontoVisitView, name = "add_all_visit_tooth_all_nh_np_td_to_visit" ),
    path('tooth/healing_history/<td_id>',HealingHistoryView, name = "healing_history" ),
    path('tooth/heal_or_destroyed/<td_id>',SetAsHealedOrDestroyedView, name = "heal_or_destroyed" ),
    path('tooth/heal_tooth/<td_id>',HealDestructionView, name = 'add_healing' ),
    path('tooth/edit_heal_tooth/<th_id>',HealDestructionEditView, name = 'edit_healing' ),
    path('tooth/remove_healing/<th_id>',HealDestructionRemoveView, name = 'remove_healing' ),
    path('tooth/update_data/<tooth_id>',UpdataDataView, name = 'update_data' ),
    path('tooth/change_active/<tooth_id>',ChangeToothActive, name = 'change_active' ),
    path('tooth/return_mleczny/<tooth_id>',ReturnMlecznyTooth, name = 'return_mleczny' ),
    path('tooth/new_td/<tooth_id>',AddToothDestruction, name = 'new_td' ),
    path('tooth/delete_tooth/<tooth_id>',DeleteTooth, name = 'delete_tooth' ), 
    path('tooth/delete_td/<td_id>',DeleteToothDestructions, name = 'delete_td' ), 
    path('tooth/add_rentgen/<tooth_id>',add_rentgen_view, name = 'add_rentgen' ), 
    path('tooth/delete_rentgen/<ren_id>',DeleteRentgenView, name = 'delete_rentgen' ), 
    path('tooth/add_rentgen/',add_rentgen_view, name = 'add_rentgen' ), 

    path('tooth/<patient_id>/',ToothView, name = 'tooth_all_view'),
    path('tooth/show/<tooth_id>/',ToothAbout, name = 'tooth_about'),
    path('tooth_healed/<side>/<tooth_id>',tooth_all_heal_view, name = 'tooth_all_heal'),
    path('tooth_side_destructions/<side>/<tooth_id>',tooth_side_destructions, name = 'tooth_side_destructions'),
    path('visit/add_tooth/<visit_id>', AddToothToVisitView, name = 'add_tooth_to_visit'),
    path('visit/add_chosen_tooth/<tooth_id>/<visit_id>', AddChosenToothToVisitView, name = 'add_chosen_tooth'),
    path('visit/remove_tooth_from_visit/<tooth_id>/<visit_id>', RemoveToothFromVisitView, name = 'remove_tooth_from_visit'),
    path('visit/add_cost/<visit_id>', AddVisitCost, name = 'add_visit_cost'),
    path('clinic/location/info/<location_id>',clinic_location_info_view, name = 'clinic_location_info'),
    path('clinic/location/ask/join/<location_id>',location_ask_for_invite, name = 'location_ask_for_invite'),
    path('clinic/location/resign/<location_id>',location_resign_view, name = 'location_resign'),
    path('clinic/location/invite/approve/<invitation_id>',location_approve_view, name = 'location_approve'),
    path('clinic/location/invite/reject/<invitation_id>',location_reject_view, name = 'location_reject'),
    path("chat/<username>", ThreadView.as_view(), name = "chat"),
    path("chat_reload/<dentist_id",chat_reload,name="chat_reload"),






]
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
