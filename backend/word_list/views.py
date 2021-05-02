import numpy as np
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import TestItemSerializer

from transformers import BertForMaskedLM, BertTokenizer

from english_test_solver.settings import BERT_PATH
from src.BertScorer import BertScorerCorrection


class SelectWordView(APIView):
    """Controller for running model."""

    def post(self, request):
        serializer = TestItemSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data

        model = BertForMaskedLM.from_pretrained(BERT_PATH,)
        bert_tokenizer = BertTokenizer.from_pretrained(BERT_PATH)
        bert_scorer_correction = BertScorerCorrection(model, bert_tokenizer)

        # make scoring
        sentence = data['sentence']
        candidates = data['candidates']
        try:
            scores = bert_scorer_correction([sentence], [candidates])[0]
            # normalize scores
            normalized_scores = np.exp(scores)
            normalized_scores = normalized_scores / np.sum(normalized_scores)
            # send predictions
            return Response(data=normalized_scores)
        except ValueError as e:
            raise ValidationError(str(e))
