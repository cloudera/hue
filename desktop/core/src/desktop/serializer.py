from rest_framework import serializers
from .models import LlmPrompt

class UnixEpochDateField(serializers.DateTimeField):
    def to_representation(self, value):
        return int(value.timestamp() * 1000)

class LlmPromptSerializer(serializers.ModelSerializer):
    updatedAt = UnixEpochDateField(source='updated_at', read_only=True)
    createdAt = UnixEpochDateField(source='created_at', read_only=True)

    class Meta:
        model = LlmPrompt
        fields = ('id','prompt','dialect','db','updatedAt', 'createdAt',)