from django.urls import path

from .views import SelectWordView

urlpatterns = [
    path('', SelectWordView.as_view()),
]
