from django.urls import path

from inwork import views

urlpatterns = [
    path('get_csrf_token', views.APICSRFToken.as_view()),
    path('get-categories', views.APIGetCategories.as_view()),
    path('select_services', views.APISelectServices.as_view()),
    path('select_masters', views.APISelectMasters.as_view()),
    path('get_master_schedule', views.APIGetMasterSchedule.as_view()),
    path('create_records', views.APICreateRecords.as_view()),
    path('get_schedules', views.APIMonthMastersShedule.as_view()),
    path('new_schedules', views.APICreateSchedule.as_view()),
    path('get_masters_work_time', views.APIGetMasterWorkTime.as_view()),
    path('get_visits_info_all', views.APIGetDateEventsForAll.as_view()),
    path('get_visits_info_one', views.APIGetDateEventsForOne.as_view()),
    path('logging', views.APILogger.as_view()),
]
