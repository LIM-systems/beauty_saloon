from django.urls import path

from inwork import views

urlpatterns = [
    path('allcategories', views.APIAllCategories.as_view()),
    path('select_services', views.APISelectServices.as_view()),
    path('select_masters', views.APISelectMasters.as_view()),
    path('get_master_schedule', views.APIGetMasterSchedule.as_view()),
    path('create_records', views.APICreateRecords.as_view()),
]
