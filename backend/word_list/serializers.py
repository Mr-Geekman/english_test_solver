from rest_framework import serializers


class TestItemSerializer(serializers.Serializer):
    """Item of test to solve."""
    sentence = serializers.CharField()
    candidates = serializers.ListField(
        child=serializers.CharField()
    )
