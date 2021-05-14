import os

from django.apps import AppConfig

from transformers import BertForMaskedLM, BertTokenizer

from english_test_solver.settings import BASE_DIR
from src.BertScorer import BertScorerCorrection


class ChooseWordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'choose_word'
    bert_path = os.path.join(BASE_DIR, 'models', 'BertBase')
    tokenizer = BertTokenizer.from_pretrained(bert_path)
    max_bert_size = 512
    max_bert_candidate = 128
    bert_scorer_correction = BertScorerCorrection(
        BertForMaskedLM.from_pretrained(bert_path),
        tokenizer, max_length=max_bert_size
    )
