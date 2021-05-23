from django.urls import path

from .views import ChooseWordBertView, ChooseWordGPTView


urlpatterns = [
    path('bert/', ChooseWordBertView.as_view(), name='choose_word_bert'),
    path('gpt/', ChooseWordGPTView.as_view(), name='choose_word_gpt'),
]
