from django.urls import path

from .views import ChooseWordBertView


urlpatterns = [
    path('bert/', ChooseWordBertView.as_view()),
]

handler500 = 'rest_framework.exceptions.server_error'
handler400 = 'rest_framework.exceptions.bad_request'
