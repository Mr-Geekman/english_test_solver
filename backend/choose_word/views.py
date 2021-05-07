import numpy as np
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TestItemSerializer
from .apps import ChooseWordConfig


class ChooseWordBertView(APIView):
    """Controller for running model."""

    parser_classes = [JSONParser]

    def post(self, request):
        serializer = TestItemSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data

        # make scoring
        sentence_left = data['sentence_left']
        sentence_right = data['sentence_right']
        mask_token = ChooseWordConfig.tokenizer.mask_token
        sentence = f'{sentence_left} {mask_token} {sentence_right}'
        candidates = data['candidates']
        scores = ChooseWordConfig.bert_scorer_correction(
            [sentence], [candidates]
        )[0]
        # normalize scores
        normalized_scores = np.exp([np.mean(x) for x in scores])
        normalized_scores = normalized_scores / np.sum(normalized_scores)
        # send predictions
        return Response(data=normalized_scores)
