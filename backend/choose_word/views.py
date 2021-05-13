from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import TestItemSerializer
from .utils import process_text_bert


class ChooseWordBertView(APIView):
    """Controller for running model."""

    parser_classes = [JSONParser]

    def post(self, request):
        serializer = TestItemSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data

        text_parts = data['text_parts']
        candidates = data['candidates']
        try:
            results = process_text_bert(text_parts, candidates)
        except ValueError as e:
            raise ValidationError(str(e))
        return Response(data=results)
