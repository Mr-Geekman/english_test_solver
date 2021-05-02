from rest_framework import serializers


class TestItemSerializer(serializers.Serializer):
    """Item of test to solve."""
    sentence_left = serializers.CharField()
    sentence_right = serializers.CharField()
    candidates = serializers.ListField(
        child=serializers.CharField()
    )
