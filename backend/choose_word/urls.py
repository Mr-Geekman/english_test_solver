from django.urls import path

from .views import ChooseWordBertView

urlpatterns = [
    path('bert/', ChooseWordBertView.as_view()),
]