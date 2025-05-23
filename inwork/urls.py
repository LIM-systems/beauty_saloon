from django.urls import path

from inwork import views

urlpatterns = [
    path('get_csrf_token', views.APICSRFToken.as_view()),
    path('get-categories', views.APIGetCategories.as_view()),
    path('get-services', views.APIGetServices.as_view()),
    path('get-masters', views.APIGetMasters.as_view()),
    path('get-master-schedule', views.APIGetMasterSchedule.as_view()),
    path('create-records', views.APICreateRecords.as_view()),
    path('in-admin', views.APIAdminCheck.as_view()),
    path('get_schedules', views.APIMonthMastersShedule.as_view()),
    path('new_schedules', views.APICreateSchedule.as_view()),
    path('get_masters_work_time', views.APIGetMasterWorkTime.as_view()),
    path('get_visits_info_all', views.APIGetDateEventsForAll.as_view()),
    path('get_visits_info_one', views.APIGetDateEventsForOne.as_view()),
    path('logging', views.APILogger.as_view()),
]
