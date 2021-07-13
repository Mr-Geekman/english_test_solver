import os

from django.apps import AppConfig

from transformers import (
    BertForMaskedLM, BertTokenizer, GPT2Tokenizer, GPT2LMHeadModel
)

from english_test_solver.settings import BASE_DIR
from src.BertScorer import BertScorerCorrection
from src.GPTScorer import GPTScorerSentence


class ChooseWordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'choose_word'

    bert_path = os.path.join(BASE_DIR, 'models', 'bert-base-uncased')
    bert_tokenizer = BertTokenizer.from_pretrained(bert_path)
    max_bert_size = 512
    max_bert_candidate = 128
    bert_scorer_correction = BertScorerCorrection(
        BertForMaskedLM.from_pretrained(bert_path),
        bert_tokenizer, max_length=max_bert_size
    )

    gpt_path = os.path.join(BASE_DIR, 'models', 'gpt2')
    gpt_tokenizer = GPT2Tokenizer.from_pretrained(gpt_path)
    max_gpt_size = 1024
    gpt_scorer_sentence = GPTScorerSentence(
        GPT2LMHeadModel.from_pretrained(gpt_path),
        gpt_tokenizer, max_length=max_gpt_size
    )

    benchmark_data_path = os.path.join(BASE_DIR, name, 'data', 'sdamgia.json')
