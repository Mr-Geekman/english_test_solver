import numpy as np
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import TestItemSerializer
from .apps import WordListConfig


class SelectWordView(APIView):
    """Controller for running model."""

    def post(self, request):
        serializer = TestItemSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data

        # make scoring
        sentence = data['sentence']
        candidates = data['candidates']
        try:
            scores = WordListConfig.bert_scorer_correction(
                [sentence], [candidates]
            )[0]
            # normalize scores
            normalized_scores = np.exp(scores)
            normalized_scores = normalized_scores / np.sum(normalized_scores)
            # send predictions
            return Response(data=normalized_scores)
        except ValueError as e:
            raise ValidationError(str(e))
