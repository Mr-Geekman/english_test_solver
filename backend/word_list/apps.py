import os

from django.apps import AppConfig

from transformers import BertForMaskedLM, BertTokenizer

from english_test_solver.settings import BASE_DIR
from src.BertScorer import BertScorerCorrection


class WordListConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'word_list'
    BERT_PATH = os.path.join(BASE_DIR, 'models', 'BertBase')
    bert_scorer_correction = BertScorerCorrection(
        BertForMaskedLM.from_pretrained(BERT_PATH),
        BertTokenizer.from_pretrained(BERT_PATH)
    )
