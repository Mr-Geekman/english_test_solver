from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TestItemSerializer
from .utils import process_text_bert


class ChooseWordBertView(APIView):
    """Controller for running model."""

    handler500 = 'rest_framework.exceptions.server_error'
    handler400 = 'rest_framework.exceptions.bad_request'
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = TestItemSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data

        text_parts = data['text_parts']
        candidates = data['candidates']
        results = process_text_bert(text_parts, candidates)

        return Response(data=results)
