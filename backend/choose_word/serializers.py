from rest_framework import serializers


class TestItemSerializer(serializers.Serializer):
    """Item of test to solve."""
    text_parts = serializers.ListField(child=serializers.CharField())
    candidates = serializers.ListField(child=serializers.ListField(
        child=serializers.CharField()
    ))
