from django.urls import path

from .views import ChooseWordBertView


handler500 = 'rest_framework.exceptions.server_error'
handler400 = 'rest_framework.exceptions.bad_request'

urlpatterns = [
    path('bert/', ChooseWordBertView.as_view()),
]
