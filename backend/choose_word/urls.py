from django.urls import path

from .views import ChooseWordBertView, ChooseWordGPTView, BenchmarkView


urlpatterns = [
    path('bert/', ChooseWordBertView.as_view(), name='choose_word_bert'),
    path('gpt/', ChooseWordGPTView.as_view(), name='choose_word_gpt'),
    path('benchmark/', BenchmarkView.as_view(), name='choose_word_benchmark')
]
