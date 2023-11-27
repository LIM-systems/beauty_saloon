from django.urls import path
from inwork.views import *

urlpatterns = [
    path('sign_up/', SignUp.as_view()),
    path('sign_up/<int:tg_id>/', SignUp.as_view()),
]